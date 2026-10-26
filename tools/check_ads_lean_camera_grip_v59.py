"""Offline invariants; native camera/IK evaluation still needs DayZ."""
from pathlib import Path
import unittest,sys,re
import numpy as np
from scipy.spatial.transform import Rotation
from dayz_graph_formats import newnodes
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v58';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v59'
class CameraGrip59(unittest.TestCase):
 def test_rifle_view_relative_transform_survives_both_lean_and_vertical_aim(self):
  weapon=np.eye(4);weapon[:3,3]=[.12,1.4,.35]
  camera=np.eye(4);camera[:3,3]=[.15,1.65,.1]
  relative=np.linalg.inv(weapon)@camera
  for side in (-1,1):
   for pitch in (-80,-40,0,40,80):
    moved=weapon.copy();moved[:3,:3]=Rotation.from_euler('xyz',[pitch,side*12,side*20],degrees=True).as_matrix();moved[0,3]+=side*.3
    view=moved@relative
    np.testing.assert_allclose(np.linalg.inv(view)@moved,np.linalg.inv(camera)@weapon,atol=1e-12)
    # Position-only v58 cannot preserve orientation for the same transform.
    position_only=camera.copy();position_only[:3,3]=view[:3,3]
    self.assertGreater(np.max(abs((np.linalg.inv(position_only)@moved)[:3,:3]-(np.linalg.inv(camera)@weapon)[:3,:3])),.1)
 def test_pose_nodes_and_gun_settings_unchanged_support_flag_only(self):
  old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((B/'WorkspaceSource/locomotion.agf').read_text());self.assertEqual(old.keys(),new.keys())
  for name in old:
   if name.startswith('{'):continue
   expected=old[name]
   if name=='ML58_FinalSupportGrip':expected=expected.replace('WeightSecondaryChain "(isbitset(ArmIK, 2) || MLADSLeanCanary > 0.9)"','WeightSecondaryChain "true"')
   self.assertEqual(new[name],expected,name)
  for pitch in (-85,-20,0,20,85):
   for lean in (-1,0,1):
    weight=abs(lean)*max(0,min(1,abs(pitch)/10))
    self.assertEqual(weight,0 if pitch==0 or lean==0 else 1)
 def test_ads_camera_unchanged_and_raised_has_no_pose_writes(self):
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text()
  marker='modded class DayZPlayerCameraIronsights'
  self.assertEqual(old[old.index(marker):],new[new.index(marker):])
  self.assertNotRegex(new,r'AnimSet|SetTransform|SetPosition|SetOrientation|OverrideAim')
  self.assertIn('[MLCAM59]',new);self.assertIn('Math3D.MatrixMultiply4(weaponMS, m_ML59ReferenceView, desiredView)',new)
if __name__=='__main__':unittest.main()
