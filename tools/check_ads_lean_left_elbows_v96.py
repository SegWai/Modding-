"""Check elbow target geometry, fixed wrists, post-grip graph and scopes."""
from pathlib import Path
import re,json,math
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v95';b=base/'MovementLab_ADS_Lean_Mosin_v96'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(95|96)\]',r'[\g<1>VERSION]',s.replace('v95','vVERSION').replace('v96','vVERSION'))
for p in (a/'LogicSource').rglob('*'):
 if p.is_file():assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((b/'Left-Elbows-v96.json').read_text());solve=json.loads((b/'Left-Elbows-Solve-v96.json').read_text())
for name,node in old.items():
 expected=node.replace('Child "ML88_LoweredRaisedOnly"','Child "ML96_LeftMovingElbowsOnly"') if name=='MeleeBlockQ' else node
 assert new[name]==expected,name
assert 'Child "ML88_LoweredRaisedOnly"' in new['ML96_CaptureHands']
assert 'Child "ML96_LeftMoving_LeftArm_Z"' in new['ML96_RestoreHands']
assert 'Child "ML96_RestoreHands"' in new['ML96_PublishElbowHold']
for bone,angles in spec['upper_arm_delta_math_xyz'].items():
 for axis,angle in zip('XYZ',angles):
  node=new['ML96_LeftMoving_'+bone+'_'+axis]
  assert 'Op Rotate' in node and 'Op Translate' not in node
  assert abs(float(re.search(r'Amount ([-\d.eE]+)',node)[1])+angle)<1e-12
# Exact reference elbow Y shifts, wrist transforms and other-body invariants.
parents=solve['parents'];out=bridge.reconstruct(solve['base'],parents,{n:{'rotation_xyz':solve['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in parents})
for side,shift in [('Right',.05),('Left',-.07)]:
 assert abs(out[side+'ForeArm'][1][3]-solve['previous_desired'][side+'ForeArm'][1][3]-shift)<1e-8
 np.testing.assert_allclose(out[side+'Hand'],solve['previous_desired'][side+'Hand'],atol=1e-8)
for n in ('Head','Pelvis','Spine','Spine1','Spine2','Spine3','LeftShoulder','RightShoulder','LeftFoot','RightFoot'):
 np.testing.assert_allclose(out[n],solve['previous_desired'][n],atol=1e-8)
for n,p in parents.items():
 if p:
  before=math.dist([solve['previous_desired'][n][i][3] for i in range(3)],[solve['previous_desired'][p][i][3] for i in range(3)])
  after=math.dist([out[n][i][3] for i in range(3)],[out[p][i][3] for i in range(3)])
  assert abs(before-after)<1e-8
def clamp(x,lo,hi):return max(lo,min(hi,x))
env=dict(clamp=clamp,MLADSLeanAmount=-1,MLADSLeanGate=1,MLADSLeanMoveBlend=1,MLADSLeanWeaponShift=1,Stance=0,ML87FirstPersonCrouchLean=0,ML93ArmDrop=1)
assert eval(spec['weight'],{'__builtins__':{}},env)==1
for key,value in [('MLADSLeanAmount',1),('MLADSLeanMoveBlend',0),('Stance',1),('ML87FirstPersonCrouchLean',1),('ML93ArmDrop',0)]:
 e=env.copy();e[key]=value;assert eval(spec['weight'],{'__builtins__':{}},e)==0
agr=(b/'WorkspaceSource/player_main.agr').read_text()
for name in ('ML96_CaptureHands','ML96_RestoreHands'):
 for chain in re.findall(r'IkChain "([^"]+)"',new[name]):assert chain in agr
print('PASS: reference elbows +5cm right/-7cm left, hands/orientations/lengths/body fixed; only new post-grip left-moving branch, original right and scripts preserved. Native IK visual placement unverified.')
