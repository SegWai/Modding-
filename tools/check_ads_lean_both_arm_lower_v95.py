"""Verify left captured solve, unchanged v94 right side and shared comparison."""
from pathlib import Path
import re,json,math
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v94';b=base/'MovementLab_ADS_Lean_Mosin_v95'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((b/'Both-Arms-Lower-v95.json').read_text());solve=json.loads((b/'Left-Arm-Rotation-Solve-v95.json').read_text())
changed={n for n in old if not n.startswith('{') and old[n]!=new[n]};assert changed==set(spec['left_changed_nodes']) and len(changed)==18
assert old.keys()==new.keys()
for name,node in old.items():
 if name.startswith('ML39_RightMovingLower_'):assert new[name]==node
parents=solve['parents'];corrections={n:{'rotation_xyz':solve['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in parents};result=bridge.reconstruct(solve['base'],parents,corrections)
for hand in ('LeftHand','RightHand'):
 np.testing.assert_allclose(np.array(result[hand])[:3,3]-np.array(solve['previous_desired'][hand])[:3,3],[0,-.12,0],atol=1e-8)
 np.testing.assert_allclose(np.array(result[hand])[:3,:3],np.array(solve['previous_desired'][hand])[:3,:3],atol=1e-8)
for n,p in parents.items():
 np.testing.assert_allclose(result[n],solve['desired'][n],atol=1e-8)
 if p:
  d1=math.dist([result[n][i][3] for i in range(3)],[result[p][i][3] for i in range(3)])
  d0=math.dist([solve['base'][n][i][3] for i in range(3)],[solve['base'][p][i][3] for i in range(3)])
  assert abs(d1-d0)<1e-8
for n in ('Head','Spine','Spine1','Spine2','Spine3','LeftShoulder','RightShoulder','Pelvis','LeftFoot','RightFoot'):
 np.testing.assert_allclose(result[n],solve['previous_desired'][n],atol=1e-8)
def clamp(x,lo,hi):return max(lo,min(hi,x))
for name in changed:
 prev=old[name];expr=re.search(r'Expression "([^"]+)"',new[name])[1];scope=re.search(r'Expression "([^"]+)"',prev)[1];oldamt=float(re.search(r'Amount ([-\d.eE]+)',prev)[1]);bone,axis=name.removeprefix('ML32_ReferenceHold_').rsplit('_',1);want=-solve['rotation_corrections'][bone]['XYZ'.index(axis)]
 env=dict(clamp=clamp,MLADSLeanAmount=-1,MLADSLeanGate=1,MLADSLeanMoveBlend=1,MLADSLeanWeaponShift=1,Stance=0,ML87FirstPersonCrouchLean=0,ML93ArmDrop=1)
 assert abs(eval(expr,{'__builtins__':{}},env)-want)<1e-12
 for key,val in [('ML93ArmDrop',0),('Stance',1),('ML87FirstPersonCrouchLean',1)]:
  e=env.copy();e[key]=val
  assert abs(eval(expr,{'__builtins__':{}},e)-oldamt*eval(scope,{'__builtins__':{}},e))<1e-12
cam='LogicSource/Scripts/4_World/MLADSLeanCamera.c';assert (a/cam).read_text().replace('MLCAM94','MLCAM95')==(b/cam).read_text()
keys=(b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();assert 'KC_F8 && m_ML71ControlDown' in keys and 'left/right moving lean' in keys
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'Math.AbsFloat(m_MLADSLeanAmount) < 0.98' in player
print('PASS: left target additional 12cm matches right target amount; v94 right unchanged; hand rotations/lengths/body preserved on reference; OFF/first-person/crouch restore original left values. Native left visual result pending.')
