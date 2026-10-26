from pathlib import Path
import json,re,math
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v94';b=base/'MovementLab_ADS_Lean_Mosin_v99'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((b/'Left-Elbow-Test-v99.json').read_text());d=json.loads((b/'Left-Elbow-25-v99.json').read_text())
assert old.keys()==new.keys();assert {n for n in old if not n.startswith('{') and old[n]!=new[n]}==set(spec['changed_nodes']) and len(spec['changed_nodes'])==9
assert all(n.startswith(('ML32_ReferenceHold_LeftArm_','ML32_ReferenceHold_LeftForeArm_','ML32_ReferenceHold_LeftHand_')) for n in spec['changed_nodes'])
assert abs(d['bend_plane_degrees'])==25 and d['left_elbow_delta_xyz_m'][1]<0
result=bridge.reconstruct(d['base'],d['parents'],{n:{'rotation_xyz':d['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in d['parents']})
for n in result:np.testing.assert_allclose(result[n],d['desired'][n],atol=1e-8)
for n in ('LeftHand','RightHand','RightArm','RightForeArm','Pelvis','Spine','Spine1','Spine2','Spine3','Head','LeftShoulder','RightShoulder','LeftFoot','RightFoot'):
 np.testing.assert_allclose(result[n],d['previous_desired'][n],atol=1e-8)
for n,p in d['parents'].items():
 if p:
  before=np.linalg.norm(np.array(d['previous_desired'][n])[:3,3]-np.array(d['previous_desired'][p])[:3,3]);after=np.linalg.norm(np.array(result[n])[:3,3]-np.array(result[p])[:3,3]);assert abs(before-after)<1e-8
for n in spec['changed_nodes']:
 assert '*ML93ArmDrop*(1.0-clamp(Stance, 0.0, 1.0))*(1.0-ML87FirstPersonCrouchLean)' in new[n]
cam='LogicSource/Scripts/4_World/MLADSLeanCamera.c';assert (a/cam).read_text().replace('MLCAM94','MLCAM99')==(b/cam).read_text()
assert 'KC_F8 && m_ML71ControlDown' in (b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
print('PASS: v94 baseline, left-only 25deg bend-plane rotation with fixed wrist/gun targets and preserved lengths; right graph unchanged; no extra overlay, camera unchanged. Native visual rotation unverified.')
