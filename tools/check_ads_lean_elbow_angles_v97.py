"""Check feasible requested arm elevations and preserved grip on reference."""
from pathlib import Path
import json,re,math
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v95';b=base/'MovementLab_ADS_Lean_Mosin_v97'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());solve=json.loads((b/'Left-Elbows-Solve-v97.json').read_text());natural=json.loads((b/'Left-Hold-Natural-v97.json').read_text());before=json.loads((a/'Left-Arm-Rotation-Solve-v95.json').read_text())['desired']
for name,node in old.items():
 if name.startswith('ML32_ReferenceHold_') and not name.startswith('ML32_ReferenceHold_LeftShoulder_'):continue
 expected=node.replace('Child "ML88_LoweredRaisedOnly"','Child "ML97_LeftMovingElbowsOnly"') if name=='MeleeBlockQ' else node
 assert new[name]==expected,name
for side,angle in [('Right',80),('Left',45)]:
 a0=np.array(solve['desired'][side+'Arm'])[:3,3];e=np.array(solve['desired'][side+'ForeArm'])[:3,3];upper=e-a0
 actual=math.degrees(math.acos(np.clip(-upper[1]/np.linalg.norm(upper),-1,1)))
 assert abs(actual-angle)<1e-8
 if side=='Right':assert upper[0]>.2
 hand=np.array(solve['desired'][side+'Hand']);oldhand=np.array(before[side+'Hand'])
 np.testing.assert_allclose(hand[:3,3]-oldhand[:3,3],solve['common_hand_shift_from_v95_m'],atol=1e-9)
 np.testing.assert_allclose(hand[:3,:3],oldhand[:3,:3],atol=1e-9)
 np.testing.assert_allclose(hand,natural['desired'][side+'Hand'],atol=1e-9)
# Common hand shift leaves the exact relative grip transform unchanged.
L=np.array(solve['desired']['LeftHand']);R=np.array(solve['desired']['RightHand']);oldL=np.array(before['LeftHand']);oldR=np.array(before['RightHand'])
np.testing.assert_allclose(np.linalg.inv(R)@L,np.linalg.inv(oldR)@oldL,atol=1e-9)
for data in (natural,solve):
 parents=data['parents'];replay=bridge.reconstruct(data['base'],parents,{n:{'rotation_xyz':data['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in parents})
 for n in parents:
  np.testing.assert_allclose(replay[n],data['desired'][n],atol=1e-8)
  p=parents[n]
  if p:
   d0=np.linalg.norm(np.array(before[n])[:3,3]-np.array(before[p])[:3,3]);d1=np.linalg.norm(np.array(replay[n])[:3,3]-np.array(replay[p])[:3,3]);assert abs(d0-d1)<1e-8
 for n in ('Pelvis','Spine','Spine1','Spine2','Spine3','Head','LeftShoulder','RightShoulder','LeftFoot','RightFoot'):
  np.testing.assert_allclose(data['desired'][n],before[n],atol=1e-8)
# Active branch limited to moving left, non-first-person, ON comparison.
expr=re.search(r'BlendWeight "([^"]+)"',new['ML97_LeftMovingElbowsOnly'])[1]
def clamp(x,lo,hi):return min(hi,max(lo,x))
env=dict(clamp=clamp,MLADSLeanAmount=-1,MLADSLeanGate=1,MLADSLeanMoveBlend=1,MLADSLeanWeaponShift=1,Stance=0,ML87FirstPersonCrouchLean=0,ML93ArmDrop=1)
assert eval(expr,{'__builtins__':{}},env)==1
for key,val in [('MLADSLeanAmount',1),('MLADSLeanMoveBlend',0),('Stance',1),('ML87FirstPersonCrouchLean',1),('ML93ArmDrop',0)]:
 d=env.copy();d[key]=val;assert eval(expr,{'__builtins__':{}},d)==0
cam='LogicSource/Scripts/4_World/MLADSLeanCamera.c';assert (a/cam).read_text().replace('MLCAM95','MLCAM97')==(b/cam).read_text()
keys=(b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();assert 'KC_F8 && m_ML71ControlDown' in keys
print('PASS: right 80deg outward, left 45deg down on captured reference; reachable shifted hold preserves relative grip/orientation/lengths/body; right-moving values and camera unchanged; Ctrl+F8 retained. Native output unverified.')
