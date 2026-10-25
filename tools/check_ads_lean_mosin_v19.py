"""Retain range coverage; regress Enforce vector/scalar division failure."""
import sys,unittest,re,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v18 as previous
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v19'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v18'
module=previous
while module:
 module.KIT=KIT
 if hasattr(module,'base'):module.base.KIT=KIT
 module=getattr(module,'previous',None)
class VectorScalarRangeTests(previous.SinglePlayerLayerRangeTests):
 def test_scope_of_player_controller_changes_and_script_structure(self):
  old=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  bad='  vector velocity = (GetPosition() - m_MLADSLeanRangeLastPosition) / (elapsed * 0.001);'
  fixed='''  // Enforce supports vector * scalar; do not divide a vector by a scalar.
  float elapsedMilliseconds = elapsed;
  float inverseSeconds = 1000.0 / elapsedMilliseconds;
  vector displacement = GetPosition() - m_MLADSLeanRangeLastPosition;
  vector velocity = displacement * inverseSeconds;'''
  self.assertEqual(old.count(bad),1)
  actual=self.player.replace('MLADSLEAN19','MLADSLEAN18').replace('lean v19','lean v18')
  self.assertEqual(actual,old.replace(bad,fixed))
  ammo='LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c'
  self.assertEqual((KIT/ammo).read_text(),(OLD/ammo).read_text())
  mission='Missions/MLADSLeanMosin.ChernarusPlus/init.c'
  self.assertEqual((KIT/mission).read_text().replace('MLADSLEAN19','MLADSLEAN18').replace('lean v19','lean v18'),(OLD/mission).read_text())
 def test_packaged_hashes_and_launcher_preferences(self):
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v19-Logs',(KIT/'Collect-Logs.ps1').read_text())
 def test_sampler_uses_supported_vector_multiplication_with_guarded_time(self):
  block=self.player.split('void MLADSLeanRangeSampleMotion()',1)[1].split('override void EEKilled',1)[0]
  self.assertIn('if (elapsed < 80)\n   return;',block)
  self.assertIn('float elapsedMilliseconds = elapsed;',block)
  scalar=re.search(r'float inverseSeconds = ([^;]+);',block)[1]
  self.assertIn('vector velocity = displacement * inverseSeconds;',block)
  self.assertNotRegex(block,r'vector\s+\w+\s*=[^;\n]*/')
  # Units: metres times inverse seconds must reproduce the original intended velocity.
  for millis,displacement,expected in [(80,.1,1.25),(100,.1,1),(200,1,5)]:
   inverse=eval(scalar,{'__builtins__':{}},{'elapsedMilliseconds':float(millis)})
   self.assertAlmostEqual(displacement*inverse,expected)
  self.assertIn('elapsed <= 200 && velocity.Length() <= 8',block)
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(previous.previous.base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(VectorScalarRangeTests));return suite
if __name__=='__main__':unittest.main()
