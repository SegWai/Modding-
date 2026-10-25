"""Right-only neck/head exposure, preserved shooting range and loaded controls."""
import sys,unittest,re,json,math,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v20'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v19'
base.KIT=KIT
class HeadExposureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.g=(KIT/'WorkspaceSource/locomotion.agf').read_text();cls.nodes=newnodes(cls.g)
 def test_only_added_head_exposure_path_changes(self):
  old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());new=self.nodes
  self.assertEqual({n for n in old if old[n]!=new[n]},{'SickHotColdQ'})
  added={n for n in new if n not in old and not n.startswith('{')}
  self.assertEqual(added,{'ML20_RightLeanHeadExposure'})
  self.assertIn('Child "ML20_RightLeanHeadExposure"',new['SickHotColdQ'])
  self.assertIn('Child "ML15_HeadForwardNod"',new['ML20_RightLeanHeadExposure'])
  self.assertEqual(new['NormalWeaponIK'],old['NormalWeaponIK'])
 def test_only_right_custom_lean_moves_head_subtree(self):
  node=self.nodes['ML20_RightLeanHeadExposure'];expr=re.search(r'Expression "([^"]+)"',node)[1]
  for amount,gate,expected in [(-1,1,0),(0,1,0),(1,0,0),(.5,1,.5),(1,1,1)]:
   got=base.expression(expr,{'clamp':lambda x,a,b:max(a,min(b,x)),'MLADSLeanAmount':amount,'MLADSLeanGate':gate})
   self.assertEqual(got,expected)
  self.assertNotIn('MLADSLeanCanary',expr)
  self.assertEqual(set(re.findall(r'Bone "([^"]+)"',node)),{'Neck'})
 def test_expected_neck_rotation_and_translation(self):
  node=self.nodes['ML20_RightLeanHeadExposure']
  items=re.findall(r'Bone "Neck"\s+Axis ([XYZ])\s+Space Model\s+Op (Rotate|Translate)\s+Amount ([-0-9.eE]+)',node)
  values={(a,op):float(value) for a,op,value in items}
  self.assertEqual(set(values),{('Z','Rotate'),('X','Translate'),('Y','Translate')})
  self.assertAlmostEqual(math.degrees(values['Z','Rotate']),-10,places=6)
  self.assertEqual(values['X','Translate'],-.025);self.assertEqual(values['Y','Translate'],.01)
  snap=json.loads((KIT/'Pose-Snapshot.json').read_text());parents=snap['parents']
  def descendant(bone):
   while bone:
    if bone=='Neck':return True
    bone=parents[bone]
   return False
  self.assertTrue(descendant('Head'))
  for bone in ['LeftShoulder','RightShoulder','LeftArm','RightArm','LeftHand','RightHand','Pelvis','LeftFoot','RightFoot']:
   self.assertFalse(descendant(bone),bone)
  # Authoring-model geometry: bend around neck pivot plus translation exposes head centre.
  pose=snap['right'];neck=[pose['Neck'][i][3] for i in range(3)];head=[pose['Head'][i][3] for i in range(3)]
  angle=-values['Z','Rotate'];x,y=head[0]-neck[0],head[1]-neck[1]
  dx=math.cos(angle)*x-math.sin(angle)*y-x-.025
  dy=math.sin(angle)*x+math.cos(angle)*y-y+.01
  self.assertLess(dx,-.04);self.assertGreater(dx,-.06)
  self.assertGreater(dy,.01);self.assertLess(dy,.025)
 def test_controller_ammo_respawn_and_pose_baselines_unchanged(self):
  for path in ['LogicSource/Scripts/4_World/MLADSLeanPlayer.c','LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c','LogicSource/Scripts/5_Mission/MLADSLeanKeys.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   new=(KIT/path).read_text().replace('MLADSLEAN20','MLADSLEAN19').replace('lean v20','lean v19')
   self.assertEqual(new,(OLD/path).read_text(),path)
  for path in ['WorkspaceSource/player_main.agr','Pose-Snapshot.json','Static-Pose-Snapshot.json','Mode-Coverage.json']:
   self.assertEqual((KIT/path).read_bytes(),(OLD/path).read_bytes(),path)
 def test_registered_controls_and_change_arguments_preserved(self):
  agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
  declared=set(re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr))
  for arg in re.findall(r'HasVariableChanged\(\s*([^,)\n]+)',self.g):self.assertIn(arg.strip(),declared)
  self.assertNotIn('MLADSLeanDemoActive',self.g)
  self.assertEqual(re.findall(r'HasVariableChanged\([^\n]+',self.g),re.findall(r'HasVariableChanged\([^\n]+',(OLD/'WorkspaceSource/locomotion.agf').read_text()))
 def test_pbo_hashes_and_direct_launcher(self):
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v20-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(HeadExposureTests));return suite
if __name__=='__main__':unittest.main()
