"""Bake body-only targets from exact historical pose audits and current approved save.
No authoring data is included in the runtime ZIP. Native rendering still needs testing.
"""
from pathlib import Path
import sys,json,re,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent))
from dayz_graph_formats import newnodes
root=Path(__file__).resolve().parents[1]
base=root/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v182'
out=base.with_name('MovementLab_ADS_Lean_Mosin_v183')
w=out/'LogicSource/Scripts/4_World'
# Bake body-only target frames from the existing approved raised pose heritage.
# No arm/shoulder targets are baked: unarmed native local arm pose is inherited.
nodes=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());heritage=json.loads((base/'Native-Head-Travel-v55.json').read_text());parents=heritage['parents'];preset=json.loads((base/'MLLeanPreset.json').read_text())
body=['Pelvis','Spine','Spine1','Spine2','Spine3','Neck','Neck1','Head','LeftUpLeg','LeftLeg','LeftFoot','RightUpLeg','RightLeg','RightFoot'];compressed=[-1,0,1,2,3,4,5,6,0,8,9,0,11,12]
children={n:[]for n in parents}
for n,p in parents.items():
 if p:children[p].append(n)
def descendants(n):return [n]+[x for c in children[n]for x in descendants(c)]
subs={n:descendants(n)for n in parents}
def transform(p,n,R=None,t=None):
 pivot=p[n][:3,3].copy()
 for child in subs[n]:
  if R is not None:p[child][:3,3]=pivot+R@(p[child][:3,3]-pivot);p[child][:3,:3]=R@p[child][:3,:3]
  if t is not None:p[child][:3,3]+=t
def apply_nodes(p,selected):
 for node in selected:
  n=re.search(r'Bone "([^"]+)"',node)[1];axis='XYZ'.index(re.search(r'Axis ([XYZ])',node)[1]);value=float(re.search(r'Amount ([-+\d.eE]+)',node)[1]);v=np.zeros(3);v[axis]=value
  if 'Op Rotate' in node:transform(p,n,R=Rotation.from_euler('xyz',-v).as_matrix())
  else:transform(p,n,t=v)
targets={}
for side in ['left','right']:
 p={n:np.array(matrix,float)for n,matrix in heritage['sides'][side]['desired'].items()}
 if side=='right':
  # v164 compacted several authored139 nodes; do not reconstruct a partial
  # prefix from node names. The160 audit retains the exact pre160 frames.
  audit=json.loads((base/'Right-Position-v160.json').read_text())
  p={n:np.array(matrix,float)for n,matrix in audit['reference'].items()}
  prior=json.loads((base.with_name('MovementLab_ADS_Lean_Mosin_v158')/'MLLeanPreset.json').read_text())
  for part in reversed(prior['RightLean']['BodySettings']['Parts']):
   n=part['BoneName']
   for axis,key in reversed(list(enumerate(['Pitch','Yaw','Roll']))):
    a=np.zeros(3);a[axis]=-part[key]*np.pi/180;transform(p,n,R=Rotation.from_euler('xyz',a).as_matrix())
   transform(p,n,t=-np.array([part[x]for x in ['X','Y','Z']])*.01)
 saved=preset[side.title()+'Lean'];v=saved['WeaponSettings'];headangles=[v['Head'+a]for a in ['Pitch','Yaw','Roll']]
 # F6 fixed-model X,Y,Z head rotation order precedes F7.
 for axis,value in enumerate(headangles):
  a=np.zeros(3);a[axis]=value*np.pi/180;transform(p,'Head',R=Rotation.from_euler('xyz',a).as_matrix())
 for part in saved['BodySettings']['Parts']:
  n=part['BoneName']
  if n not in body:continue
  transform(p,n,t=np.array([part[x]for x in ['X','Y','Z']])*.01)
  for axis,key in enumerate(['Pitch','Yaw','Roll']):
   a=np.zeros(3);a[axis]=part[key]*np.pi/180;transform(p,n,R=Rotation.from_euler('xyz',a).as_matrix())
 if side=='right':apply_nodes(p,[nodes['ML160_Pelvis_Translate_X']]+[nodes[f'ML160_Right{part}_Rotate_{axis}']for part in ['UpLeg','Leg','Foot']for axis in 'XYZ'])
 targets[side]={n:p[n].tolist()for n in body}
(out/'Unarmed-Body-Targets-v183.json').write_text(json.dumps({'standing_sha256':hashlib.sha256((base/'MLLeanPreset.json').read_bytes()).hexdigest(),'bones':body,'parents':compressed,'targets':targets,'arms':'native unarmed local pose; no raised shoulder/arm/forearm/hand offsets imported','height':'same rig/scale; authored body heights retained, no scale or height override','native_rendering':'NOT RUN'},indent=2)+'\n')
# Emit immutable target frames as literals: no extra runtime loader/schema.
s='''// Targets contain body/legs only. Arms inherit the native lowered unarmed pose.
class ML183Targets
{
 static ML172Snapshot Build(bool left)
 {
  ML172Snapshot result = new ML172Snapshot;
  if (left)
  {
'''
for index,side in enumerate(['left','right']):
 if index:s+='  }\n  else\n  {\n'
 for n in body:
  a=np.array(targets[side][n]);args=[a[:3,3],a[0,:3],a[1,:3],a[2,:3]]
  s+='   Add(result, '+', '.join('Vector('+', '.join(f'{x:.12g}'for x in v)+')'for v in args)+');\n'
s+='''  }
  return result;
 }
 static void Add(ML172Snapshot result, vector position, vector rowA, vector rowB, vector rowC)
 {
  ML172Frame frame = new ML172Frame;
  frame.Position = position;
  frame.Orientation = new ML144Rot;
  frame.Orientation.A = rowA;
  frame.Orientation.B = rowB;
  frame.Orientation.C = rowC;
  result.Frames.Insert(frame);
 }
};
''';(w/'MLUnarmedTargets183.c').write_text(s)
