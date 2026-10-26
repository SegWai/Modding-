"""Ensure failed post-grip solver is gone and only existing arm rotations differ."""
from pathlib import Path
import re,json
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v95';b=base/'MovementLab_ADS_Lean_Mosin_v98'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((b/'Left-Arm-Retry-v98.json').read_text());solve=json.loads((b/'Left-Arm-Solve-v98.json').read_text())
assert old.keys()==new.keys()
assert not any(n.startswith(('ML96_','ML97_')) for n in new)
assert {n for n in old if old[n]!=new[n]}==set(spec['changed_nodes']) and len(spec['changed_nodes'])==18
for name,node in old.items():
 if not name.startswith('ML32_ReferenceHold_'):assert node==new[name]
def clamp(x,lo,hi):return max(lo,min(hi,x))
original89=newnodes((base/'MovementLab_ADS_Lean_Mosin_v89/WorkspaceSource/locomotion.agf').read_text())
for name in spec['changed_nodes']:
 expr=re.search(r'Expression "([^"]+)"',new[name])[1];before=original89[name];oldamt=float(re.search(r'Amount ([-\d.eE]+)',before)[1]);scope=re.search(r'Expression "([^"]+)"',before)[1]
 env=dict(clamp=clamp,MLADSLeanAmount=-1,MLADSLeanGate=1,MLADSLeanMoveBlend=1,MLADSLeanWeaponShift=1,Stance=0,ML87FirstPersonCrouchLean=0,ML93ArmDrop=1)
 bone,axis=name.removeprefix('ML32_ReferenceHold_').rsplit('_',1)
 assert abs(eval(expr,{'__builtins__':{}},env)+solve['rotation_corrections'][bone]['XYZ'.index(axis)])<1e-12
 for key,val in [('ML93ArmDrop',0),('ML87FirstPersonCrouchLean',1),('Stance',1)]:
  e=env.copy();e[key]=val;assert abs(eval(expr,{'__builtins__':{}},e)-oldamt*eval(scope,{'__builtins__':{}},e))<1e-12
replay=bridge.reconstruct(solve['base'],solve['parents'],{n:{'rotation_xyz':solve['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in solve['parents']})
for n in replay:np.testing.assert_allclose(replay[n],solve['desired'][n],atol=1e-8)
cam='LogicSource/Scripts/4_World/MLADSLeanCamera.c';assert (a/cam).read_text().replace('MLCAM95','MLCAM98')==(b/cam).read_text()
assert 'KC_F8 && m_ML71ControlDown' in (b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
print('PASS: v95 graph topology/native IK restored; only existing left 18 arm rotations changed; OFF/first-person/crouch keep baseline; right hold and camera unchanged. Native elbow shape unverified.')
