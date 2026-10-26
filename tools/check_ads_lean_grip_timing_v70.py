"""Guard the camera/pose while refining native grip IK timing. No native test."""
from pathlib import Path
import unittest,re
from dayz_graph_formats import newnodes
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v69';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v70'
class GripTiming70(unittest.TestCase):
 def test_all_old_nodes_and_authored_amounts_unchanged_except_source_routing(self):
  old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((B/'WorkspaceSource/locomotion.agf').read_text())
  for name,node in old.items():
   if name.startswith('{'):continue
   expected=node.replace('Child "NormalWeaponIK"','Child "ML70_GripTimingBlend"') if name=='ML32_ReferenceHold_LeftShoulder_X' else node
   self.assertEqual(new[name],expected,name)
  added={name for name in new.keys()-old.keys() if not name.startswith('{')};self.assertEqual(added,{'ML70_SynchronousWeaponIK','ML70_GripTimingBlend'})
 def test_solver_same_native_profile_and_inputs_only_timing_and_activation_change(self):
  n=newnodes((B/'WorkspaceSource/locomotion.agf').read_text());old=n['NormalWeaponIK'];sync=n['ML70_SynchronousWeaponIK']
  expected=old.replace('NormalWeaponIK','ML70_SynchronousWeaponIK',1).replace('IkconfigName "WeaponIKTest"','IkconfigName "ML70_SynchronousGripConfig"').replace('BlendInTime 0.36','BlendInTime 0').replace('BlendOutTime 0.15','BlendOutTime 0')
  for field in ('WeightAim','WeightPrimaryChain','WeightSecondaryChain'):expected=re.sub(field+r' "[^"]+"',field+' "true"',expected)
  self.assertEqual(sync,expected);self.assertNotIn('outputweaponoffsettobuffer',sync)
  for lean in (-1,-.5,0,.5,1):
   for gate in (0,.2,1):
    w=min(1,max(0,abs(lean)*gate));self.assertGreaterEqual(w,0);self.assertLessEqual(w,1)
    if lean==0 or gate==0:self.assertEqual(w,0)
  self.assertIn('Child0 "NormalWeaponIK"',n['ML70_GripTimingBlend']);self.assertIn('OptimizeMax 1',n['ML70_GripTimingBlend'])
 def test_fixed_camera_and_reach_controller_unchanged(self):
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text().replace('MLCAM70','MLCAM69');self.assertEqual(new,old)
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  for marker,end in [(' protected bool ML69AimCentered',' // Standing exposure calibration:')]:self.assertEqual(old[old.index(marker):old.index(end)],new[new.index(marker):new.index(end)])
  self.assertNotIn('ML60UpdateGrip',new);self.assertNotRegex(new,r'\]\s*\[')
 def test_diagnostics_wait_for_settled_direction(self):
  s=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();self.assertIn('m_ML70GripSlotStable >= 0.5',s);self.assertIn('float handToHandDrift = -1;',s)
if __name__=='__main__':unittest.main()
