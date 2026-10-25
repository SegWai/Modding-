"""Regression: only the existing shared shoulder displacement changes."""
import sys, unittest, hashlib, json
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v25'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v24'
base.KIT=KIT
class RightChestTests(unittest.TestCase):
 def test_only_arm_offset_changed_in_graph(self):
  a=(OLD/'WorkspaceSource/locomotion.agf').read_text();b=(KIT/'WorkspaceSource/locomotion.agf').read_text()
  node=newnodes(a)['ML24_MarkedShoulderOffset']
  self.assertEqual(node.count('Amount 0.08'),2)
  self.assertEqual(a.replace(node,node.replace('Amount 0.08','Amount 0.14')),b)
 def test_scripts_and_registration_preserved(self):
  for p in list((OLD/'LogicSource').rglob('*'))+list((OLD/'Missions').rglob('*'))+[OLD/'WorkspaceSource/player_main.agr']:
   if p.is_file():
    a=p.read_text().replace('MLADSLEAN24','MLADSLEAN25').replace('lean v24','lean v25').replace('Test v24','Test v25')
    self.assertEqual(a,(KIT/p.relative_to(OLD)).read_text(),str(p))
 def test_package_hashes(self):
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
 def test_launcher_and_logs(self):
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotIn('choice ',(KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower())
  self.assertIn('Mosin-Lean-v25-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(RightChestTests));return suite
if __name__=='__main__':unittest.main()
