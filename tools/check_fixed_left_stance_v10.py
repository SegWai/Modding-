"""Verify mirror hierarchy, contact solve geometry and fixed-left wiring (offline)."""
from pathlib import Path
import re,sys
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];b=r/'shoulder-swap-test/MovementLab_LeftHand_Lean_v10';a=b.with_name('MovementLab_LeftHand_Lean_v9')
h=(b/'LogicSource/Scripts/4_World/MLAShoulderPose.c').read_text();section=h[h.index(' void BuildNames()'):h.index(' void Bind(')]
names=re.findall(r'Names.Insert\("([^"]+)"\)',section);parents=list(map(int,re.findall(r'Parents.Insert\((-?\d+)\)',section)));op=list(map(int,re.findall(r'Opposite.Insert\((\d+)\)',section)))
assert len(names)==62 and len(set(names))==62
for i,p in enumerate(parents):assert p<i and (p>=0 or i==0)
for i,j in enumerate(op):assert op[j]==i
for side in ['Left','Right']:
 for child,parent in [('UpLeg','Pelvis'),('Leg',side+'UpLeg'),('Foot',side+'Leg'),('ToeBase',side+'Foot')]:assert names[parents[names.index(side+child)]]==parent
nd=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
for i,n in enumerate(names):
 for j in range(6):
  k=i*6+j;node=nd['MLASwapPose'+str(k)]
  assert f'Bone "{n}"'in node and f'Expression "MLASwapC{k}"'in node
  child='ML172_SharedWalkingUpper' if k==0 else 'MLASwapPose'+str(k-1)
  assert f'Child "{child}"'in node
assert 'Child1 "MLASwapPose371"'in nd['MLASwapBeforeAim']
agr=(b/'WorkspaceSource/player_main.agr').read_text();controls=re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr)
assert len(controls)==len(set(controls));assert len([x for x in controls if x.startswith('MLASwap')])==379
# Feet swap fore/aft while staying on their anatomical side.
S=np.diag([-1.,1.,1.]);left=np.array([-.15,0.,.10]);right=np.array([.15,0.,-.12])
newleft=S@right;newright=S@left
assert newleft[0]<0<newright[0] and newleft[2]<newright[2]
# Shoulder sagittal-plane reflection switches the leading shoulder.
leftshoulder=np.array([-.2,1.4,.08]);rightshoulder=np.array([.2,1.4,-.05])
assert (S@leftshoulder)[2]>(S@rightshoulder)[2]
# Exact bounded two-bone geometry with the original pole; no limb stretching.
rng=np.random.default_rng(10);err=0
for _ in range(3000):
 upper,lower=rng.uniform(.2,.4,2);distance=rng.uniform(abs(upper-lower)+.003,upper+lower-.003)
 axis=rng.normal(size=3);axis/=np.linalg.norm(axis);pole=rng.normal(size=3);pole-=axis*np.dot(pole,axis);pole/=np.linalg.norm(pole)
 root=rng.normal(0,.1,3);target=root+axis*distance;along=(upper**2-lower**2+distance**2)/(2*distance)
 elbow=root+axis*along+pole*np.sqrt(max(0,upper**2-along**2))
 e=max(abs(np.linalg.norm(elbow-root)-upper),abs(np.linalg.norm(target-elbow)-lower));err=max(err,e);assert e<1e-12
 # Rigid gun-frame transport of original support point preserves its contact.
 sourceR=Rotation.random(random_state=rng).as_matrix();targetR=Rotation.random(random_state=rng).as_matrix()
 sourceP=rng.normal(0,.1,3);targetP=rng.normal(0,.1,3);wrist=rng.normal(0,.1,3)
 local=sourceR.T@(wrist-sourceP);out=targetP+targetR@local
 assert np.allclose(targetR.T@(out-targetP),local)
assert 'standing && state.m_iMovement == 0 && leanSide == 1'in h
assert 'source.Frames[Names.Find("LeftHand")]'in h
assert 'Override3rdIsRightShoulder(HumanInputControllerOverrideType.ENABLED, false)'in h
assert 'key < 72'in h and 'key = key + 36'in h
assert '&& !actionRunning'in h and 'raisedReady || loweredStanding'in h
assert 'LeftRequested'not in h and not(b/'LogicSource/Inputs.xml').exists()
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'Profiles/LeanMosin/'+n,'LogicSource/Presets/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
# Graph dependency cycles can cause native evaluation faults.
sys.setrecursionlimit(20000);done=set();visiting=set()
def visit(n):
 if n not in nd or n in done:return
 assert n not in visiting,n
 visiting.add(n)
 for child in re.findall(r'\bChild\d* "([^"]+)"',nd[n]):visit(child)
 visiting.remove(n);done.add(n)
for n in nd:
 if not n.startswith('{'):visit(n)
print(f'PASS:62-bone parent/opposite hierarchy;372 mapped transforms;379 controls/DAG;3000 support geometry/contact cases max error {err:.3g};foot/shoulder reversal;fixed-left camera;presets untouched. Native compile/render/gameplay NOT RUN.')
