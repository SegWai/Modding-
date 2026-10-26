"""Directional elbow seed with captured native wrist target and unchanged working hold."""
import sys,unittest,json,re,hashlib,math
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from check_ads_lean_mosin_v36 import CommonTargetTests
from dayz_graph_formats import newnodes,end
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v38';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v37';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class ElbowTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.n=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text());cls.a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text())
 def test_chain_captures_final_grip_then_changes_elbow_and_restores_same_target(self):
  n=self.n
  self.assertIn('Child "ML33_FinalGripIK"',n['ML37_CaptureRightGrip'])
  self.assertIn('Child "ML37_CaptureRightGrip"',n['ML37_RightElbowIn'])
  self.assertIn('Child "ML37_RightElbowIn"',n['ML37_RightElbowOut'])
  self.assertIn('Child "ML37_RightElbowOut"',n['ML37_RestoreRightGrip'])
  self.assertIn('Child0 "ML33_FinalGripIK"',n['ML37_RightElbowBlend']);self.assertIn('Child1 "ML37_RestoreRightGrip"',n['ML37_RightElbowBlend'])
  self.assertIn('Child "ML37_RightElbowBlend"',n['ML15_HeadForwardNod'])
  for name in ['ML37_CaptureRightGrip','ML37_RestoreRightGrip']:
   self.assertIn('IkTarget "RHandIKTarget"',n[name])
   chain=re.search(r'IkChain "([^\"]+)"',n[name])[1]
   agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
   self.assertIn('}'+chain+'"',agr)
   match=re.search(r'AnimSrcGCTIkChain "\{[A-F0-9]+\}'+re.escape(chain)+r'"',agr)
   self.assertIsNotNone(match)
   start=match.start();definition=agr[start:end(agr,start)]
   self.assertIn('MiddleJoint "RightForeArm"',definition)
   self.assertNotIn('Left',definition)
 def test_direction_seed_and_scope(self):
  for name,wanted_expr,wanted_angle in [('ML37_RightElbowIn','clamp(MLADSLeanAmount, 0.0, 1.0)',36),('ML37_RightElbowOut','clamp(-MLADSLeanAmount, 0.0, 1.0)',-20)]:
   b=self.n[name];self.assertIn('Expression "'+wanted_expr+'"',b)
   self.assertRegex(b,r'Bone "RightArm"\s+Axis Z\s+Space Model\s+Op Rotate')
   self.assertAlmostEqual(math.degrees(float(re.search(r'Amount ([-\d.eE]+)',b)[1])),wanted_angle,places=8)
   self.assertNotIn('Op Translate',b)
  expr=re.search(r'BlendWeight "([^\"]+)"',self.n['ML37_RightElbowBlend'])[1]
  for gate,speed,stance,enabled,wanted in [(1,1,0,1,1),(0,1,0,1,0),(1,0,0,1,0),(1,1,1,1,0),(1,1,0,0,0)]:
   self.assertEqual(base.expression(expr,dict(MLADSLeanGate=gate,MovementSpeed=speed,Stance=stance,MLADSLeanWeaponShift=enabled,clamp=lambda x,a,b:max(a,min(b,x)))),wanted)
  self.assertIn('OptimizeMin 1',self.n['ML37_RightElbowBlend'])
  self.assertNotIn('MLADSLeanCanary',expr)
 def test_original_gun_height_and_body_nodes_are_unchanged(self):
  changed={n for n in self.a if n in self.n and not n.startswith('{') and self.a[n]!=self.n[n]}
  self.assertEqual(changed,{'ML37_RightElbowIn','ML37_RightElbowOut'})
  self.assertEqual(self.n['ML15_HeadForwardNod'],self.a['ML15_HeadForwardNod'])
  self.assertEqual({n for n in self.n if n not in self.a and not n.startswith('{')},set())
  for name in ['ML37_RightElbowIn','ML37_RightElbowOut']:
   before=self.a[name];amount=float(re.search(r'Amount ([-\d.eE]+)',before)[1])
   self.assertEqual(re.sub(r'Amount [-\d.eE]+','Amount '+format(amount*2,'.12g'),before),self.n[name])
 def test_no_cycles_in_new_paths(self):
  def visit(name,stack):
   self.assertNotIn(name,stack)
   if name not in self.n:return
   for child in re.findall(r'\bChild[01]? "([^\"]+)"',self.n[name]):visit(child,stack+[name])
  visit('ML37_RightElbowBlend',[])
 def test_world_controller_and_height_registration_unchanged(self):
  for p in list((OLD/'LogicSource/Scripts/4_World').glob('*.c'))+[OLD/'Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual(p.read_text().replace('MLADSLEAN37','MLADSLEAN38').replace('lean v37','lean v38'),(KIT/p.relative_to(OLD)).read_text())
  self.assertEqual((OLD/'WorkspaceSource/player_main.agr').read_text().replace('Locomotion_v37.agf','Locomotion_v38.agf'),(KIT/'WorkspaceSource/player_main.agr').read_text())
 def test_packed_graph_integrity_and_direct_launch(self):
  _,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes())
  self.assertEqual(entries['MLADSLeanLocomotion_v38.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertIn(b'MLADSLeanLocomotion_v38.agf',entries['player_main.agr'])
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('Mosin-Lean-v38-Logs',(KIT/'Collect-Logs.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(CommonTargetTests);suite.addTests(loader.loadTestsFromTestCase(ElbowTests));return suite
if __name__=='__main__':unittest.main()
