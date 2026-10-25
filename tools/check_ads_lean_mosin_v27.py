"""Archive routing and unchanged-pose checks after native v26 graph errors."""
import sys,unittest,re,hashlib,json
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v27'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v26'
base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class ResourceLoadingTests(unittest.TestCase):
 def test_packed_root_resolves_private_fragment_without_vanilla_override(self):
  prefix,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes())
  root=entries['player_main.agr'].decode()
  self.assertEqual(prefix,'DZ\\anims\\workspaces\\player\\player_main')
  names=re.findall(r'\{([A-F0-9]+)\}DZ/anims/workspaces/player/player_main/([^" ]+\.agf)',root)
  loc=[(g,p) for g,p in names if 'Locomotion' in p]
  self.assertEqual(len(loc),1)
  guid,path=loc[0]
  self.assertIn(path,entries)
  self.assertNotEqual(guid,'6CA2ACDCAC1184DC')
  self.assertNotIn('locomotion.agf',entries)
  self.assertNotIn('Locomotion.agf',entries)
  self.assertEqual(entries[path],(OLD/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertEqual(root,(KIT/'WorkspaceSource/player_main.agr').read_text())
 def test_control_template_contents_and_all_pose_values_preserved(self):
  a=(OLD/'WorkspaceSource/player_main.agr').read_text();b=(KIT/'WorkspaceSource/player_main.agr').read_text()
  def normalize(s):
   s=re.sub(r'(ControlTemplate AnimSrcGCT )"\{[A-F0-9]+\}"',r'\1"{CONTROL}"',s)
   return re.sub(r'\{[A-F0-9]+\}DZ/anims/workspaces/player/player_main/(?:Locomotion|MLADSLeanLocomotion_v27)\.agf','{FRAGMENT}Locomotion.agf',s)
  self.assertEqual(normalize(a),normalize(b))
  self.assertEqual((OLD/'WorkspaceSource/locomotion.agf').read_bytes(),(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
 def test_range_scripts_and_death_controller_unchanged(self):
  paths=['LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']
  for p in paths:
   self.assertEqual((OLD/p).read_text().replace('MLADSLEAN26','MLADSLEAN27').replace('lean v26','lean v27'),(KIT/p).read_text())
  p='LogicSource/Scripts/4_World/MLADSLeanPlayer.c'
  self.assertEqual((OLD/p).read_text().split('protected bool m_MLADSLeanRangeTarget;',1)[1].replace('MLADSLEAN26','MLADSLEAN27'),(KIT/p).read_text().split('protected bool m_MLADSLeanRangeTarget;',1)[1])
 def test_observation_is_read_only_and_waits_for_settling(self):
  s=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  sample=s.split('protected void MLADSLeanReportShoulderPose(int gait)',1)[1].split('// Read-only measurements',1)[0]
  self.assertNotIn('AnimSet',sample)
  for field in ['enabled=','bound=','lean=','gait=','chest_ms=','right_hand_ms=','left_hand_ms=','weapon_ms=','weapon_chest_x_m=']:self.assertIn(field,sample)
  self.assertIn('m_MLADSLeanShoulderStableTime > 0.35',s)
  self.assertIn('now + 1000',s)
  self.assertIn('shoulderSign != m_MLADSLeanShoulderLastSign',s)
  for line in s.splitlines():
   if 'sample +=' in line:self.assertLessEqual(line.count('+'),2)
 def test_hashes_and_direct_launcher(self):
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertIn('Mosin-Lean-v27-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(ResourceLoadingTests));return suite
if __name__=='__main__':unittest.main()
