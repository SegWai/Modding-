from pathlib import Path
import json,re,sys,math
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,'tools');from dayz_graph_formats import newnodes
k=Path('ads-lean-test/MovementLab_ADS_Lean_Mosin_v158');d=json.loads((k/'Native-Head-Travel-v55.json').read_text());parents=d['parents'];p={n:np.array(m,float) for n,m in d['sides']['right']['desired'].items()}
children={n:[] for n in p}
for n,parent in parents.items():
 if parent:children[parent].append(n)
def sub(n):
 return [n]+[x for c in children[n] for x in sub(c)]
subs={n:sub(n) for n in p}
def move(p,n,R=None,t=None):
 pivot=p[n][:3,3].copy()
 for c in subs[n]:
  if R is not None:
   p[c][:3,3]=pivot+R@(p[c][:3,3]-pivot);p[c][:3,:3]=R@p[c][:3,:3]
  if t is not None:p[c][:3,3]+=t
nodes=newnodes((k/'WorkspaceSource/locomotion.agf').read_text())
# Follow existing transform ordering for v139 body, through right level-head.
chain=[];name='ML140_LevelRightHead'
while name!='ML133_StandingLeftElbow':
 node=nodes[name]
 if name.startswith('ML139_RightStraight_') or name=='ML140_LevelRightHead':chain.append(node)
 m=re.search(r'\bChild(?:0)? "([^"]+)"',node)
 if not m:raise Exception(name)
 name=m[1]
for node in reversed(chain):
 bone=re.search(r'Bone "([^"]+)"',node)[1];axis=re.search(r'Axis ([XYZ])',node)[1];op=re.search(r'Op (\w+)',node)[1];value=float(re.search(r'Amount ([\d.e+-]+)',node)[1]);a='XYZ'.index(axis)
 if op=='Rotate':
  angles=np.zeros(3);angles[a]=-value;move(p,bone,Rotation.from_euler('xyz',angles).as_matrix())
 else:
  t=np.zeros(3);t[a]=value;move(p,bone,t=t)
# Approved late F7 offsets in exactly its graph order. F6 arm/head rotations
# do not move the head pivot or legs, so irrelevant to the displacement solve.
preset=json.loads((k/'MLLeanPreset.json').read_text())
for part in preset['RightLean']['BodySettings']['Parts']:
 bone=part['BoneName'];t=np.array([part[x] for x in ['X','Y','Z']])*.01
 if np.any(t):move(p,bone,t=t)
 for i,field in enumerate(['Pitch','Yaw','Roll']):
  if part[field]:
   angles=np.zeros(3);angles[i]=part[field]*math.pi/180;move(p,bone,Rotation.from_euler('xyz',angles).as_matrix())
source={n:m.copy() for n,m in p.items()}
goal=d['sides']['right']['target_head_x_m'];shift=goal-p['Head'][0,3]
def turn(a,b):
 a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);v=np.cross(a,b);ss=np.linalg.norm(v);cc=np.clip(a@b,-1,1)
 if ss<1e-7:return np.eye(3)
 return Rotation.from_rotvec(v/ss*math.atan2(ss,cc)).as_matrix()
# Preserve the approved upright upper body and its height. Translate the
# complete pelvis subtree to the restored reference; retain right foot frame
# by re-solving that leg. Left leg keeps its exact relative pose and follows
# the pelvis into a narrower stance, remaining at the same ground height.
delta=np.array([shift,0.,0.]);move(p,'Pelvis',t=delta)
side='Right';names=[side+x for x in ['UpLeg','Leg','Foot']]
a,e,f=[p[n][:3,3].copy() for n in names];target=source['RightFoot'][:3,3].copy()
l1=np.linalg.norm(e-a);l2=np.linalg.norm(f-e);v=target-a;dist=np.linalg.norm(v)
assert abs(l1-l2)+.005<dist<l1+l2-.005,('right leg unsafe',dist,l1+l2)
u=v/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);pole=e-a;pole-=u*(pole@u);assert pole@pole>1e-8;pole/=np.linalg.norm(pole)
goal_knee=a+u*along+pole*np.sqrt(max(0,l1*l1-along*along))
upper=turn(e-a,goal_knee-a);move(p,'RightUpLeg',R=upper)
assert np.max(abs(p['RightLeg'][:3,3]-goal_knee))<1e-9
lower=turn(p['RightFoot'][:3,3]-goal_knee,target-goal_knee);move(p,'RightLeg',R=lower)
move(p,'RightFoot',R=source['RightFoot'][:3,:3]@p['RightFoot'][:3,:3].T)
import captured_pose_bridge as bridge
reference={n:m.tolist() for n,m in source.items()};desired={n:m.tolist() for n,m in p.items()}
corr=bridge.solve(reference,desired,parents);replay=bridge.reconstruct(reference,parents,corr)
error=max(abs(replay[n][i][j]-desired[n][i][j]) for n in parents for i in range(4) for j in range(4));assert error<1e-9
assert abs(p['Head'][0,3]-goal)<1e-9
for n in subs['RightFoot']:assert np.max(abs(p[n]-source[n]))<1e-9,n
for n in subs['Spine']+subs['LeftUpLeg']:
 assert np.max(abs(p[n][:3,:3]-source[n][:3,:3]))<1e-9,n
 assert np.max(abs(p[n][:3,3]-source[n][:3,3]-delta))<1e-9,n
for side in ['Left','Right']:
 for chain in [['Arm','ForeArm','Hand'],['UpLeg','Leg','Foot']]:
  names=[side+x for x in chain]
  for first,last in zip(names,names[1:]):assert abs(np.linalg.norm(p[last][:3,3]-p[first][:3,3])-np.linalg.norm(source[last][:3,3]-source[first][:3,3]))<1e-9
report={'head_neutral_reference_x_m':goal-.219,'reference_head_before_m':source['Head'][:3,3].tolist(),'target_right_head_x_m':goal,'pelvis_shift_m':delta.tolist(),'left_foot_displacement_m':(p['LeftFoot'][:3,3]-source['LeftFoot'][:3,3]).tolist(),'right_foot_error_m':float(np.max(abs(p['RightFoot']-source['RightFoot']))),'right_leg_reach_reserve_m':float(l1+l2-dist),'reference':reference,'desired':desired,'parents':parents,'corrections':corr,'reconstruction_error':error,'target_reference':'historical native neutral raised HeadX+0.219m plus approved current F7 offsets; actual current actor displacement must be verified in DayZ','native_validation':'NOT RUN'}
Path('/tmp/solve160.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['reference','desired','parents','corrections']},indent=2))
