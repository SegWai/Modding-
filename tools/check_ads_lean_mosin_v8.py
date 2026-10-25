"""Retain previous checks; regress the native diagnostic expression failure."""
import sys,unittest
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v7 as previous
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v8'
previous.KIT=KIT
previous.previous.KIT=KIT
previous.previous.previous.KIT=KIT
class DiagnosticExpressionRegression(unittest.TestCase):
 def test_reported_status_expression_split_without_losing_fields(self):
  import re
  old=(ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v7/LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  before=next(line for line in old.splitlines() if 'string status =' in line)
  after=[line for line in code.splitlines() if 'string status =' in line or 'status +=' in line]
  self.assertEqual(len(after),9)
  self.assertEqual(re.findall(r'"([^"\n]*)"',before),re.findall(r'"([^"\n]*)"','\n'.join(after)))
  self.assertTrue(all(line.count('+')<=2 for line in after))
  # The entire actor logic is identical once diagnostics and version labels are removed.
  normalized_old=old.replace(before,'STATUS').replace('MLADSLEAN7','MLADSLEAN8')
  start=code.index('  // Keep each diagnostic expression small')
  end=code.index('\n  if (localPlayer)',start)
  self.assertEqual(normalized_old,code[:start]+'STATUS'+code[end:])
def load_tests(loader,tests,pattern):
 suite=previous.load_tests(loader,tests,pattern)
 suite.addTests(loader.loadTestsFromTestCase(DiagnosticExpressionRegression));return suite
if __name__=='__main__':unittest.main()
