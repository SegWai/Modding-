"""Build and independently verify the two small, uncompressed test PBOs.
Run with Python 3 from any working directory. Not needed to launch the supplied ZIP.
"""
from pathlib import Path
import hashlib,json,struct,subprocess,re,sys,zipfile
ROOT=Path(__file__).resolve().parent

def read_pbo(data):
 position=0
 def string():
  nonlocal position
  stop=data.index(b'\0',position);value=data[position:stop].decode('ascii');position=stop+1;return value
 assert string()==''
 assert struct.unpack_from('<5I',data,position)==(0x56657273,0,0,0,0);position+=20
 assert string()=='prefix';prefix=string();assert string()==''
 rows=[]
 while True:
  name=string();method,original,reserved,stamp,size=struct.unpack_from('<5I',data,position);position+=20
  assert (method,original,reserved,stamp)==(0,0,0,0)
  if not name:assert size==0;break
  rows.append((name,size))
 result={}
 for name,size in rows:
  assert name not in result;result[name]=data[position:position+size];assert len(result[name])==size;position+=size
 assert data[position:position+1]==b'\0'
 assert data[position+1:]==hashlib.sha1(data[:position]).digest()
 return prefix,result

def build(source,prefix,target):
 entries={p.relative_to(source).as_posix().replace('/','\\'):p.read_bytes() for p in source.rglob('*') if p.is_file()}
 # Never expose the modified fragment at the vanilla shared resource path.
 if source.name == 'WorkspaceSource':
  entries['MLADSLeanLocomotion_v173.agf'] = entries.pop('locomotion.agf')
  root_graph = entries['player_main.agr'].decode()
  assert 'MLADSLeanLocomotion_v173.agf' in root_graph
  assert '/Locomotion.agf' not in root_graph

 assert entries and 'config.cpp' in entries
 header=b'\0'+struct.pack('<5I',0x56657273,0,0,0,0)+b'prefix\0'+prefix.encode()+b'\0\0'
 for name,payload in sorted(entries.items()):header+=name.encode('ascii')+b'\0'+struct.pack('<5I',0,0,0,0,len(payload))
 body=header+b'\0'+struct.pack('<5I',0,0,0,0,0)+b''.join(v for _,v in sorted(entries.items()))
 data=body+b'\0'+hashlib.sha1(body).digest()
 parsed_prefix,parsed=read_pbo(data);assert parsed_prefix==prefix and parsed==entries
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 return hashlib.sha256(data).hexdigest()

def validate_graph():
 g=(ROOT/'WorkspaceSource/locomotion.agf').read_text();agr=(ROOT/'WorkspaceSource/player_main.agr').read_text()
 # Every custom graph identifier must exist in the packed control template.
 declared=set(re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr))
 expressions=re.findall(r'(?m)^\s*(?:Expression|Condition|StartCondition|InterruptExpr|BlendWeight|Weight\w+|Weapon\w+|Value[XY]) "(.*)"',g)
 referenced=set(re.findall(r'\bMLADSLean\w+\b',' '.join(expressions)))
 assert referenced <= declared, 'Undeclared graph controls: '+str(referenced-declared)
 for arg in re.findall(r'HasVariableChanged\(\s*([^,)\n]+)',g):
  assert re.fullmatch(r'[A-Za-z_]\w*',arg.strip()) and arg.strip() in declared, 'HasVariableChanged requires a variable: '+arg
 for name in ['MLADSLeanGate','MLADSLeanCanary','MLADSLeanAmount']:
  assert agr.count('AnimSrcGCTVarFloat '+name+' ')==1
  body=re.search(r'AnimSrcGCTVarFloat '+name+r'\s*\{([^{}]*)\}',agr)[1]
  lines=[line.strip() for line in body.splitlines() if line.strip()]
  assert len(lines)==3 and all(re.fullmatch(r'(DefaultValue|MinValue|MaxValue) -?[0-9.]+',line) for line in lines)
 coverage=json.loads((ROOT/'Mode-Coverage.json').read_text())
 assert set(coverage)=={'StandIdle','StandWalk','CrouchIdle','CrouchWalk'}
 for mode,entry in coverage.items():
  for suffix in ['Left','Right']:
   name=entry['native_chain']+suffix
   expression=re.search(r'AnimSrcNodeProcTransform '+name+r'\s*\{.*?Expression "([^"]+)"',g,re.S)[1]
   assert '*(1.0-MLADSLeanGate)' in expression
  if mode!='StandIdle':assert not any(any(x in n for x in ['Leg','Foot','Toe','HipExtra']) for n in entry['bones'])
  if mode.startswith('Crouch'):assert 'Pelvis' not in entry['bones']
 assert g.count('WeaponRoll "(8.0*clamp(MLADSLeanAmount,-1.0,0.0)+(8.0-7.0*') == 24
 walk_revision=json.loads((ROOT/'Walk-Posture-v21.json').read_text())
 assert walk_revision['right_moving_head_lift_metres']==0.006
 assert all(item['new_pelvis_drop_metres']==-0.06 for item in walk_revision['walking_standing_pelvis'])
 assert g.count('AnimSrcNodeProcTransform ML21_RightMovingHeadLift {')==1
 shoulder=json.loads((ROOT/'Weapon-Shoulder-v24.json').read_text())
 assert shoulder['offset_metres']==0.08
 assert 'ML24_MarkedShoulderOffset' not in g
 assert 'ML29_FinalRightChestHold' not in g
 assert g.count('AnimSrcNodeProcTransform ML32_ReferenceHold_') == 21
 assert g.count('outputweaponoffsettobuffer = true') == 19
 assert g.count('AnimSrcNodeWeaponIk ML50_PublishBalancedWeapon {') == 1
 assert g.count('AnimSrcNodeWeaponIk ML48_PublishStandingLeftWeapon {') == 1
 assert g.count('AnimSrcNodeWeaponIk ML45_PublishStandingRightWeapon {') == 1
 assert g.count('AnimSrcNodeWeaponIk ML33_FinalGripIK {') == 1
 assert 'AnimSrcGCTVarFloat MLADSLeanWeaponShift {' in agr
 assert '*MLADSLeanWeaponShift' in g
 assert '*TestFloat' not in g
 upright=json.loads((ROOT/'Walk-Upright-v23.json').read_text())
 assert upright['torso_roll_scale']==0.4 and upright['native_forward_pitch_rotation_remaining_fraction']==0.25
 assert g.count('AnimSrcNodeProcTransform ML23_WalkForwardPitchRelief {')==1
 reference_head=json.loads((ROOT/'Reference-Head-v22.json').read_text())
 assert reference_head['graph_values']['right_moving_head_lift_metres']==0.026
 exposure=json.loads((ROOT/'Head-Exposure-v20.json').read_text())
 assert exposure['model_translation_metres']==[-0.025,0.01,0]
 assert g.count('AnimSrcNodeProcTransform ML20_RightLeanHeadExposure {')==1
 right_head=json.loads((ROOT/'Head-Direction-v17.json').read_text())
 assert len(right_head['changed_nodes'])==4
 head_direction=json.loads((ROOT/'Head-Direction-v16.json').read_text())
 assert len(head_direction['changed_nodes'])==4
 for change in head_direction['changed_nodes']:
  assert change['new_graph_amount'] == -change['old_graph_amount']
 revision=json.loads((ROOT/'Pose-Revision-v14.json').read_text())
 assert revision['head']['pitch_forward_degrees']==5 and revision['head']['extra_counter_roll_degrees']==0
 assert g.count('AnimSrcNodeProcTransform ML15_HeadForwardNod {')==1
 assert 'ML14_HeadCounterRoll' not in g
 assert '*(1.0-MLADSLeanMoveBlend)' in g
 spec=json.loads((ROOT/'Pose-Spec.json').read_text());assert max(spec['math_reconstruction_error'].values())<1e-5
 symmetry=json.loads((ROOT/'Symmetry-Measurements.json').read_text())
 assert max(v['symmetry_error_m'] for v in symmetry['authoring_model_offsets'].values())<1e-5
 return {'pose_math_reconstruction_max_error':spec['math_reconstruction_error'],'corrected_bones_per_direction':{k:len(v) for k,v in spec['corrections'].items()},'mode_coverage':coverage,'authoring_symmetry_max_error_m':max(v['symmetry_error_m'] for v in symmetry['authoring_model_offsets'].values()),'shared_weapon_roll_target':'right stationary standing +1-degree full-lean roll target; other +8/-8 targets retained; native visible alignment pending','npc':'one stationary NPC; alternating one-second lean sides after graph warmup; no patrol, mimic or respawn','native_compilation_and_playback':'V173 NOT RUN: requires user Windows DayZDiag. Native exposure balance, weapon roll, gait, crouch and NPC behavior remain pending.'}

def main():
 world_sources=list((ROOT/'LogicSource/Scripts/4_World').glob('*.c'))
 layers=sum(len(re.findall(r'\bmodded class PlayerBase\b',p.read_text())) for p in world_sources)
 assert layers==1, 'Lean/range callbacks must share one PlayerBase patch'
 player=(ROOT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
 assert 'protected float m_ML136Cycle;' in player and 'm_ML114Mimic' not in player
 checks=validate_graph()
 hashes={}
 for src,prefix,path in [('LogicSource','MLADSLeanLogic','@MLADSLeanLogic/Addons/MLADSLeanLogic.pbo'),('WorkspaceSource','DZ\\anims\\workspaces\\player\\player_main','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo')]:hashes[path]=build(ROOT/src,prefix,ROOT/path)
 checks.update({'pbo_sha256':hashes,'pbo_headers_prefix_offsets_source_and_sha1':'passed: independently parsed and compared to every input file','official_script_revision':'e8204c69fcfd056ea29a9728990fd9f7941ce8a6','script_API_review':'Native movement overrides, weapon SetADS, graph writes and lifecycle methods checked against official 1.30 scripts; native compilation pending','changed_native_files':['locomotion.agf','player_main.agr'],'source_directory':'F:/DayZProjects','revision':'v173 isolated walking-in-place NPC with F6/F7 left/right weapon, arms, head and body editing; separate combined MLWalkingLeanPreset save; approved stationary preset unchanged; native compilation and preview pending','dependencies':'Native DayZ firearms only: AK74, SKS, Glock19; no external weapon mods or Community Framework required.'})
 (ROOT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
 print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
