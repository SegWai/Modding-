"""Raised-view inspection scope, native ADS preservation and approved-pose integrity."""
import sys,unittest,json,re,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from check_ads_lean_mosin_v36 import CommonTargetTests
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v40';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v39';base.KIT=KIT
class ActivationScopeTests(CommonTargetTests):
 def test_actual_activation_guard_covers_walk_crouch_and_demo(self):
  original=self.code
  try:
   # Existing guard suite uses the old name for the already-resolved inspection flag.
   self.code=original.replace('(aiming || inspectionAllowed)','(aiming || MLADSLeanSettings.Inspection)')
   super().test_actual_activation_guard_covers_walk_crouch_and_demo()
  finally:self.code=original
class FirstPersonTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
 def test_approved_workspace_is_byte_identical_in_source_and_pbo(self):
  for p in (OLD/'WorkspaceSource').rglob('*'):
   if p.is_file():self.assertEqual(p.read_bytes(),(KIT/p.relative_to(OLD)).read_bytes(),str(p))
  p='@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo';self.assertEqual((OLD/p).read_bytes(),(KIT/p).read_bytes())
 def test_actual_inspection_expression_scope_truth_table(self):
  expr=re.search(r'inspectionAllowed = (inspectionAllowed && [^;]+);',self.c)[1]
  for local in [False,True]:
   for enabled in [False,True]:
    for camera in ['DayZPlayerCamera3rdPerson','DayZPlayerCamera1stPerson','DayZPlayerCameraIronsights','DayZPlayerCameraOptics','none']:
     allowed=base.expression(expr,dict(inspectionAllowed=enabled,cameraName=camera)) if local else enabled
     self.assertEqual(allowed,enabled and (not local or camera=='DayZPlayerCamera3rdPerson'))
     for aiming in [False,True]:
      target=aiming or allowed
      if aiming:self.assertTrue(target)
      elif local and camera!='DayZPlayerCamera3rdPerson':self.assertFalse(target)
  self.assertEqual(self.c.count('(aiming || inspectionAllowed)'),2)
  self.assertNotIn('(aiming || MLADSLeanSettings.Inspection)',self.c)
 def test_only_inspection_scope_and_status_added_to_player_source(self):
  old=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text().replace('MLADSLEAN39','MLADSLEAN40').replace('lean v39','lean v40')
  actual=self.c
  added=actual.split('  // F8 is a third-person pose inspection feature',1)[1].split("  // Match the player's actual native gait",1)[0]
  actual=actual.replace('  // F8 is a third-person pose inspection feature'+added,'')
  actual=actual.replace('(aiming || inspectionAllowed)','(aiming || MLADSLeanSettings.Inspection)')
  status='''  string status = "view=" + viewState;
  status += " camera=" + cameraName;
  status += " inspection_requested=" + MLADSLeanSettings.Inspection;
  status += " inspection_applied=" + inspectionAllowed;
  status += " bindings=" + m_MLADSLeanBound;'''
  actual=actual.replace(status,'  string status = "bindings=" + m_MLADSLeanBound;')
  self.assertEqual(actual,old)
 def test_no_camera_matrix_input_or_shooting_override(self):
  newcode=self.c.split('// F8 is a third-person pose inspection feature',1)[1].split("// Match the player's actual native gait",1)[0]
  for forbidden in ['AnimSet','SetADS','OverrideMovement','SetPosition','m_CameraTM','m_fShootFromCamera','CameraHandler(']:self.assertNotIn(forbidden,newcode)
  for p in (KIT/'LogicSource').rglob('*.c'):self.assertNotRegex(p.read_text(),r'modded class DayZPlayerCamera')
 def test_camera_status_and_world_range_preserved(self):
  for field in ['view=','camera=','inspection_requested=','inspection_applied=','native_ADS=']:self.assertIn(field,self.c)
  for line in self.c.splitlines():
   if 'status +=' in line or 'string status =' in line:self.assertLessEqual(line.count('+'),2)
  for p in ['LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual((OLD/p).read_text().replace('MLADSLEAN39','MLADSLEAN40').replace('lean v39','lean v40'),(KIT/p).read_text())
 def test_hashes_direct_launch_and_log_version(self):
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('Mosin-Lean-v40-Logs',(KIT/'Collect-Logs.ps1').read_text())
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(ActivationScopeTests);suite.addTests(loader.loadTestsFromTestCase(FirstPersonTests));return suite
if __name__=='__main__':unittest.main()
