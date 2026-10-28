"""Independent FK proof of minimum-swing elbow correction and graph isolation."""
from pathlib import Path
import json,re,sys,numpy as np,hashlib
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));from dayz_graph_formats import newnodes
base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v173';out=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v179'
rng=np.random.default_rng(179);maximum=0.;oldangles=[];newangles=[]
def turn(a,b):
 a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);cross=np.cross(a,b);s=np.linalg.norm(cross);c=np.clip(a@b,-1,1)
 if s<1e-9:return np.eye(3)
 return Rotation.from_rotvec(cross/s*np.arctan2(s,c)).as_matrix()
for _ in range(1000):
 root=rng.uniform(-1,1,3);axis=rng.normal(size=3);axis/=np.linalg.norm(axis)
 pole=rng.normal(size=3);pole-=axis*(axis@pole);pole/=np.linalg.norm(pole)
 distance=rng.uniform(.25,.45);along=distance*rng.uniform(.35,.65);radius=rng.uniform(.08,.22)
 elbow=root+axis*along+pole*radius;wrist=root+axis*distance
 phi=rng.uniform(-2.8,2.8);whole=Rotation.from_rotvec(axis*phi).as_matrix();goal=root+whole@(elbow-root)
 arm=turn(elbow-root,goal-root);lower=turn(arm@(wrist-elbow),wrist-goal);hand=(lower@arm).T
 actual_elbow=root+arm@(elbow-root);actual_wrist=actual_elbow+lower@arm@(wrist-elbow)
 err=max(np.max(abs(actual_elbow-goal)),np.max(abs(actual_wrist-wrist)),np.max(abs(hand@lower@arm-np.eye(3))))
 assert err<1e-10;maximum=max(maximum,float(err))
 # Rotation axis orthogonal to original upper bone: no added axial winding.
 rotvec=Rotation.from_matrix(arm).as_rotvec();old_upper=elbow-root;old_upper/=np.linalg.norm(old_upper)
 assert abs(rotvec@old_upper)<1e-9
 assert np.linalg.norm(rotvec)<=abs(phi)+1e-9
 oldangles.append(abs(phi));newangles.append(np.linalg.norm(rotvec))
 # Native sign convention conversion roundtrip.
 for matrix in [arm,lower,hand]:
  native=-Rotation.from_matrix(matrix).as_euler('xyz');assert np.max(abs(Rotation.from_euler('xyz',-native).as_matrix()-matrix))<1e-10
n0=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());n1=newnodes((out/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((out/'Minimum-Twist-v179.json').read_text());added={k for k in set(n1)-set(n0) if not k.startswith('{')}
assert len(added)==9
for name in added:
 node=n1[name];assert 'Bone "LeftForeArm"' in node and 'Space Model' in node and 'Op Rotate' in node
 assert 'ML173WalkingPreview' in node
for name,old in n0.items():
 if name in spec['chains']:
  expected=re.sub(r'Child "[^"]+"','Child "'+spec['chains'][name]+'"',old,count=1)
  assert n1[name]==expected
 else:assert n1[name]==old,name
# Both non-preview actors see zero added forearm rotation and unchanged solver.
source=(out/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
assert 'if (m_ML173Walking && m_ML179Bound)\n     leftOK = ML179ArmSwing.Pole' in source
assert 'else\n     leftOK = MLArmPoleMath104.Swivel' in source
assert 'if (m_ML173Walking && m_ML179Bound)\n    leftSolved = ML179ArmSwing.Editor' in source
assert 'else\n    leftSolved = ML146ArmMath.Swivel' in source
assert 'if (m_ML173Walking && leanSide == 0 && !m_ML104PoleReady && m_ML104CalibAttempts < 3)' in source
assert 'm_ML174' not in source
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
 assert (base/rel).read_bytes()==(out/rel).read_bytes()
for rel in ['MLWalkingLeanPreset.json','LogicSource/Presets/MLWalkingLeanPreset.json','Profiles/LeanMosin/MLWalkingLeanPreset.json']:
 assert hashlib.sha256((out/rel).read_bytes()).hexdigest()=='fc02c504287f1895891b01e40f7dffebb230eb3da605c88b887c7534c79921d0'
 assert json.loads((out/rel).read_bytes())['PresetVersion']==1
# No v174 zero schema or later IK override is restored.
assert not (out/'LogicSource/Scripts/4_World/MLArmZero174.c').exists()
assert n1['ML166_PublishFinalAimedWeapon']==n0['ML166_PublishFinalAimedWeapon']
helper=(out/'LogicSource/Scripts/4_World/MLArmSwing179.c').read_text()
for x in ['armTurn = ML144Math.Turn(oldUpper, newUpper)','foreTurn = ML144Math.Turn(inheritedLower, desiredLower)','handTurn = combined.Inverse()']:assert x in helper
for p in (out/'LogicSource/Scripts').rglob('*.c'):
 assert not re.search(r'\]\s*(\+\+|--)|(\+\+|--)\s*[A-Za-z_]\w*\[',p.read_text())
 stripped=re.sub(r'//[^\n]*|"(?:\\.|[^"\\])*"','',p.read_text());assert stripped.count('{')==stripped.count('}')
result={'random_elbow_targets':1000,'max_joint_and_palm_matrix_error':maximum,'mean_old_whole_arm_rotation_degrees':float(np.mean(oldangles)*180/np.pi),'mean_new_shoulder_swing_degrees':float(np.mean(newangles)*180/np.pi),'added_upper_arm_axial_component':0,'new_forearm_nodes':9,'new_controls':6,'uploaded_absolute_walking_preset_unchanged':True,'native_compile_mesh_and_gait':'NOT RUN'}
(out/'Minimum-Twist-Checks-v179.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
