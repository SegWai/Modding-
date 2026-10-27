"""Verify direct graph wiring and stored reference FK, not native playback."""
from pathlib import Path
import sys,json,re,hashlib
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import captured_pose_bridge as bridge
from dayz_graph_formats import newnodes
root=Path(__file__).resolve().parents[1]/'ads-lean-test';a=root/'MovementLab_ADS_Lean_Mosin_v158';b=root/'MovementLab_ADS_Lean_Mosin_v160'
d=json.loads((b/'Right-Position-v160.json').read_text());ref={n:np.array(m) for n,m in d['reference'].items()};desired={n:np.array(m) for n,m in d['desired'].items()};delta=np.array(d['pelvis_shift_m'])
out=bridge.reconstruct(d['reference'],d['parents'],d['corrections']);error=max(abs(out[n][i][j]-d['desired'][n][i][j]) for n in out for i in range(4) for j in range(4));assert error<1e-10
assert .3<delta[0]<.35 and np.allclose(delta[1:],0)
assert abs(desired['Head'][0,3]-d['head_neutral_reference_x_m']-.219)<1e-10
for n in ['Pelvis','Spine','Spine1','Spine2','Spine3','Neck','Neck1','Head','LeftArm','RightArm','LeftForeArm','RightForeArm','LeftHand','RightHand','LeftFoot']:
 assert np.allclose(desired[n][:3,:3],ref[n][:3,:3],atol=1e-10),n
 assert np.allclose(desired[n][:3,3]-ref[n][:3,3],delta,atol=1e-10),n
assert np.allclose(desired['RightFoot'],ref['RightFoot'],atol=1e-10)
# A common translation cannot change relative hands or their gun attachment.
for n in ['LeftHand','RightHand']:
 assert np.allclose(desired[n][:3,3]-desired['Head'][:3,3],ref[n][:3,3]-ref['Head'][:3,3])
for side in ['Left','Right']:
 for chain in [('UpLeg','Leg','Foot'),('Arm','ForeArm','Hand')]:
  names=[side+x for x in chain]
  for first,last in zip(names,names[1:]):
   assert abs(np.linalg.norm(desired[first][:3,3]-desired[last][:3,3])-np.linalg.norm(ref[first][:3,3]-ref[last][:3,3]))<1e-10
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
for n,node in old.items():
 expected=node.replace('Child "ML149_BodyWithWeapon"','Child "ML160_RightPositionOnly"') if n=='ML157_HeadX' else node
 assert new[n]==expected,n
added={n for n in set(new)-set(old) if not n.startswith('{')};assert added==set(d['graph_nodes'])|{'ML160_WeaponFollow','ML160_RightPositionOnly'}
for n in d['graph_nodes']:
 assert f'Expression "{d["graph_scope"]}"' in new[n]
# Reconstruct serialized native amounts, not just the solver's desired data.
serialized={n:{'rotation_xyz':[0.,0.,0.],'translation_xyz':[0.,0.,0.]} for n in d['parents']}
for n in d['graph_nodes']:
 node=new[n];bone=re.search(r'Bone "([^"]+)"',node)[1];axis='XYZ'.index(re.search(r'Axis ([XYZ])',node)[1]);op=re.search(r'Op (\w+)',node)[1];value=float(re.search(r'Amount ([-+\d.eE]+)',node)[1])
 serialized[bone]['rotation_xyz' if op=='Rotate' else 'translation_xyz'][axis]= -value if op=='Rotate' else value
out=bridge.reconstruct(d['reference'],d['parents'],serialized)
assert max(abs(out[n][i][j]-d['desired'][n][i][j]) for n in out for i in range(4) for j in range(4))<1e-10
expr=d['graph_scope']
for lean in [-1,0,1]:
 for stance in [0,1,2]:
  for moving in [0,1]:
   values={'MLADSLeanAmount':lean,'MLADSLeanGate':1,'Stance':stance,'MLADSLeanMoveBlend':moving,'MovementSpeed':moving,'ML93ArmDrop':1,'ML106ShoulderedGrip':1,'ML87FirstPersonCrouchLean':0}
   weight=eval(expr,{'__builtins__':{},'clamp':lambda x,a,b:max(a,min(b,x))},values)
   assert weight==(1 if lean==1 and stance==0 and moving==0 else 0)
for name in ['MLADSLeanCamera.c','MLVanillaLoadout156.c','MLDemoCycle158.c','MLUnifiedPreset153.c']:
 rel='LogicSource/Scripts/4_World/'+name;assert (a/rel).read_bytes()==(b/rel).read_bytes(),name
for rel in ['MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
 assert hashlib.sha256((b/rel).read_bytes()).hexdigest()=='deeaeac1af612bfe4edaa542e6ebabf6da992b163bd7eac56579a0dd4f0bdb61'
world=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'ML159UpdateTravel' not in world and 'rejected unsafe foot reach' not in world
assert 'WeightPrimaryChain "false"' in new['ML160_WeaponFollow'] and 'WeightSecondaryChain "false"' in new['ML160_WeaponFollow']
report={'direct_graph_displacement_m':d['pelvis_shift_m'],'head_target_from_historical_neutral_m':.219,'left_foot_moves_with_body':True,'right_foot_reference_preserved':True,'upper_body_shape_and_height_preserved':True,'serialized_graph_FK_error':error,'native_test':'NOT RUN; target/displacement/foot stance require native test'}
(b/'Right-Position-Checks-v160.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
