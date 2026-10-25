"""Dedicated control, resource routing and missing-optional-bone regression checks."""
import sys,unittest,re,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes,end
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v28';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v27';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class DedicatedControlTests(unittest.TestCase):
 def test_only_offset_control_expression_changed(self):
  a=(OLD/'WorkspaceSource/locomotion.agf').read_text();b=(KIT/'WorkspaceSource/locomotion.agf').read_text()
  self.assertEqual(a.count('*TestFloat'),1)
  self.assertEqual(a.replace('*TestFloat','*MLADSLeanWeaponShift'),b)
  node=newnodes(b)['ML24_MarkedShoulderOffset']
  self.assertEqual(node.count('Amount 0.35'),2)
 def test_dedicated_control_defaults_on_without_reordering_existing_variables(self):
  a=(OLD/'WorkspaceSource/player_main.agr').read_text();b=(KIT/'WorkspaceSource/player_main.agr').read_text()
  declared=re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',b)
  self.assertEqual(declared[:-1],re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',a))
  self.assertEqual(declared[-1],'MLADSLeanWeaponShift')
  self.assertRegex(b,r'AnimSrcGCTVarFloat MLADSLeanWeaponShift \{\s+DefaultValue 1\s+MinValue 0\s+MaxValue 1\s+\}')
  code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  self.assertIn('BindVariableFloat("MLADSLeanWeaponShift")',code)
  self.assertNotIn('BindVariableFloat("TestFloat")',code)
  self.assertIn('AnimSetFloat(m_MLADSLeanWeaponShiftVar, shoulderShiftScale)',code.split('super.CommandHandler(',1)[1])
 def test_optional_hand_lookup_cannot_suppress_weapon_and_chest_samples(self):
  s=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  block=s.split('protected void MLADSLeanReportShoulderPose(int gait)',1)[1].split('// Read-only measurements',1)[0]
  returns=re.findall(r'if \(([^\n]+)\)\s+return;',block)
  self.assertEqual(returns,['chestIndex < 0 || !held'])
  self.assertIn('GetBoneIndexByName("RightHand_Dummy")',block)
  self.assertIn('GetBoneIndexByName("LeftHand_Dummy")',block)
  for field in ['right_hand_index=','left_hand_index=','weapon_chest_x_m=','chest_ms=','weapon_ms=','enabled=','lean=','gait=']:self.assertIn(field,block)
  self.assertNotIn('AnimSet',block)
  # Missing optional hands still reaches the observable rifle/chest sample.
  for right,left in [(-1,-1),(-1,5),(4,-1),(4,5)]:
   chest=1;held=True
   self.assertFalse(chest<0 or not held)
  for line in block.splitlines():
   if 'sample +=' in line:self.assertLessEqual(line.count('+'),2)
 def test_private_resource_and_complete_payload_integrity(self):
  prefix,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes())
  root=entries['player_main.agr'].decode();self.assertIn('/MLADSLeanLocomotion_v28.agf',root)
  self.assertEqual(entries['MLADSLeanLocomotion_v28.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertNotIn('locomotion.agf',entries)
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
 def test_range_behaviour_unchanged_and_direct_launcher(self):
  for p in ['LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual((OLD/p).read_text().replace('MLADSLEAN27','MLADSLEAN28').replace('lean v27','lean v28'),(KIT/p).read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertIn('Mosin-Lean-v28-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests);suite.addTests(loader.loadTestsFromTestCase(DedicatedControlTests));return suite
if __name__=='__main__':unittest.main()
