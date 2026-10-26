"""Regression for requested reversal to30cm anatomical left."""
import sys,unittest,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v30';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v29';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class LeftHoldTests(unittest.TestCase):
 def test_only_translation_and_private_resource_version_change(self):
  a=(OLD/'WorkspaceSource/locomotion.agf').read_text();b=(KIT/'WorkspaceSource/locomotion.agf').read_text()
  node=newnodes(a)['ML29_FinalRightChestHold'];self.assertEqual(node.count('Amount 0.15'),2)
  self.assertEqual(a.replace(node,node.replace('Amount 0.15','Amount -0.30')),b)
  self.assertEqual((OLD/'WorkspaceSource/player_main.agr').read_text().replace('Locomotion_v29.agf','Locomotion_v30.agf'),(KIT/'WorkspaceSource/player_main.agr').read_text())
 def test_player_and_range_controller_unchanged(self):
  for p in list((OLD/'LogicSource/Scripts/4_World').glob('*.c'))+[OLD/'Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual(p.read_text().replace('MLADSLEAN29','MLADSLEAN30').replace('lean v29','lean v30'),(KIT/p.relative_to(OLD)).read_text())
 def test_final_shift_packed_and_hashes_valid(self):
  _,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes())
  self.assertEqual(entries['MLADSLeanLocomotion_v30.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertIn(b'MLADSLeanLocomotion_v30.agf',entries['player_main.agr'])
  self.assertNotIn('locomotion.agf',entries)
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
 def test_direct_launcher_and_current_comparison_label(self):
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertIn('Mosin-Lean-v30-Logs',(KIT/'Collect-Logs.ps1').read_text())
  self.assertIn('30 cm left',(KIT/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests);suite.addTests(loader.loadTestsFromTestCase(LeftHoldTests));return suite
if __name__=='__main__':unittest.main()
