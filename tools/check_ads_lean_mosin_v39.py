"""Right-only lowered hold, native grip reconciliation and untouched elbow/height settings."""
import sys,unittest,json,re,hashlib,math
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from check_ads_lean_mosin_v36 import CommonTargetTests
from dayz_graph_formats import newnodes
import captured_pose_bridge as pose
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v39';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v38';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class LowerHoldTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.n=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text());cls.a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());cls.d=json.loads((KIT/'Right-Moving-Lower-v39.json').read_text())
 def test_authoring_hands5cm_lower_without_side_shift_rotation_or_limb_stretch(self):
  d=self.d;parents=d['parents'];c={n:{'rotation_xyz':d['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in parents};out=pose.reconstruct(d['base'],parents,c)
  for n in parents:
   for i in range(4):
    for j in range(4):self.assertAlmostEqual(out[n][i][j],d['desired'][n][i][j],delta=1e-8)
   p=parents[n]
   if p:
    a=math.dist([d['base'][n][i][3] for i in range(3)],[d['base'][p][i][3] for i in range(3)])
    b=math.dist([out[n][i][3] for i in range(3)],[out[p][i][3] for i in range(3)])
    self.assertAlmostEqual(a,b,delta=1e-8)
  for hand in ['RightHand','LeftHand']:
   for i,delta in enumerate([0,-.05,0]):
    self.assertAlmostEqual(out[hand][i][3]-d['base'][hand][i][3],delta,delta=1e-8)
    for j in range(3):self.assertAlmostEqual(out[hand][i][j],d['base'][hand][i][j],delta=1e-8)
  for n in ['Pelvis','Spine','Spine1','Spine2','Spine3','Neck','Neck1','Head','RightShoulder','LeftShoulder','LeftFoot','RightFoot']:self.assertEqual(d['base'][n],d['desired'][n])
 def test_rotation_chain_before_final_grip_matches_math_and_is_right_only(self):
  d=self.d;child='ML32_ReferenceHold_RightHand_Z';count=0
  for bone in pose.ordered(d['parents']):
   if bone not in d['rotation_corrections']:continue
   for axis,angle in zip('XYZ',d['rotation_corrections'][bone]):
    name=f'ML39_RightMovingLower_{bone}_{axis}';b=self.n[name];count+=1
    self.assertIn('Child "'+child+'"',b);self.assertIn('Op Rotate',b);self.assertNotIn('Op Translate',b)
    self.assertAlmostEqual(float(re.search(r'Amount ([-\d.eE]+)',b)[1]),-angle,places=10)
    expr=re.search(r'Expression "([^\"]+)"',b)[1]
    for amount,speed,stance,want in [(1,1,0,1),(-1,1,0,0),(1,0,0,0),(1,1,1,0)]:self.assertEqual(base.expression(expr,dict(MLADSLeanAmount=amount,MLADSLeanGate=1,MovementSpeed=speed,Stance=stance,MLADSLeanWeaponShift=1,clamp=lambda x,a,b:max(a,min(b,x)))),want)
    child=name
  self.assertEqual(count,18);self.assertIn('Child "'+child+'"',self.n['ML33_FinalGripIK'])
 def test_native_final_aim_and_grip_boolean_gate_covers_lowered_side_but_leaves_other_modes(self):
  final=self.n['ML33_FinalGripIK'];old=self.a['ML33_FinalGripIK'];clamp=lambda x,a,b:max(a,min(b,x))
  for field in ['WeightAim','WeightPrimaryChain','WeightSecondaryChain']:
   expr=re.search(field+r' "([^\"]+)"',final)[1];prev=re.search(field+r' "([^\"]+)"',old)[1]
   for lean in [-1,-.5,0,1]:
    for stance in [0,1,2]:
     for speed in [0,1]:
      env=dict(MLADSLeanAmount=lean,MLADSLeanGate=1,MovementSpeed=speed,Stance=stance,MLADSLeanWeaponShift=1,clamp=clamp)
      result=base.expression(expr,env);self.assertIsInstance(result,bool)
      if lean<=0 or stance!=0 or speed==0:self.assertEqual(result,base.expression(prev,env))
      else:self.assertTrue(result)
  for field in ['WeaponDirLr','WeaponDirUd','WeaponRoll']:self.assertEqual(re.search(field+r' "([^\"]*)"',final)[1],re.search(field+r' "([^\"]*)"',old)[1])
 def test_only_final_solver_changed_and_all_elbow_height_body_nodes_preserved(self):
  changed={n for n in self.a if n in self.n and not n.startswith('{') and self.a[n]!=self.n[n]};self.assertEqual(changed,{'ML33_FinalGripIK'})
  new={n for n in self.n if n not in self.a and not n.startswith('{')};self.assertEqual(len(new),18);self.assertTrue(all(n.startswith('ML39_RightMovingLower_') for n in new))
  for node in ['ML37_CaptureRightGrip','ML37_RightElbowIn','ML37_RightElbowOut','ML37_RestoreRightGrip','ML37_RightElbowBlend','ML36_WalkingHeight95','MovementRasIK']:self.assertEqual(self.a[node],self.n[node])
 def test_shared_world_controller_and_range_unchanged(self):
  for p in list((OLD/'LogicSource/Scripts/4_World').glob('*.c'))+[OLD/'Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual(p.read_text().replace('MLADSLEAN38','MLADSLEAN39').replace('lean v38','lean v39'),(KIT/p.relative_to(OLD)).read_text())
  self.assertEqual((OLD/'WorkspaceSource/player_main.agr').read_text().replace('Locomotion_v38.agf','Locomotion_v39.agf'),(KIT/'WorkspaceSource/player_main.agr').read_text())
 def test_packaged_graph_hashes_and_direct_launcher(self):
  _,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes());self.assertEqual(entries['MLADSLeanLocomotion_v39.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertIn(b'MLADSLeanLocomotion_v39.agf',entries['player_main.agr'])
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('Mosin-Lean-v39-Logs',(KIT/'Collect-Logs.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(CommonTargetTests);suite.addTests(loader.loadTestsFromTestCase(LowerHoldTests));return suite
if __name__=='__main__':unittest.main()
