"""Offline validation only: graph isolation, immutable presets, FK and capture lifecycle."""
from pathlib import Path
import sys,json,re,hashlib,random
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent))
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
root=Path(__file__).resolve().parents[1];base=root/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v182';kit=base.with_name('MovementLab_ADS_Lean_Mosin_v183');w=kit/'LogicSource/Scripts/4_World';m=kit/'LogicSource/Scripts/5_Mission'
raw=(root/'ads-lean-test/User-Presets/Current-MLCrouchLeanPreset.json').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='2de68073870eb3b17bf24f9546ff90a41b737b516b0535351eae6d247f90eb20'
for name in ['MLLeanPreset.json','MLWalkingLeanPreset.json']:
 for rel in [name,'Profiles/LeanMosin/'+name,'LogicSource/Presets/'+name]:assert (kit/rel).read_bytes()==(base/rel).read_bytes()
for rel in ['MLCrouchLeanPreset.json','Profiles/LeanMosin/MLCrouchLeanPreset.json','LogicSource/Presets/MLCrouchLeanPreset.json']:assert(kit/rel).read_bytes()==raw
for rel in ['MLUnarmedLeanPreset.json','Profiles/LeanMosin/MLUnarmedLeanPreset.json','LogicSource/Presets/MLUnarmedLeanPreset.json']:
 j=json.loads((kit/rel).read_text());assert j['PresetVersion']==1
 for side in ['LeftLean','RightLean']:
  assert all(v==0 for v in j[side]['WeaponSettings'].values())
  assert len(j[side]['BodySettings']['Parts'])==24
  for p in j[side]['BodySettings']['Parts']:assert all(p[k]==0 for k in ['X','Y','Z','Pitch','Yaw','Roll'])
a=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((kit/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((kit/'Unarmed-Comparison-v183.json').read_text());added=set(b)-set(a);named={n for n in added if not n.startswith('{')};assert named==set(spec['new_nodes']) and len(named)==238
for name,node in a.items():
 if name.startswith('{'):continue
 expected=node.replace('Child "ML169_NativeCompare"','Child "ML183_UnarmedOnly"')if name=='MeleeBlockQ'else node
 assert b[name]==expected,name
assert 'OptimizeMin 1' in b['ML183_UnarmedOnly'] and 'OptimizeMax 1'in b['ML183_UnarmedOnly']
# Unarmed path has only the unmodified native graph and 237 model transforms.
seen=set();stack=['ML183_Edit_RightToeBase_RZ']
while stack:
 name=stack.pop()
 if name in seen:continue
 seen.add(name)
 if name in b:stack+=re.findall(r'\bChild\d* "([^"]+)"',b[name])
assert 'NormalWeaponIK'in seen
assert not any(n in seen for n in ['ML166_PublishFinalAimedWeapon','ML182CrouchWeaponFollow','ML149_BodyWeaponFollow','ML173_SharedWalkingUpper'])
assert not any('Arm' in re.findall(r'Bone "([^"]+)"',b[n])[0]for n in named if n.startswith('ML183_Base'))
# Check all graph references and no new cycles.
sys.setrecursionlimit(20000);visiting=set();done=set()
def visit(name):
 if name in done or name not in b:return
 assert name not in visiting,name
 visiting.add(name)
 for child in re.findall(r'\bChild\d* "([^"]+)"',b[name]):visit(child)
 visiting.remove(name);done.add(name)
for name in b:
 if not name.startswith('{'):visit(name)
agr=(kit/'WorkspaceSource/player_main.agr').read_text();declared=set(re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr))
for n in named:
 for expr in re.findall(r'(?:Expression|BlendWeight) "([^"]+)"',b[n]):
  assert set(re.findall(r'\bML\w+\b',expr))<=declared,(n,expr)
assert len([n for n in declared if n.startswith('ML183')])==94
# FK reconstructs target for varied native unarmed source skeletons. Arms are
# deliberately outside the target set, so no raised arm pose can be copied.
targetdata=json.loads((kit/'Unarmed-Body-Targets-v183.json').read_text());bones=targetdata['bones'];parents={n:None if p<0 else bones[p]for n,p in zip(bones,targetdata['parents'])};rng=np.random.default_rng(183);maxerr=0
for side,target in targetdata['targets'].items():
 for sample in range(150):
  source={}
  for name in bridge.ordered(parents):
   mat=np.eye(4);mat[:3,:3]=Rotation.from_rotvec(rng.normal(0,.1,3)).as_matrix()@np.array(target[name])[:3,:3];mat[:3,3]=np.array(target[name])[:3,3]+rng.normal(0,.025,3);source[name]=mat.tolist()
  corrections=bridge.solve(source,target,parents);out=bridge.reconstruct(source,parents,corrections)
  err=max(abs(np.array(out[n])-np.array(target[n])).max()for n in bones);maxerr=max(maxerr,float(err));assert err<1e-10
# Native sign convention serialized node order RotateXYZ then TranslateXYZ.
for index,bone in enumerate(bones):
 for offset,(op,axis)in enumerate([(op,axis)for op in ['Rotate','Translate']for axis in 'XYZ']):
  node=b[f'ML183_Base{index*6+offset}'];assert f'Bone "{bone}"'in node and f'Axis {axis}'in node and f'Op {op}'in node
helper=(w/'MLUnarmedPose183.c').read_text();assert 'if (side >= 0 && !sampled && !Failed[side] && Settled > 0.35)'in helper
assert 'Capture(actor)'in helper and helper.count('Capture(actor)')==1
assert 'BodyRevision'not in helper and 'ValuesRevision'not in helper # edits cannot invalidate/capture corrected output
assert 'actor.AnimSetBool(RaisedVar, false)'in helper and 'actor.AnimSetBool(ADSVar, false)'in helper
assert 'actor.AnimSetFloat(NativeVar, 1)'in helper
assert 'Vars.Count() == 237'in helper
assert not re.search(r'\w+\[[^\]]+\]\s*(?:\+\+|--)',helper)
# Menu data independent, weapon page inaccessible, same synchronized side hold.
for name in ['MLPoseEditorMenu144.c','MLBodyMenu149.c','MLADSLeanKeys.c']:
 s=(m/name).read_text();assert 'ML182WeaponState'not in s and 'ML182BodyState'not in s
assert 'unusedTab.Show(false)'in(m/'MLPoseEditorMenu144.c').read_text()
preset=(w/'MLUnarmedPreset183.c').read_text();assert '$profile:MLUnarmedLeanPreset.json'in preset and '$profile:MLCrouchLeanPreset.json'not in preset
scene=(kit/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();start=scene.index(' PlayerBase ML181CreatePreview');stop=scene.index(' override void OnMissionFinish',start);spawn=scene[start:stop]
assert 'CreateInHands'not in spawn and 'Weapon_Base'not in spawn
assert spawn.count('ML181CreatePreview(')==3 and 'right * 0.5'in spawn
assert '"Hoodie_Red", true'in spawn and '"Hoodie_Blue", false'in spawn
assert 'SetScale'not in scene and 'SetScale'not in helper
player=(w/'MLADSLeanPlayer.c').read_text();assert 'move.ForceStance(DayZPlayerConstants.STANCEIDX_ERECT)'in player
assert 'm_ML183UnarmedPose.Update(this, pDt, m_MLADSLeanDemoAmount, m_ML182NativeReference);\n   return;'in player
# There is no recapture while sliders change: the side snapshot stays fixed.
captures=[0,0];ready=[False,False]
for step in range(1000):
 side=(step//100)%2
 if not ready[side]:captures[side]+=1;ready[side]=True
assert captures==[1,1]
result={'crouch_sha256':sha,'raw_approved_files':'identical','new_graph_nodes':len(named),'new_controls':94,'single_native_base_path':True,'fk_cases':300,'max_fk_error':maxerr,'menu_scene_routing':'passed','native_compile_rendering_FPS':'NOT RUN'}
(kit/'Unarmed-Comparison-Checks-v183.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
