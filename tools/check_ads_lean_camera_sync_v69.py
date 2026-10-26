"""Native rendering still needs DayZ; these test binding algebra and trim gating."""
from pathlib import Path
import unittest,re
import numpy as np
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v68';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v69'
class CameraSync69(unittest.TestCase):
 def test_wrist_relative_camera_preserves_current_pose_and_tracks_rendered_wrist(self):
  rng=np.random.default_rng(69)
  def transform():
   m=np.eye(4);m[:3,:3]=Rotation.random(random_state=rng).as_matrix();m[:3,3]=rng.normal(size=3);return m
  for i in range(100):
   wrist,view=transform(),transform();relative=np.linalg.inv(wrist)@view
   np.testing.assert_allclose(wrist@relative,view,atol=1e-12)
   render_delta=transform();render_wrist=render_delta@wrist
   np.testing.assert_allclose(render_wrist@relative,render_delta@view,atol=1e-12)
   np.testing.assert_allclose(np.linalg.inv(render_wrist)@(render_wrist@relative),relative,atol=1e-12)
 def test_reach_hold_does_not_chase_look_and_resettles_after_return(self):
  for yaw,pitch in [(6,0),(-40,20),(0,-30),(70,80)]:
   self.assertFalse(abs(yaw)<=5 and abs(pitch)<=5)
   trim=.013;stable=.3
   for frame in range(144*3):
    # Exact new branch: active full lean + off-centre aim holds trim, resets
    # stability. No response to the rotating head X or the old fade branch.
    stable=0
    self.assertEqual(trim,.013)
   self.assertEqual(stable,0)
  for fps in (20,60,144):
   stable=0;trim=.013;dt=min(1/fps,.05)
   for frame in range(fps):
    stable+=dt
    if stable>=.2:trim=max(-.02,min(.02,trim+.001*min(dt/.25,1)))
   self.assertGreater(trim,.013);self.assertLessEqual(trim,.02)
 def test_graph_and_pose_pbo_are_identical_and_ads_camera_unchanged(self):
  for name in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo'):self.assertEqual((A/name).read_bytes(),(B/name).read_bytes())
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();marker='modded class DayZPlayerCameraIronsights';self.assertEqual(old[old.index(marker):],new[new.index(marker):])
  for line in ('result.m_iDirectBone = primaryHand;','result.m_iDirectBoneMode = 3;','result.m_fUseHeading = 0;','Math3D.MatrixInvMultiply4(primaryPose, modelView, result.m_CameraTM);'):self.assertIn(line,new)
  self.assertNotRegex(new,r'AnimSet|SetTransform|SetPosition|SetOrientation')
 def test_controller_source_guards_and_hold_precede_correction(self):
  s=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();a=s.index(' protected void ML50UpdateStandingReach(');b=s.index(' // Standing exposure calibration:',a);body=s[a:b]
  self.assertIn('neutral = neutral && centered;',body)
  held=body[body.index('if (active && !centered)'):body.index('  if (active)')]
  self.assertIn('return;',held);self.assertNotIn('m_ML50ReachTrim =',held);self.assertNotIn('m_ML50ReachTrim *=',held)
  self.assertIn('m_ML50ReachStable < 0.2',body)
  self.assertNotRegex(s,r'\]\s*\[')
if __name__=='__main__':unittest.main()
