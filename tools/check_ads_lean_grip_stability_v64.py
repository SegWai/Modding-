"""Regression checks for v63 feedback windup; not native DayZ validation."""
from pathlib import Path
import unittest,re,math
import numpy as np
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v63';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v64'
class Stability64(unittest.TestCase):
 def test_wrist_feedback_removed(self):
  s=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();s=s[s.index(' protected void ML60UpdateGrip'):s.index(' // Read-only camera weight,')]
  self.assertNotRegex(s,r'MatrixToQuat|QuatLerp|QuatToMatrix|wantedRotation|MatrixToAngles')
  for i in range(3):self.assertIn(f'AnimSetFloat(m_ML60GripVars[{i}], 0);',s)
  self.assertIn('wantedShift.Normalized() * 0.12',s);self.assertIn('if (requestedWeight < 0.001)',s)
 def test_bounded_translation_with_pose_motion_and_lean_reversals(self):
  for fps in (20,30,60,144):
   shift=np.zeros(3);prev_weight=0;peak=0
   for frame in range(fps*12):
    t=frame/fps;base=np.array([.04*math.sin(t*3),1.4+.03*math.cos(t),.3]);target=base+np.array([.06*math.sin(t*2),.04*math.cos(t*2),.02])
    weight=abs(math.sin(t*2));observed=base+shift*prev_weight
    estimated_base=observed-shift*prev_weight;wanted=target-estimated_base
    if np.linalg.norm(wanted)>.12:wanted=wanted/np.linalg.norm(wanted)*.12
    alpha=min(min(1/fps,.05)*20,.5);shift+=(wanted-shift)*alpha
    if weight<.001:shift=np.zeros(3)
    self.assertLessEqual(np.linalg.norm(shift),.1200001);prev_weight=weight;peak=max(peak,np.linalg.norm(shift))
   self.assertLess(peak,.08)
 def test_graph_and_approved_alignment_preserved(self):
  for name in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo'):self.assertEqual((A/name).read_bytes(),(B/name).read_bytes())
  s=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();self.assertIn('m_ML58EyeCorrection = targetCorrection;',s);self.assertNotIn('(targetCorrection - m_ML58EyeCorrection) * alpha',s)
  marker='modded class DayZPlayerCameraIronsights';old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();self.assertEqual(old[old.index(marker):],s[s.index(marker):])
  self.assertIn('Math3D.MatrixMultiply4(weaponMS, m_ML59ReferenceView, desiredView)',s)
if __name__=='__main__':unittest.main()
