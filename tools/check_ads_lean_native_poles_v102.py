"""Native math parity, one-shot/scope isolation and backpack wiring checks."""
from pathlib import Path
import re,json,math
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v101';b=base/'MovementLab_ADS_Lean_Mosin_v102'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
for name,node in old.items():
 expected=node.replace('Child "ML88_LoweredRaisedOnly"','Child "ML102_LeftElbowDirections"') if name=='MeleeBlockQ' else node
 assert new[name]==expected,name
spec=json.loads((b/'Native-Elbow-Poles-v102.json').read_text());agr=(b/'WorkspaceSource/player_main.agr').read_text()
for control in spec['controls']:assert agr.count('AnimSrcGCTVarFloat '+control+' ')==1
for side in ('Left','Right'):
 target='ML102_'+side+'WristHold'
 assert 'IkTarget "'+target+'"' in new['ML102_CapturePrivateHands']
 assert 'IkTarget "'+target+'"' in new['ML102_RestorePrivateHands']
 for axis in 'XYZ':assert 'Expression "ML102'+side+axis+'"' in new['ML102_Pole_'+side+'_'+axis]
for name in ('ML102_CapturePrivateHands','ML102_RestorePrivateHands'):
 for chain in re.findall(r'IkChain "([^"]+)"',new[name]):assert chain in agr
# Port the native helper's literal position/rotation equations.
def solve(root,elbow,wrist,pole):
 upper=elbow-root;lower=wrist-elbow;reach=wrist-root;l1=np.linalg.norm(upper);l2=np.linalg.norm(lower);distance=np.linalg.norm(reach);direction=reach/distance
 along=(l1*l1-l2*l2+distance*distance)/(2*distance);radius=math.sqrt(max(0,l1*l1-along*along));projected=pole-direction*np.dot(pole,direction);projected/=np.linalg.norm(projected);goal=root+direction*along+projected*radius
 source=upper/l1;target=(goal-root)/np.linalg.norm(goal-root);cross=np.cross(source,target);sine=np.linalg.norm(cross);cosine=np.clip(np.dot(source,target),-1,1)
 if sine<1e-6:return np.zeros(3),goal
 x,y,z=cross/sine;q=1-cosine;d20=z*x*q-y*sine;d21=z*y*q+x*sine;d22=cosine+z*z*q;d10=y*x*q+z*sine;d00=cosine+x*x*q;ay=math.asin(np.clip(-d20,-1,1))
 if abs(math.cos(ay))>1e-6:ax=math.atan2(d21,d22);az=math.atan2(d10,d00)
 else:ax=math.atan2(-(y*z*q-x*sine),cosine+y*y*q);az=0
 return -np.array([ax,ay,az]),goal
pose=json.loads((a/'Left-Shoulder-Height-v101.json').read_text())['desired'];rng=np.random.default_rng(102)
for side,pole in [('Left',np.array([.35,-1,.15])),('Right',np.array([1,-.25,.6]))]:
 root,elbow,wrist=[np.array(pose[side+x])[:3,3] for x in ('Arm','ForeArm','Hand')]
 for offset in [np.zeros(3)]+[rng.normal(0,.02,3) for _ in range(100)]:
  r=root+offset;e=elbow+offset;w=wrist+offset;angles,goal=solve(r,e,w,pole);matrix=np.array(bridge.rotation(*(-angles)))[:3,:3]
  np.testing.assert_allclose(r+matrix@(e-r),goal,atol=1e-9)
  assert abs(np.linalg.norm(goal-r)-np.linalg.norm(e-r))<1e-10
  assert abs(np.linalg.norm(w-goal)-np.linalg.norm(w-e))<1e-10
  direction=(w-r)/np.linalg.norm(w-r);assert np.dot(pole,goal-e)>=-1e-10
  if side=='Left':assert goal[1]<e[1]
  else:assert goal[0]>e[0]
# Source checks ensure calibration is one-time from an unmodified overlay,
# then constants are written, not incremental feedback from corrected bones.
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();helper=(b/'LogicSource/Scripts/4_World/MLArmPoleMath102.c').read_text()
assert '!m_ML102PoleReady && canSample && m_ML102LeftStable > 0.25' in player
assert 'm_ML102CalibAttempts < 3' in player and 'm_ML102CalibCooldown = 1.0' in player
assert 'm_ML102PoleVars[poleIndex] >= 0' in player
assert 'm_ML102PoleVars[poleIndex] != m_ML102PoleVars[priorPole]' in player
assert 'AnimSetFloat(m_ML102PoleVars[0], enabled)' in player
assert 'AutomaticPoseCaptureBudget = 16' in player and 'AutomaticPoseCaptureBudget--' in player
assert 'Elbow test ready' in player
assert not re.search(r'SetBone|SetPosition|SetTransform|OverrideAim',helper)
cam='LogicSource/Scripts/4_World/MLADSLeanCamera.c';assert (a/cam).read_text().replace('MLCAM101','MLCAM102')==(b/cam).read_text()
mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert 'FindAttachmentBySlotName("Back")' in mission
assert 'CreateAttachment("AliceBag_Green")' in mission and 'CreateAttachment("MountainBag_Green")' in mission
for weapon in ('AK74','MP5K','FNX45','SVD'):assert '"'+weapon+'"' in mission
ammo='LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c'
assert (a/ammo).read_text().replace('MLLOADOUT101','MLLOADOUT102').replace('MLADSLEAN101','MLADSLEAN102')==(b/ammo).read_text()
def clamp(x,lo,hi):return max(lo,min(hi,x))
env=dict(clamp=clamp,MLADSLeanAmount=-1,MLADSLeanGate=1,MLADSLeanMoveBlend=1,Stance=0,ML87FirstPersonCrouchLean=0,ML93ArmDrop=1,ML102ElbowEnabled=1)
assert eval(spec['scope_weight'],{'__builtins__':{}},env)==1
for key,val in [('MLADSLeanAmount',1),('MLADSLeanMoveBlend',0),('Stance',1),('ML87FirstPersonCrouchLean',1),('ML93ArmDrop',0),('ML102ElbowEnabled',0)]:
 d=env.copy();d[key]=val;assert eval(spec['scope_weight'],{'__builtins__':{}},d)==0
print('PASS: native math equations reach fixed-wrist elbow circles and desired down/out directions; one-shot bound/capped calibration, private targets, original right/camera/loadout preserved; backpack slot explicit. Native compilation/solver/render unverified.')
