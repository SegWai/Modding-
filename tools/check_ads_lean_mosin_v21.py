"""Shared walk height/head lift while preserving stationary legs and range logic."""
import sys,unittest,re,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v21'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v20'
base.KIT=KIT
class SharedWalkPostureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.g=(KIT/'WorkspaceSource/locomotion.agf').read_text();cls.nodes=newnodes(cls.g)
  cls.old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text())
 def test_symmetric_standing_walk_drop_halved(self):
  for side in ['left','right']:
   name=f'ML5_StandWalk_{side}_Pelvis_Translate_Y'
   old=float(re.search(r'Amount ([-+0-9.eE]+)',self.old[name])[1]);new=float(re.search(r'Amount ([-+0-9.eE]+)',self.nodes[name])[1])
   self.assertAlmostEqual(old,-.12,places=6);self.assertEqual(new,-.06)
   self.assertAlmostEqual(new-old,.06,places=6)
   self.assertEqual(re.sub(r'Amount [-+0-9.eE]+','Amount VALUE',self.old[name]),re.sub(r'Amount [-+0-9.eE]+','Amount VALUE',self.nodes[name]))
 def test_small_head_lift_only_on_right_movement(self):
  node=self.nodes['ML21_RightMovingHeadLift'];expr=re.search(r'Expression "([^"]+)"',node)[1]
  self.assertEqual(re.findall(r'Bone "([^"]+)"',node),['Neck'])
  self.assertIn('Axis Y',node);self.assertIn('Op Translate',node)
  self.assertEqual(float(re.search(r'Amount ([-+0-9.eE]+)',node)[1]),.006)
  for lean,gate,speed,wanted in [(1,1,1,1),(1,1,2,1),(1,1,0,0),(-1,1,1,0),(0,1,1,0),(1,0,1,0),(.5,1,.5,.25)]:
   got=base.expression(expr,{'MLADSLeanAmount':lean,'MLADSLeanGate':gate,'MovementSpeed':speed,'clamp':lambda x,a,b:max(a,min(b,x))})
   self.assertEqual(got,wanted)
  self.assertNotIn('MLADSLeanCanary',expr)
  self.assertIn('Child "ML21_RightMovingHeadLift"',self.nodes['SickHotColdQ'])
  self.assertIn('Child "ML20_RightLeanHeadExposure"',node)
 def test_changes_limited_to_walk_hip_height_and_head_path(self):
  allowed={'SickHotColdQ','ML5_StandWalk_left_Pelvis_Translate_Y','ML5_StandWalk_right_Pelvis_Translate_Y'}
  changed={n for n in self.old if not n.startswith('{') and self.old[n]!=self.nodes[n]}
  self.assertEqual(changed,allowed)
  self.assertEqual({n for n in self.nodes if n not in self.old and not n.startswith('{')},{'ML21_RightMovingHeadLift'})
  for name in ['MovementRasIK','MLADSLeanFootIKBlend','NormalWeaponIK','ML20_RightLeanHeadExposure']:
   self.assertEqual(self.nodes[name],self.old[name])
  for name in self.old:
   if name.startswith(('ML5_StandIdle_','ML5_CrouchIdle_','ML5_CrouchWalk_')):self.assertEqual(self.nodes[name],self.old[name],name)
 def test_player_and_npc_share_all_corrections_and_controller_stays_unchanged(self):
  for path in ['LogicSource/Scripts/4_World/MLADSLeanPlayer.c','LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c','LogicSource/Scripts/5_Mission/MLADSLeanKeys.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   new=(KIT/path).read_text().replace('MLADSLEAN21','MLADSLEAN20').replace('lean v21','lean v20')
   self.assertEqual(new,(OLD/path).read_text(),path)
  for side in ['left','right']:
   node=self.nodes[f'ML5_StandWalk_{side}_Pelvis_Translate_Y']
   expr=re.search(r'Expression "([^"]+)"',node)[1]
   self.assertNotIn('MLADSLeanCanary',expr)
   self.assertIn('MLADSLeanAmount',expr);self.assertIn('MLADSLeanGate',expr)
  self.assertIn('do not add NPC-only pose changes',(ROOT/'ads-lean-test/AGENTS.md').read_text())
 def test_known_controls_and_pose_assets_unchanged(self):
  for path in ['WorkspaceSource/player_main.agr','Pose-Snapshot.json','Static-Pose-Snapshot.json','Mode-Coverage.json']:
   self.assertEqual((KIT/path).read_bytes(),(OLD/path).read_bytes())
  self.assertNotIn('MLADSLeanDemoActive',self.g)
  self.assertEqual(re.findall(r'HasVariableChanged\([^\n]+',self.g),re.findall(r'HasVariableChanged\([^\n]+',(OLD/'WorkspaceSource/locomotion.agf').read_text()))
 def test_packaging_and_direct_launcher(self):
  validation=json.loads((KIT/'validation.json').read_text())
  for path,h in validation['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/path).read_bytes()).hexdigest(),h)
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v21-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(SharedWalkPostureTests));return suite
if __name__=='__main__':unittest.main()
