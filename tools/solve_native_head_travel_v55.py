"""Offline pose solve; requires NumPy and SciPy. Does not validate native playback."""
import sys,json,re,math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.spatial.transform import Rotation
import argparse
parser=argparse.ArgumentParser(description='Solve planted-foot native-distance standing lean from captured reference matrices')
parser.add_argument('--input',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--neutral',type=float,default=.118624)
args=parser.parse_args()
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import captured_pose_bridge as bridge
source=json.loads(args.input.read_text());parents=source['parents']
def tm(rows):
 m=np.eye(4);m[:3,:]=np.array([rows[str(i)] for i in range(4)]).T;u,s,v=np.linalg.svd(m[:3,:3]);m[:3,:3]=u@v;return m
children={n:[] for n in parents}
for n,p in parents.items():
 if p:children[p].append(n)
def descendants(n):
 result=[n]
 for ch in children[n]:result+=descendants(ch)
 return result
subtrees={n:descendants(n) for n in parents}
def move_bone(pose,n,new):
 delta=new@np.linalg.inv(pose[n])
 for ch in subtrees[n]:pose[ch]=delta@pose[ch]
def swing(a,b):
 a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);axis=np.cross(a,b);s=np.linalg.norm(axis);c=np.clip(a@b,-1,1)
 if s<1e-10:
  if c>0:return np.eye(3)
  axis=np.cross(a,np.array([1.,0,0]));
  if np.linalg.norm(axis)<1e-5:axis=np.cross(a,np.array([0.,1,0]))
  return Rotation.from_rotvec(axis/np.linalg.norm(axis)*math.pi).as_matrix()
 return Rotation.from_rotvec(axis/s*math.atan2(s,c)).as_matrix()
def bend_spine(reference,angle):
 p={n:m.copy() for n,m in reference.items()}
 n='Spine'
 m=p[n].copy();m[:3,:3]=Rotation.from_euler('z',angle).as_matrix()@m[:3,:3];move_bone(p,n,m)
 return p
result={}
for side,sign in [('left',-1),('right',1)]:
 cid=source['sides'][side]['reference_capture_id'];targetx=args.neutral+(-.42 if side=='left' else .219)
 ref={n:np.array(source['sides'][side]['reference'][n]) for n in parents}
 hip_shift=(targetx-ref['Head'][0,3])*.35
 for attempt in range(100):
  hip_pose={n:m.copy() for n,m in ref.items()};pelvis=hip_pose['Pelvis'].copy();pelvis[0,3]+=hip_shift;move_bone(hip_pose,'Pelvis',pelvis)
  feasible=True
  for limb in ('Left','Right'):
   a,b,c=[limb+k for k in ('UpLeg','Leg','Foot')]
   l1=np.linalg.norm(ref[b][:3,3]-ref[a][:3,3]);l2=np.linalg.norm(ref[c][:3,3]-ref[b][:3,3]);d=np.linalg.norm(ref[c][:3,3]-hip_pose[a][:3,3])
   if d>=l1+l2-.002:feasible=False
  if feasible:break
  hip_shift*=.9
 else:raise ValueError('No feasible planted-foot hip shift')
 def f(a):return bend_spine(hip_pose,a)['Head'][0,3]-targetx
 # Choose the smallest-turn solution near the approved pose.
 brackets=[];grid=np.linspace(-math.radians(65),math.radians(65),261)
 for a,b in zip(grid[:-1],grid[1:]):
  if f(a)*f(b)<=0:brackets.append((a,b))
 if not brackets:raise ValueError('Target unreachable with bounded spine bend')
 angle=min([brentq(f,a,b,xtol=1e-13) for a,b in brackets],key=abs)
 p=bend_spine(hip_pose,angle);delta_head=p['Head'][:3,3]-ref['Head'][:3,3]
 head=p['Head'].copy();head[:3,:3]=ref['Head'][:3,:3];move_bone(p,'Head',head)
 arm_stats={}
 for limb,kind in [(x,k) for k in ('arm','leg') for x in ('Left','Right')]:
  upper=limb+('Arm' if kind=='arm' else 'UpLeg');lower=limb+('ForeArm' if kind=='arm' else 'Leg');hand=limb+('Hand' if kind=='arm' else 'Foot')
  s0,e0,w0=[ref[n][:3,3] for n in (upper,lower,hand)]
  shoulder=p[upper][:3,3].copy();wrist=w0+delta_head if kind=='arm' else w0.copy()
  l1=np.linalg.norm(e0-s0);l2=np.linalg.norm(w0-e0);vec=wrist-shoulder;d=np.linalg.norm(vec)
  if not abs(l1-l2)+1e-6<d<l1+l2-1e-6:raise ValueError((side,limb,'arm unreachable',d,l1+l2))
  u=vec/d;a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-a*a));centre=shoulder+u*a
  pole_guess=e0+delta_head if kind=='arm' else e0+np.array([hip_shift*.5,0,0])
  pole=pole_guess-centre;pole-=u*(pole@u);pole/=np.linalg.norm(pole);elbow=centre+pole*h
  m=p[upper].copy();m[:3,:3]=swing(e0-s0,elbow-shoulder)@ref[upper][:3,:3];m[:3,3]=shoulder;move_bone(p,upper,m)
  assert np.linalg.norm(p[lower][:3,3]-elbow)<1e-6
  m=p[lower].copy();m[:3,:3]=swing(w0-e0,wrist-elbow)@ref[lower][:3,:3];m[:3,3]=elbow;move_bone(p,lower,m)
  assert np.linalg.norm(p[hand][:3,3]-wrist)<1e-6
  m=p[hand].copy();m[:3,:3]=ref[hand][:3,:3];m[:3,3]=wrist;move_bone(p,hand,m)
  arm_stats[limb+'_'+kind]={'upper_length_m':l1,'lower_length_m':l2,'shoulder_wrist_distance_m':d,'remaining_reach_m':l1+l2-d,'elbow_shift_from_rigid_hand_shift_m':float(np.linalg.norm(elbow-pole_guess))}
 reference={n:m.tolist() for n,m in ref.items()};desired={n:m.tolist() for n,m in p.items()};corr=bridge.solve(reference,desired,parents);replay=bridge.reconstruct(reference,parents,corr)
 error=max(abs(replay[n][i][j]-desired[n][i][j]) for n in parents for i in range(4) for j in range(4))
 assert error<1e-10 and abs(p['Head'][0,3]-targetx)<1e-10
 lower_bones=[n for n in parents if n in subtrees['LeftFoot'] or n in subtrees['RightFoot']]
 assert all(np.max(abs(p[n]-ref[n]))<1e-10 for n in lower_bones)
 # Head/hand/finger/weapon rotations stay unchanged; hand and head get same translation.
 for n in ['Head','LeftHand','RightHand']:
  assert np.max(abs(p[n][:3,:3]-ref[n][:3,:3]))<1e-10
  assert np.linalg.norm(p[n][:3,3]-ref[n][:3,3]-delta_head)<1e-10
 result[side]={'reference_capture_id':cid,'target_head_x_m':targetx,'hip_lateral_shift_m':float(hip_shift),'spine_total_adjustment_radians':angle,'spine_total_adjustment_degrees':math.degrees(angle),'head_translation_m':delta_head.tolist(),'head_height_before_m':float(ref['Head'][1,3]),'head_height_after_m':float(p['Head'][1,3]),'reference':reference,'desired':desired,'corrections':corr,'arm_stats':arm_stats,'math_replay_error':error,'lower_bones_preserved':lower_bones}
 print(side,'hip shift',hip_shift,'bend deg',math.degrees(angle),'head shift',delta_head,'armstats',arm_stats)
args.output.write_text(json.dumps({'parents':parents,'sides':result,'target_definition':'Head travel from neutral aimed head: 0.42m character-left, 0.219m character-right. Torso rigid tilt preserves original relative spine bends.'},indent=2)+'\n')
