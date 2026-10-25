"""Upright shared walking torso with compensated head roll and native pitch relief."""
import sys,unittest,re,json,math,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v23'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v22'
base.KIT=KIT
def amount(node):return float(re.search(r'Amount ([-+0-9.eE]+)',node)[1])
class UprightWalkingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.g=(KIT/'WorkspaceSource/locomotion.agf').read_text();cls.n=newnodes(cls.g)
  cls.old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text())
 def test_side_bend_reduced_equally_and_head_roll_compensated(self):
  for side in ['left','right']:
   torso=[f'ML5_StandWalk_{side}_{bone}_Rotate_Z' for bone in ['Spine','Spine1','Spine2']]
   for name in torso:self.assertAlmostEqual(amount(self.n[name]),amount(self.old[name])*.4,places=9)
   oldsum=sum(amount(self.old[name]) for name in torso);newsum=sum(amount(self.n[name]) for name in torso)
   self.assertAlmostEqual(abs(math.degrees(newsum)),10.4,delta=.001)
   neck=f'ML5_StandWalk_{side}_Neck1_Rotate_Z';head=f'ML5_StandWalk_{side}_Head_Rotate_Z'
   self.assertAlmostEqual(oldsum+amount(self.old[neck])+amount(self.old[head]),newsum+amount(self.n[neck])+amount(self.n[head]),places=8)
   self.assertEqual(self.n[head],self.old[head])
 def test_forward_relief_keeps_native_transform_and_collision_untouched(self):
  native=self.n['LeanForwardMoveRotNode'];relief=self.n['ML23_WalkForwardPitchRelief']
  self.assertEqual(native,self.old['LeanForwardMoveRotNode'])
  self.assertNotIn('Bone "Collision"',relief)
  pattern=r'Bone "([^"]+)"\s+Axis X\s+Space Model\s+Op Rotate\s+Amount ([-+0-9.eE]+)'
  native_values={b:float(v) for b,v in re.findall(pattern,native)}
  relief_values={b:float(v) for b,v in re.findall(pattern,relief)}
  self.assertEqual(set(native_values),set(relief_values));self.assertEqual(len(relief_values),6)
  for bone,value in native_values.items():self.assertAlmostEqual(relief_values[bone],-.75*value)
  expr=re.search(r'Expression "([^"]+)"',relief)[1]
  for lean,gate,wanted in [(1,1,.25),(-1,1,.25),(0,1,1),(1,0,1),(.5,1,.625)]:
   value=base.expression(expr,{'LeanForward':10,'MLADSLeanGate':gate,'MLADSLeanAmount':lean,'clamp':lambda x,a,b:max(a,min(b,x)),'abs':abs})
   original=10*math.pi/180
   self.assertAlmostEqual((original*.3+value*-.225)/(original*.3),wanted)
 def test_relief_only_on_standing_moving_branch(self):
  self.assertIn('Child "ML23_WalkForwardPitchRelief"',self.n['MovementRasSTM'])
  self.assertIn('Child "LeanForwardMoveRotNode"',self.n['ML23_WalkForwardPitchRelief'])
  original=self.old['MovementRasSTM']
  self.assertEqual(self.n['MovementRasSTM'],original.replace('Child "LeanForwardMoveRotNode"','Child "ML23_WalkForwardPitchRelief"'))
  expr=re.search(r'Expression "([^"]+)"',self.n['ML23_WalkForwardPitchRelief'])[1]
  self.assertNotIn('MLADSLeanCanary',expr) # same correction for both actors
 def test_only_intended_walk_nodes_change(self):
  expected={'MovementRasSTM'}
  for side in ['left','right']:
   expected|={f'ML5_StandWalk_{side}_{b}_Rotate_Z' for b in ['Spine','Spine1','Spine2','Neck1']}
  self.assertEqual({n for n in self.old if not n.startswith('{') and self.n[n]!=self.old[n]},expected)
  self.assertEqual({n for n in self.n if n not in self.old and not n.startswith('{')},{'ML23_WalkForwardPitchRelief'})
  for name,node in self.old.items():
   if name.startswith(('ML5_StandIdle_','ML5_CrouchIdle_','ML5_CrouchWalk_')):self.assertEqual(self.n[name],node,name)
  for name in ['MovementRasIK','NormalWeaponIK','ML20_RightLeanHeadExposure','ML21_RightMovingHeadLift','ML5_StandWalk_left_Pelvis_Translate_Y','ML5_StandWalk_right_Pelvis_Translate_Y']:
   self.assertEqual(self.n[name],self.old[name])
 def test_shared_player_npc_and_range_logic_preserved(self):
  for path in ['LogicSource/Scripts/4_World/MLADSLeanPlayer.c','LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c','LogicSource/Scripts/5_Mission/MLADSLeanKeys.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   new=(KIT/path).read_text().replace('MLADSLEAN23','MLADSLEAN22').replace('lean v23','lean v22')
   self.assertEqual(new,(OLD/path).read_text(),path)
  self.assertEqual((KIT/'WorkspaceSource/player_main.agr').read_bytes(),(OLD/'WorkspaceSource/player_main.agr').read_bytes())
  self.assertNotIn('MLADSLeanDemoActive',self.g)
 def test_manifest_and_direct_launcher(self):
  d=json.loads((KIT/'validation.json').read_text())
  for path,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/path).read_bytes()).hexdigest(),h)
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v23-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(UprightWalkingTests));return suite
if __name__=='__main__':unittest.main()
