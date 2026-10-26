"""Captured-reference rotation solve and reversible native test path checks."""
from pathlib import Path
import re,json,math
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v89';b=base/'MovementLab_ADS_Lean_Mosin_v94'
spec=json.loads((b/'Arm-Drop-Test-v94.json').read_text());solve=json.loads((b/'Arm-Rotation-Solve-v94.json').read_text());parents=solve['parents']
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());changed={n for n in old if not n.startswith('{') and old[n]!=new[n]}
assert changed==set(spec['changed_existing_nodes']) and len(changed)==18
assert old.keys()==new.keys()
def clamp(x,lo,hi):return max(lo,min(hi,x))
for name in changed:
 prev=old[name];now=new[name];assert 'Op Rotate' in now and 'Op Translate' not in now
 oldamt=float(re.search(r'Amount ([-\d.eE]+)',prev)[1]);expr=re.search(r'Expression "([^"]+)"',now)[1]
 bone,axis=name.removeprefix('ML39_RightMovingLower_').rsplit('_',1);wanted=-solve['rotation_corrections'][bone]['XYZ'.index(axis)]
 for mode in (0,1):
  env=dict(clamp=clamp,MLADSLeanAmount=1,MLADSLeanGate=1,MLADSLeanMoveBlend=1,MLADSLeanWeaponShift=1,Stance=0,ML87FirstPersonCrouchLean=0,ML93ArmDrop=mode)
  value=eval(expr,{'__builtins__':{}},env);assert abs(value-(wanted if mode else oldamt))<1e-12
  for key,val in [('MLADSLeanAmount',-1),('MLADSLeanMoveBlend',0),('Stance',1),('ML87FirstPersonCrouchLean',1)]:
   e=env.copy();e[key]=val;assert abs(eval(expr,{'__builtins__':{}},e))<1e-12
corrections={n:{'rotation_xyz':solve['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in parents}
result=bridge.reconstruct(solve['base'],parents,corrections)
original39=json.loads((a/'Right-Moving-Lower-v39.json').read_text())
for n,p in parents.items():
 np.testing.assert_allclose(result[n],solve['desired'][n],atol=1e-8)
 if p:
  original=math.dist([solve['base'][n][i][3] for i in range(3)],[solve['base'][p][i][3] for i in range(3)])
  after=math.dist([result[n][i][3] for i in range(3)],[result[p][i][3] for i in range(3)])
  assert abs(original-after)<1e-8
for hand in ('LeftHand','RightHand'):
 np.testing.assert_allclose(np.array(result[hand])[:3,3]-np.array(original39['desired'][hand])[:3,3],[0,-.12,0],atol=1e-8)
 np.testing.assert_allclose(np.array(result[hand])[:3,:3],np.array(original39['desired'][hand])[:3,:3],atol=1e-8)
for n in ('Pelvis','Spine','Spine1','Spine2','Spine3','Head','LeftShoulder','RightShoulder','LeftFoot','RightFoot'):
 np.testing.assert_allclose(result[n],solve['base'][n],atol=1e-10)
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();keys=(b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();agr=(b/'WorkspaceSource/player_main.agr').read_text()
assert 'm_ML93DropVar >= 0' in player
for variable in ('m_ML87ViewVar','m_MLADSLeanGateVar','m_MLADSLeanAmountVar','m_ML71SupportVar'):assert 'm_ML93DropVar != '+variable in player
assert 'AnimSetFloat(m_ML93DropVar, mode)' in player
assert 'ML93UpdateArmProbe(pDt, state)' in player
assert 'KC_F8 && m_ML71ControlDown' in keys
assert 'Arm drop OFF: v89 arm rotations' in keys
assert 'MLDROP94' in player and 'control_bound=' in player
assert agr.count('AnimSrcGCTVarFloat ML93ArmDrop ')==1
cam='LogicSource/Scripts/4_World/MLADSLeanCamera.c'
assert (a/cam).read_text().replace('MLCAM89','MLCAM94')==(b/cam).read_text()
print('PASS: existing 18 rotation nodes only; OFF matches v89, ON solves additional 12cm on captured reference with lengths/orientation/body preserved; side/gait/view scope, toggle binding and telemetry checked. Native retention unverified.')
