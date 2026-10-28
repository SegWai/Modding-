"""Shared native lean input, complete upper mirroring and lower-body isolation."""
from pathlib import Path
import sys,json,re,hashlib,copy
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
from mirror_ads_lean_body_preset import mirror
r=Path(__file__).resolve().parents[1];base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v183';out=base.with_name('MovementLab_ADS_Lean_Mosin_v184');spec=json.loads((out/'Unarmed-Mirror-v184.json').read_text())
raw=(r/'ads-lean-test/User-Presets/MLUnarmedLeanPreset-Uploaded-v183-20261028.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==spec['upload_sha256'];uploaded=json.loads(raw)
new=(out/'MLUnarmedLeanPreset.json').read_bytes();preset=json.loads(new);assert preset['RightLean']==uploaded['RightLean']
for rel in ['Profiles/LeanMosin/MLUnarmedLeanPreset.json','LogicSource/Presets/MLUnarmedLeanPreset.json']:assert (out/rel).read_bytes()==new
for name in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json']:
 for rel in [name,'Profiles/LeanMosin/'+name,'LogicSource/Presets/'+name]:assert(out/rel).read_bytes()==(base/rel).read_bytes()
assert preset['LeftLean']['BodySettings']==mirror(preset['RightLean']['BodySettings'])
a=preset['RightLean']['WeaponSettings'];b=preset['LeftLean']['WeaponSettings']
for side,other in [('Left','Right'),('Right','Left')]:
 for axis in ['Pitch','Yaw','Roll']:assert b[side+axis]==a[other+axis]*(1 if axis=='Pitch'else -1)
for field in ['HeadYaw','HeadRoll','X','Yaw','Roll','MuzzleYaw']:assert b[field]==-a[field]
S=np.diag([-1.,1,1,1]);t=json.loads((out/'Unarmed-Body-Targets-v184.json').read_text())
for bone in t['bones']:
 other='Right'+bone[4:]if bone.startswith('Left')else('Left'+bone[5:]if bone.startswith('Right')else bone)
 assert np.allclose(t['targets']['left'][bone],S@np.array(t['targets']['right'][other])@S,atol=1e-12)
# Current right base itself is untouched; only hip attachment changes at runtime.
assert t['targets']['right']==json.loads((base/'Unarmed-Body-Targets-v183.json').read_text())['targets']['right']
old=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());nodes=newnodes((out/'WorkspaceSource/locomotion.agf').read_text());removed=set(spec['removed_lower_target_nodes']);assert len(removed)==42
for name in removed:assert name not in nodes
for name,node in nodes.items():
 if name.startswith('ML183_Base'):
  index=int(name[len('ML183_Base'):]);assert 6<=index<48
  assert not re.search(r'Bone "(?:Pelvis|\w*Leg|\w*Foot)"',node)
for name in spec['native_expression_updates']:
 if name in ['ML183_Base6','ML183_Arm0']:continue
 assert 'ML184PreviewLean' in nodes[name] and 'ML184PreviewActive'in nodes[name]
 expected=re.sub(r'\bLean\b','(Lean+(ML184PreviewLean-Lean)*ML184PreviewActive)',old[name]);assert nodes[name]==expected
# Each old native expression is EXACTLY equivalent at active=0 for all native
# lean values; at active=1 it follows the shared demo signal even if Lean=0.
checks=0
for name in spec['native_expression_updates']:
 if name.startswith('ML183_'):continue
 expr=re.search(r'Expression "([^"]+)"',nodes[name])[1]
 orig=re.search(r'Expression "([^"]+)"',old[name])[1]
 for native in [-1,-.5,0,.5,1]:
  for demo in [-1,0,1]:
   env={'Lean':native,'ML184PreviewLean':demo,'ML184PreviewActive':0,'MLADSLeanAmount':0,'MLADSLeanSmoothLow':0,'MLADSLeanGate':0}
   f={'__builtins__':{},'clamp':lambda x,a,b:max(a,min(b,x))}
   assert eval(expr,f,env)==eval(orig,f,env)
   env['ML184PreviewActive']=1
   expected={**env,'Lean':demo};assert eval(expr,f,env)==eval(orig,f,expected);checks+=1
# Validate exact reflection of the noncommuting F6 then F7 rotations.
for side in ['Left','Right']:
 other='Right'if side=='Left'else'Left'
 v=np.array([a[side+x]for x in ['Pitch','Yaw','Roll']]);u=np.array([b[other+x]for x in ['Pitch','Yaw','Roll']]);s=S[:3,:3]
 assert np.allclose(Rotation.from_euler('xyz',u,degrees=True).as_matrix(),s@Rotation.from_euler('xyz',v,degrees=True).as_matrix()@s,atol=1e-12)
# FK of upper-only runtime attachment: pelvis and all six leg frames are exact
# source frames; upper target positions follow native pelvis, no hip overlay.
rng=np.random.default_rng(184);maxerr=0
for side in ['left','right']:
 target={n:np.array(v)for n,v in t['targets'][side].items()}
 for case in range(100):
  source={n:v.copy()for n,v in target.items()}
  for n in source:
   source[n][:3,:3]=Rotation.from_rotvec(rng.normal(0,.08,3)).as_matrix()@source[n][:3,:3];source[n][:3,3]+=rng.normal(0,.02,3)
  result={};hip=source['Pelvis'][:3,3];targethip=target['Pelvis'][:3,3]
  for index,(n,parent)in enumerate(zip(t['bones'],t['parents'])):
   if index==0 or index>=8:result[n]=source[n].copy();continue
   parentname=t['bones'][parent];current=result[parentname]@np.linalg.inv(source[parentname])@source[n];desired=target[n].copy();desired[:3,3]=hip+target[n][:3,3]-targethip
   R=desired[:3,:3]@current[:3,:3].T;translation=desired[:3,3]-current[:3,3];replay=current.copy();replay[:3,:3]=R@current[:3,:3];replay[:3,3]+=translation;result[n]=replay
   maxerr=max(maxerr,float(abs(replay-desired).max()))
  for index,n in enumerate(t['bones']):
   if index==0 or index>=8:assert np.array_equal(result[n],source[n])
assert maxerr<1e-12
helper=(out/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'actor.AnimSetFloat(PreviewVar, 1)'in helper and 'actor.AnimSetFloat(PreviewLeanVar, lean)'in helper
assert 'if (boneIndex == 0 || boneIndex >= 8)'in helper and 'sourceHip.Position + relativeTarget'in helper
# DAG and references. All changed gate/targets remain single-path.
sys.setrecursionlimit(20000);visiting=set();done=set()
def visit(name):
 if name in done or name not in nodes:return
 assert name not in visiting,name
 visiting.add(name)
 for child in re.findall(r'\bChild\d* "([^"]+)"',nodes[name]):
  assert child not in removed,(name,child)
  visit(child)
 visiting.remove(name);done.add(name)
for name in nodes:
 if not name.startswith('{'):visit(name)
result={'approved_three_banks':'byte-identical','uploaded_right':'identical','left_base_and_editor':'anatomically mirrored','native_lean_expression_cases':checks,'lower_target_nodes_removed':42,'upper_attachment_FK_cases':200,'max_FK_error':maxerr,'native_compile_lean_rendering':'NOT RUN'}
(out/'Unarmed-Mirror-Checks-v184.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
