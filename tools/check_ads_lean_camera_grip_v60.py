"""Offline target/capture/restore invariants; not native DayZ IK validation."""
from pathlib import Path
import unittest,re
import numpy as np
from scipy.spatial.transform import Rotation
from dayz_graph_formats import newnodes
R=Path(__file__).resolve().parents[1];B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v60';A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v59'
class Grip60(unittest.TestCase):
 def test_target_capture_restore_chain_preserves_solver_input(self):
  n=newnodes((B/'WorkspaceSource/locomotion.agf').read_text());child='ML51_StandingLeftElbowOnly'
  for op,axes in [('Rotate','ZXY'),('Translate','XYZ')]:
   for axis in axes:
    name=f'ML60_Hand_{op}_{axis}';self.assertIn(f'Child "{child}"',n[name]);child=name
  self.assertIn(f'Child "{child}"',n['ML60_CaptureSupportTarget']);child='ML60_CaptureSupportTarget'
  for op,axes in [('Translate','ZYX'),('Rotate','YXZ')]:
   for axis in axes:
    name=f'ML60_Restore_{op}_{axis}';self.assertIn(f'Child "{child}"',n[name]);self.assertIn('Amount -1',n[name]);child=name
  self.assertIn(f'Child "{child}"',n['ML60_SolveSupportArm'])
  rng=np.random.default_rng(60)
  for trial in range(100):
   old=Rotation.random(random_state=rng).as_matrix();point=rng.normal(size=3);angles=rng.uniform(-1,1,3);shift=rng.uniform(-.3,.3,3);rot=old.copy()
   for axis,i in [('z',2),('x',0),('y',1)]:rot=Rotation.from_euler(axis,angles[i]).as_matrix()@rot
   target=(rot.copy(),point+shift)
   point_restored=target[1]-shift
   for axis,i in [('y',1),('x',0),('z',2)]:rot=Rotation.from_euler(axis,-angles[i]).as_matrix()@rot
   np.testing.assert_allclose(rot,old,atol=1e-12);np.testing.assert_allclose(point_restored,point,atol=1e-12)
 def test_only_new_left_arm_branch_and_queue_routing_change(self):
  old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((B/'WorkspaceSource/locomotion.agf').read_text())
  for name in old:
   if name.startswith('{') or name=='MeleeBlockQ':continue
   self.assertEqual(old[name],new[name],name)
  for name,node in new.items():
   if name.startswith('ML60_') and 'AnimSrcNodeProcTransform' in node:self.assertIn('Bone "LeftHand"',node)
  self.assertIn('Child "ML60_VerticalGripOnly"',new['MeleeBlockQ'])
 def test_camera_model_space_and_ads_unchanged(self):
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();marker='modded class DayZPlayerCameraIronsights'
  self.assertEqual(old[old.index(marker):],new[new.index(marker):])
  self.assertIn('result.m_iDirectBone = -1;',new);self.assertIn('result.m_fPositionModelSpace = 1.0;',new);self.assertIn('result.m_CameraTM[3] = correctedEye;',new)
  self.assertNotRegex(new,r'AnimSet|SetPosition|SetTransform|SetOrientation')
 def test_weapon_relative_target_moves_with_pitch(self):
  relative=np.eye(4);relative[:3,3]=[.06,-.05,.25]
  for side in (-1,1):
   for pitch in (-80,-40,0,40,80):
    weapon=np.eye(4);weapon[:3,:3]=Rotation.from_euler('xyz',[pitch,side*10,side*8],degrees=True).as_matrix();weapon[:3,3]=[side*.3,1.4,.2]
    hand=weapon@relative
    np.testing.assert_allclose(np.linalg.inv(weapon)@hand,relative,atol=1e-12)
if __name__=='__main__':unittest.main()
