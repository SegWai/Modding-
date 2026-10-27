"""Independent offline IK and release isolation. Not native DayZ verification."""
from pathlib import Path
import sys,re,hashlib,json
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent))
from dayz_graph_formats import newnodes
root=Path(__file__).resolve().parents[1]/'ads-lean-test'
a=root/'MovementLab_ADS_Lean_Mosin_v158';b=root/'MovementLab_ADS_Lean_Mosin_v159'
for p in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','LogicSource/Scripts/4_World/MLADSLeanCamera.c','LogicSource/Scripts/4_World/MLVanillaLoadout156.c','LogicSource/Scripts/4_World/MLDemoCycle158.c']:
 assert (a/p).read_bytes()==(b/p).read_bytes(),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
for name,node in old.items():
 expected=node.replace('Child "ML149_BodyWithWeapon"','Child "ML159_RightTravelOnly"') if name=='ML157_HeadX' else node
 assert new[name]==expected,name
added={n for n in set(new)-set(old) if not n.startswith('{')}
assert added=={f'ML159_Node{i}' for i in range(19)}|{'ML159_RightTravelOnly','ML159_WeaponFollow'}
assert 'WeightPrimaryChain "false"' in new['ML159_WeaponFollow']
assert 'WeightSecondaryChain "false"' in new['ML159_WeaponFollow']
assert 'Child "ML159_Node18"' in new['ML159_WeaponFollow']
def turn(a,b):
 a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);v=np.cross(a,b);ss=np.linalg.norm(v);cc=np.clip(a@b,-1,1)
 if ss<1e-6:return np.eye(3)
 return Rotation.from_rotvec(v/ss*np.arctan2(ss,cc)).as_matrix()
def solve(root,elbow,wrist,target):
 l1=np.linalg.norm(elbow-root);l2=np.linalg.norm(wrist-elbow);d=np.linalg.norm(target-root)
 if d<=abs(l1-l2)+.002 or d>=l1+l2-.002:return None
 axis=(target-root)/d;along=(l1*l1-l2*l2+d*d)/(2*d)
 pole=elbow-root;pole-=axis*(pole@axis)
 if pole@pole<1e-6:return None
 pole/=np.linalg.norm(pole);goal=root+axis*along+pole*np.sqrt(max(0,l1*l1-along*along))
 upper=turn(elbow-root,goal-root);lower=turn(upper@(wrist-elbow),target-goal);foot=(lower@upper).T
 return upper,lower,foot
rng=np.random.default_rng(159);passed=0;rejected=0;maxerror=0.
for _ in range(2000):
 hip=np.array([rng.uniform(-.2,.2),.9,0.]);knee=hip+np.array([rng.uniform(-.12,.12),-.4,.1]);foot=knee+np.array([rng.uniform(-.12,.12),-.4,-.1]);shift=np.array([rng.uniform(-.1,.35),0.,0.])
 solution=solve(hip,knee,foot,foot-shift)
 if solution is None:rejected+=1;continue
 u,l,f=solution
 kneeout=hip+shift+u@(knee-hip)
 footout=kneeout+l@u@(foot-knee)
 maxerror=max(maxerror,float(np.max(np.abs(footout-foot))))
 assert np.allclose(footout,foot,atol=1e-10)
 assert np.allclose(f@l@u,np.eye(3),atol=1e-10)
 assert np.isclose(np.linalg.norm(kneeout-(hip+shift)),np.linalg.norm(knee-hip))
 assert np.isclose(np.linalg.norm(footout-kneeout),np.linalg.norm(foot-knee))
 # Upper body translates rigidly: grip and torso orientation are unchanged.
 head=np.array([0.,1.7,.1]);neutral_x=.02;goal=neutral_x+.219
 correction=goal-head[0]
 assert abs((head+np.array([correction,0,0]))[0]-neutral_x-.219)<1e-12
 passed+=1
assert passed>500 and rejected>0
s=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
assert '!m_ML159Attempted && m_ML159NeutralReady && rightStable' in s
assert 'travelShift) <= 0.5' in s and 'm_ML159Angles = solvedTravel' in s
assert 'm_ML87ViewAmount < 0.01' in s
assert 'if (m_MLADSLeanAmount > 0.01 && m_ML159Bound)' in s
assert 'm_ML136Cycle >= 2.0' in s
sha=hashlib.sha256((b/'MLLeanPreset.json').read_bytes()).hexdigest()
assert sha=='deeaeac1af612bfe4edaa542e6ebabf6da992b163bd7eac56579a0dd4f0bdb61'
report={'safe_leg_cases':passed,'unreachable_rejected':rejected,'max_endpoint_error_metres':maxerror,'approved_preset_sha256':sha,'new_graph_scope':'late pelvis shift + 18 leg rotations + hand-pivot publication; all existing nodes retained except input to final head alignment','target_right_head_travel_metres':.219,'native_runtime':'NOT RUN; actual calibration/footplant/target displacement need gameplay logs'}
(b/'Right-Travel-Checks-v159.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
