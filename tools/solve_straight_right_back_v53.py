"""Offline authoring recipe; NumPy/SciPy required. Not native playback validation."""
import sys,json,math
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
import argparse
parser=argparse.ArgumentParser(description='Straighten a standing-right native spine while preserving head height and planted endpoints')
parser.add_argument('--input',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import captured_pose_bridge as bridge
D=json.loads(args.input.read_text());parents=D['parents'];ref={n:np.array(m) for n,m in D['reference'].items()}
children={n:[] for n in parents}
for n,p in parents.items():
 if p:children[p].append(n)
def subtree(n):
 out=[n]
 for ch in children[n]:out+=subtree(ch)
 return out
subs={n:subtree(n) for n in parents}
def move(p,n,m):
 delta=m@np.linalg.inv(p[n])
 for ch in subs[n]:p[ch]=delta@p[ch]
def swing(a,b):
 a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);v=np.cross(a,b);s=np.linalg.norm(v);c=np.clip(a@b,-1,1)
 if s<1e-10:
  if c>0:return np.eye(3)
  v=np.cross(a,[1.,0,0])
  if np.linalg.norm(v)<1e-5:v=np.cross(a,[0.,1,0])
  return Rotation.from_rotvec(v/np.linalg.norm(v)*math.pi).as_matrix()
 return Rotation.from_rotvec(v/s*math.atan2(s,c)).as_matrix()
spines=['Spine','Spine1','Spine2','Spine3'];chain=spines+['Neck'];lengths=[np.linalg.norm(ref[b][:3,3]-ref[a][:3,3]) for a,b in zip(chain,chain[1:])]
neck=ref['Neck'][:3,3];axis=neck-ref['Spine'][:3,3];axis/=np.linalg.norm(axis);base=neck-axis*sum(lengths)
baseoffset=ref['Spine'][:3,3]-ref['Pelvis'][:3,3]
fullPelvis=swing(baseoffset,axis);fullRot=Rotation.from_matrix(fullPelvis)
# Align some pelvic roll with the torso, while leaving enough leg reach reserve.
for fraction in [.5,.45,.4,.35,.3,.25,.2,.1,0]:
 p={n:m.copy() for n,m in ref.items()};partial=Rotation.from_rotvec(fullRot.as_rotvec()*fraction).as_matrix()
 pelvis=p['Pelvis'].copy();pelvis[:3,:3]=partial@ref['Pelvis'][:3,:3];pelvis[:3,3]=base-partial@baseoffset;move(p,'Pelvis',pelvis)
 feasible=True
 for limb in ['Left','Right']:
  a,b,c=[limb+k for k in ('UpLeg','Leg','Foot')];l1=np.linalg.norm(ref[b][:3,3]-ref[a][:3,3]);l2=np.linalg.norm(ref[c][:3,3]-ref[b][:3,3]);d=np.linalg.norm(ref[c][:3,3]-p[a][:3,3])
  if d>=l1+l2-.002:feasible=False
 if feasible:break
else:raise ValueError('Cannot keep feet and height without overextending legs')
position=base.copy()
for a,b,length in zip(chain,chain[1:],lengths):
 m=p[a].copy();m[:3,:3]=swing(ref[b][:3,3]-ref[a][:3,3],axis)@ref[a][:3,:3];m[:3,3]=position;move(p,a,m);position=position+axis*length
assert np.linalg.norm(p['Neck'][:3,3]-neck)<1e-10
move(p,'Neck',ref['Neck'].copy()) # preserve neck/head aim and position exactly
stats={}
for limb,kind in [(l,k) for k in ['arm','leg'] for l in ['Left','Right']]:
 a,b,c=[limb+k for k in (('Arm','ForeArm','Hand') if kind=='arm' else ('UpLeg','Leg','Foot'))]
 s0,e0,w0=[ref[n][:3,3] for n in (a,b,c)];s=p[a][:3,3].copy();w=w0.copy();l1=np.linalg.norm(e0-s0);l2=np.linalg.norm(w0-e0);dist=np.linalg.norm(w-s);u=(w-s)/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=np.sqrt(max(0,l1*l1-along*along));centre=s+u*along
 pole=e0-centre;pole-=u*(pole@u);pole/=np.linalg.norm(pole);e=centre+height*pole
 m=p[a].copy();m[:3,:3]=swing(e0-s0,e-s)@ref[a][:3,:3];m[:3,3]=s;move(p,a,m);assert np.linalg.norm(p[b][:3,3]-e)<1e-7
 m=p[b].copy();m[:3,:3]=swing(w0-e0,w-e)@ref[b][:3,:3];m[:3,3]=e;move(p,b,m);assert np.linalg.norm(p[c][:3,3]-w)<1e-7
 m=ref[c].copy();move(p,c,m)
 stats[limb+'_'+kind]={'reach_reserve_m':float(l1+l2-dist),'middle_joint_displacement_m':float(np.linalg.norm(e-e0))}
for n in subs['Head']+subs['LeftHand']+subs['RightHand']+subs['LeftFoot']+subs['RightFoot']:
 assert np.max(abs(p[n]-ref[n]))<1e-9,n
reference={n:m.tolist() for n,m in ref.items()};desired={n:m.tolist() for n,m in p.items()};corr=bridge.solve(reference,desired,parents);replay=bridge.reconstruct(reference,parents,corr);error=max(abs(replay[n][i][j]-desired[n][i][j]) for n in parents for i in range(4) for j in range(4));assert error<1e-10
before=np.array([ref[n][:3,3] for n in chain]);after=np.array([p[n][:3,3] for n in chain])
def line_error(points):
 u=points[-1]-points[0];u/=np.linalg.norm(u);return float(max(np.linalg.norm(np.cross(v-points[0],u)) for v in points))
report={'scope':'Standing character RIGHT lean only, as shown. Preserve left raised elbow, moving/crouch, head reach and height.','parents':parents,'reference':reference,'desired':desired,'corrections':corr,'pelvis_alignment_fraction':fraction,'pelvis_translation_m':(p['Pelvis'][:3,3]-ref['Pelvis'][:3,3]).tolist(),'spine_axis':axis.tolist(),'spine_chain':chain,'max_spine_centreline_deviation_before_m':line_error(before),'max_spine_centreline_deviation_after_m':line_error(after),'head_position_preserved_m':p['Head'][:3,3].tolist(),'limb_statistics':stats,'reconstruction_error':error,'native_validation':'NOT RUN. Target positions/heights preserved in offline solve; actual skin appearance and native pose need Windows DayZ testing.'}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('pelvis fraction',fraction,'shift',report['pelvis_translation_m'],'curve',report['max_spine_centreline_deviation_before_m'],'->',report['max_spine_centreline_deviation_after_m'],'head',report['head_position_preserved_m'],'limbs',stats)
