"""Bounded roll-response calibration and cached weapon-local support reach math."""
from pathlib import Path
import sys,re,math
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v5';b=a.with_name('MovementLab_Ambidextrous_Lean_v6');w=b/'LogicSource/Scripts/4_World'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());added={n for n in set(new)-set(old)if not n.startswith('{')};assert added=={'MLASwapSupport'+str(i)for i in range(9)}
for n,v in old.items():
 if n.startswith('{'):continue
 if n=='MLASwapBeforeAim':assert new[n]==v.replace('Child1 "MLASwapPose299"','Child1 "MLASwapSupport8"')
 elif n=='MLASwapLeftWeapon':
  expr=re.search(r'WeaponRoll "([^"]+)"',v)[1];assert new[n]==v.replace('WeaponRoll "'+expr+'"','WeaponRoll "('+expr+')+MLASwapGripRoll"')
 else:assert new[n]==v,n
for i,n in enumerate(sorted(added)):
 node=new[n];assert 'Space Model'in node and 'Op Rotate'in node
agr=(b/'WorkspaceSource/player_main.agr').read_text();ids=re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr);assert len(ids)==len(set(ids))
assert len([n for n in ids if n.startswith('MLASwap')])==311
# Probed native roll direction may be positive OR negative; recover the same
# desired camera-up orientation without hardcoding +/-90 or convention.
def rollangle(u,v,f):
 u=u-f*np.dot(u,f);v=v-f*np.dot(v,f);u/=np.linalg.norm(u);v/=np.linalg.norm(v);return math.degrees(math.atan2(f@np.cross(u,v),np.clip(u@v,-1,1)))
f=np.array([0.,0.,1]);u=np.array([0.,1.,0]);cases=0;maxerr=0
for base in [-170,-120,-90,-45,0,45,90,120,170]:
 for native_sign in [-1,1]:
  for scale in [.5,1,1.5]:
   R=lambda deg:Rotation.from_rotvec(f*math.radians(deg)).as_matrix()
   baseup=R(base)@u;probe=R(base+native_sign*scale*5)@u;response=rollangle(baseup,probe,f);error=rollangle(baseup,u,f);correction=5*error/response
   if abs(correction)>180:continue
   final=R(base+native_sign*scale*correction)@u;err=float(np.linalg.norm(final-u));maxerr=max(maxerr,err);assert err<1e-12;cases+=1
# Weapon-local support target follows gun rigidly; never a guessed model XYZ.
rng=np.random.default_rng(6)
for _ in range(300):
 sr=Rotation.random(random_state=rng).as_matrix();p=rng.normal(0,.2,3);hand=rng.normal(0,.2,3);local=sr.T@(hand-p)
 R=Rotation.random(random_state=rng).as_matrix();t=rng.normal(0,.1,3);gunR=R@sr;gunP=R@p+t;target=gunP+gunR@local
 assert np.allclose(target,R@hand+t,atol=1e-12)
# Four monotonic phases finish; finished entries never re-probe/solve; aim
# movement pauses time rather than invalidating an original arm reference.
for fps in [30,60,144]:
 stage=0;timer=0;transitions=[]
 for frame in range(fps*5):
  if stage>=4:continue
  timer+=min(1/fps,.05)
  if timer>=.25:timer=0;transitions.append(stage);stage+=1
 assert transitions==[0,1,2,3]and stage==4
h=(w/'MLAShoulderPose.c').read_text();start=h.index(' void AlignGrip(');end=h.index(' void Update(',start);align=h[start:end]
assert 'Capture(actor)'not in align and 'Cache['not in align
assert 'solution.AlignmentStage >= 4'in align and 'magnitude > 0.5 && magnitude < 12 && forwardAgreement > 0.995'in align
assert 'solution.GripRoll = 5;'in align and 'Math.Clamp(5.0 * error / response, -180, 180)'in align
support=h[h.index(' void SolveSupport('):start];assert support.count('ML144Math.Limb(')==1 and 'actualGun.Orientation.Apply(solution.SupportGunLocal)'in support
assert 'keepWristOrientation = new ML144Rot'in support
for name in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [name,'Profiles/LeanMosin/'+name,'LogicSource/Presets/'+name]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['Missions/MLADSLeanMosin.ChernarusPlus/init.c','LogicSource/Inputs.xml']:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert not re.search(r'\w+\[[^\]]+\]\s*(?:\+\+|--)',h)
# No cycles/dangling new node children; all gates still binary single-path.
sys.setrecursionlimit(20000);done=set();visiting=set()
def visit(n):
 if n not in new or n in done:return
 assert n not in visiting,n
 visiting.add(n)
 for child in re.findall(r'\bChild\d* "([^"]+)"',new[n]):visit(child)
 visiting.remove(n);done.add(n)
for n in new:
 if not n.startswith('{'):visit(n)
print('PASS:',cases,'roll convention cases, maxerror',maxerr,';300 rigid support-target cases;bounded4stage lifecycle;9nodes/10vars, canonical banks/input/scene unchanged. Native grip calibration/visuals NOT RUN.')
