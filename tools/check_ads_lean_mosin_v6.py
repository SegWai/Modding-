"""Retain v5 coverage and regress the reported native getter/launcher errors."""
from pathlib import Path
import unittest,sys,json,re
sys.dont_write_bytecode=True
import check_ads_lean_mosin_v5 as previous
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v6';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v5'
previous.KIT=KIT
class CompileLauncherRegression(unittest.TestCase):
 def test_reported_invalid_calls_replaced_by_sdk_declared_getter(self):
  old=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();new=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  contract=json.loads((KIT/'API-Contracts.json').read_text())
  self.assertEqual(old.count('GetCommand_Weapons()'),2)
  self.assertNotIn('GetCommand_Weapons(',new)
  self.assertEqual(new.count('GetCommandModifier_Weapons()'),2)
  self.assertRegex(contract['weapon_command_declaration'],r'HumanCommandWeapons\s+GetCommandModifier_Weapons\(\)')
 def test_direct_launch_and_ingame_comparison(self):
  cmd=(KIT/'Launch-Mosin-Lean-Test.cmd').read_text();ps=(KIT/'Launch-Test.ps1').read_text()
  self.assertNotRegex(cmd.lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertNotIn('NativeBaseline',ps);self.assertNotIn('Read-Host \'Choose',ps)
  self.assertIn('$mods = @($workspace,$logic)',ps)
  self.assertIn('F:\\DayZProjects',ps)
  self.assertIn('KeyCode.KC_F7',(KIT/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text())
 def test_animation_graph_and_pose_targets_unchanged(self):
  for name in ['WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','Pose-Snapshot.json','Pose-Spec.json','Mode-Coverage.json','Symmetry-Measurements.json']:
   self.assertEqual((OLD/name).read_bytes(),(KIT/name).read_bytes(),name)
 def test_future_menu_preference_recorded(self):
  rules=(ROOT/'ads-lean-test/AGENTS.md').read_text()
  self.assertIn('Launch lean-test batches directly',rules)
  self.assertIn('FPS graphics-settings helper',rules)

def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(previous.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(CompileLauncherRegression));return suite
if __name__=='__main__':unittest.main()
