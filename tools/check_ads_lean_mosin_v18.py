"""Retain range coverage and regress the undefined method across PlayerBase layers."""
import sys,unittest,re,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v17 as previous
from dayz_graph_formats import end
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v18'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v17'
previous.KIT=KIT
previous.base.KIT=KIT
class SinglePlayerLayerRangeTests(previous.RangeTests):
 @classmethod
 def setUpClass(cls):
  cls.player=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  cls.world=cls.player+'\n'+(KIT/'LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c').read_text()
  cls.mission=(KIT/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
 def test_scope_of_player_controller_changes_and_script_structure(self):
  # Reconstruct the intended merge independently from the exact v17 sources.
  p=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  r=(OLD/'LogicSource/Scripts/4_World/MLADSLeanRangeTarget.c').read_text()
  a=r.index('modded class PlayerBase');b=end(r,a);body=r[r.index('{',a)+1:b-1]
  a=p.index('modded class PlayerBase');b=end(p,a)
  expected=p[:b-1]+'\n // Range methods share this same PlayerBase layer; no upward patch calls.\n'+body+'\n'+p[b-1:]
  actual=self.player.replace('MLADSLEAN18','MLADSLEAN17').replace('lean v18','lean v17')
  self.assertEqual(actual,expected)
  ammo=(KIT/'LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c').read_text().replace('MLADSLEAN18','MLADSLEAN17')
  self.assertEqual(ammo[ammo.index('class MLADSLeanRangeAmmo'):],r[r.index('class MLADSLeanRangeAmmo'):])
  sources=[p.read_text() for p in (KIT/'LogicSource/Scripts/4_World').glob('*.c')]
  self.assertEqual(sum(len(re.findall(r'\bmodded class PlayerBase\b',s)) for s in sources),1)
  self.assertFalse((KIT/'LogicSource/Scripts/4_World/MLADSLeanRangeTarget.c').exists())
 def test_packaged_hashes_and_launcher_preferences(self):
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v18-Logs',(KIT/'Collect-Logs.ps1').read_text())
 def test_reported_call_resolves_within_same_layer(self):
  def owns_range_sample(source):
   a=source.index('modded class PlayerBase');b=end(source,a);body=source[a:b]
   return 'void MLADSLeanRangeSampleMotion()' in body and 'MLADSLeanRangeSampleMotion();' in body
  self.assertFalse(owns_range_sample((OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()))
  self.assertTrue(owns_range_sample(self.player))
  a=self.player.index('modded class PlayerBase');b=end(self.player,a);body=self.player[a:b]
  methods=re.findall(r'(?m)^ (?:protected )?(?:override )?(?:void|bool|float|int|string) (\w+)\(',body)
  self.assertEqual(len(methods),len(set(methods)))
  for name in ['MLADSLeanRangeSampleMotion','MLADSLeanStopDemo','EEKilled','HandleDeath','CommandHandler']:
   self.assertIn(name,methods)
 def test_graph_and_pose_assets_unchanged_from_v17(self):
  for name in ['WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','Pose-Snapshot.json','Static-Pose-Snapshot.json','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo']:
   self.assertEqual((KIT/name).read_bytes(),(OLD/name).read_bytes(),name)
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(previous.base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(SinglePlayerLayerRangeTests));return suite
if __name__=='__main__':unittest.main()
