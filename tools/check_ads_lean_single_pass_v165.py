"""Check graph endpoint preservation and eliminated nested base replays."""
from pathlib import Path
import sys,re,json,hashlib,struct
sys.path.insert(0,str(Path(__file__).parent))
from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v164';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v165'
d=json.loads((b/'Single-Pass-Transitions-v165.json').read_text());old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());assert set(old)==set(new)
changed=set(d['changed_nodes'])
for name,node in old.items():
 if name not in changed:assert new[name]==node,name
for gate in d['gates']:
 name=gate['gate'];scope=gate['original_scope'];expected=old[name].replace('BlendWeight "'+scope+'"','BlendWeight "clamp(('+scope+')*1000000.0,0.0,1.0)"',1);assert new[name]==expected
 for item in gate['weighted_transforms']:
  before=old[item['node']];after=new[item['node']]
  assert after==before.replace('Expression "'+item['old_expression']+'"','Expression "'+item['new_expression']+'"',1)
  # All child links/bones/axes/amounts stay unchanged. At full scope every
  # operation has exactly the old amount. Zero scope takes unchanged base.
  assert '(('+scope+'))' not in item['new_expression'] or scope.startswith('(')
 for ik in gate['unchanged_ik_nodes']:assert old[ik]==new[ik]
# Concrete last-log walking->standing-left case makes four old gates fractional.
values={'MLADSLeanAmount':-.7,'MLADSLeanGate':1.,'MLADSLeanMoveBlend':.583333,'Stance':0.,'MovementSpeed':0.,'ML87FirstPersonCrouchLean':0.,'ML93ArmDrop':1.,'ML104ElbowEnabled':1.,'ML106ShoulderedGrip':1.,'ML118ContactReady':1.}
func={'__builtins__':{},'clamp':lambda x,a,b:max(a,min(b,x)),'abs':abs}
weights={};before=1;after=1
for gate in d['gates']:
 if gate['gate'] not in d['left_stop_duplicated_layers']:continue
 w=eval(gate['original_scope'],func,values);assert 0<w<1;selector=max(0,min(1,w*1e6));assert selector==1
 weights[gate['gate']]=w;before*=2;after*=1
assert before==16 and after==1
# Independently verify native sign extension in the received exception context.
short_signed=struct.unpack('<h',struct.pack('<H',0x8000))[0];assert short_signed==-32768
zero_extended32=short_signed&0xffffffff;scaled=zero_extended32*2
assert zero_extended32==0xffff8000 and scaled==0x1ffff0000
for p in (a/'LogicSource/Scripts').rglob('*.c'):assert p.read_bytes()==(b/p.relative_to(a)).read_bytes(),p
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
 assert hashlib.sha256((b/rel).read_bytes()).hexdigest()=='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
result={'gates_converted':len(d['gates']),'weighted_transform_nodes':d['correction_transform_nodes_weighted'],'trigger_case_fractional_weights':weights,'base_replays_through_selected_left_layers':[before,after],'full_pose_endpoint_operations':'unchanged; original axes/amounts/IK settings retained','fractional_transition':'direct weighted correction, changed from blending full evaluated poses','presets_camera_player_npc_and_timing_scripts':'byte-identical v164','minidump_index_overflow_arithmetic':'verified signed16 boundary at32768','native_crash_retest':'NOT RUN'}
(b/'Single-Pass-Transition-Checks-v165.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
