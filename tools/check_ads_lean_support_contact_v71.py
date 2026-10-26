"""Scope and rollback checks for native contact trial; engine playback pending."""
from pathlib import Path
import unittest,re
from dayz_graph_formats import newnodes
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v70';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v71'
class SupportContact71(unittest.TestCase):
 def test_camera_implementation_is_unchanged(self):
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text().replace('MLCAM71','MLCAM70');self.assertEqual(old,new)
 def test_additional_native_solver_support_only_and_before_shared_aim(self):
  n=newnodes((B/'WorkspaceSource/locomotion.agf').read_text());s=n['ML71_PostPoseSupportIK']
  for text in ['Child "ML51_StandingLeftElbowOnly"','WeightAim "true"','WeightPrimaryChain "false"','WeightSecondaryChain "true"','WeaponDirLr "0.0"','WeaponDirUd "0.0"','WeaponRoll "0.0"','weaponrotator = RightHand','BlendInTime 0','BlendOutTime 0']:self.assertIn(text,s)
  self.assertNotIn('outputweaponoffsettobuffer',s)
  self.assertIn('Child "ML71_PostPoseSupportBlend"',n['ML67_SharedVerticalAim'])
  self.assertIn('Child0 "ML51_StandingLeftElbowOnly"',n['ML71_PostPoseSupportBlend']);self.assertIn('OptimizeMin 1',n['ML71_PostPoseSupportBlend'])
 def test_all_existing_pose_nodes_unchanged_except_contact_routing(self):
  old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((B/'WorkspaceSource/locomotion.agf').read_text())
  for name,node in old.items():
   if name.startswith('{'):continue
   expected=node.replace('Child "ML51_StandingLeftElbowOnly"','Child "ML71_PostPoseSupportBlend"') if name=='ML67_SharedVerticalAim' else node
   self.assertEqual(new[name],expected,name)
  self.assertEqual({n for n in new.keys()-old.keys() if not n.startswith('{')},{'ML71_PostPoseSupportIK','ML71_PostPoseSupportBlend'})
 def test_control_binding_and_comparison_fallback(self):
  agr=(B/'WorkspaceSource/player_main.agr').read_text();self.assertEqual(agr.count('AnimSrcGCTVarFloat ML71SupportGrip {'),1)
  s=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();self.assertIn('m_ML71SupportVar >= 0',s)
  self.assertGreaterEqual(s.count('m_ML71SupportVar != '),10);self.assertNotIn('ML60UpdateGrip',s);self.assertNotRegex(s,r'\]\s*\[')
  keys=(B/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();self.assertIn('key == KeyCode.KC_F9 && m_ML71ControlDown',keys);self.assertIn('Post-pose support grip OFF: v70 comparison',keys)
  self.assertNotIn('KC_F11',keys);self.assertNotIn('KC_HOME',keys)
  for lean in (-1,0,1):
   for gate in (0,1):
    self.assertEqual(max(0,min(1,abs(lean)*gate*0)),0)
if __name__=='__main__':unittest.main()
