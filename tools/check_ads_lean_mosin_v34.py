"""Final native grip solve ordering/gating and unchanged reference-pose regression checks."""
import sys,unittest,json,hashlib,re
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v34';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v33';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class FinalGripTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=(KIT/'WorkspaceSource/locomotion.agf').read_text();cls.n=newnodes(cls.s);cls.a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());cls.f=cls.n['ML33_FinalGripIK']
 def test_order_no_cycle_and_unchanged_hold_body_and_aim(self):
  last=json.loads((OLD/'Reference-Hold-v32.json').read_text())['graph_output_node']
  self.assertIn(f'Child "{last}"',self.f)
  self.assertIn('Child "ML33_FinalGripIK"',self.n['ML15_HeadForwardNod'])
  changed={n for n in self.a if n in self.n and not n.startswith('{') and self.a[n]!=self.n[n]}
  self.assertEqual(changed,{'ML33_FinalGripIK'})
  self.assertEqual({n for n in self.n if n not in self.a and not n.startswith('{')},set())
  seen=set();cur='ML15_HeadForwardNod'
  while cur in self.n:
   self.assertNotIn(cur,seen);seen.add(cur)
   child=re.search(r'\bChild "([^"]+)"',self.n[cur])
   if not child:break
   cur=child[1]
  self.assertIn('ML33_FinalGripIK',seen);self.assertIn('NormalWeaponIK',seen)
 def test_grip_only_preserves_aim_cant_and_uses_native_targets(self):
  self.assertIn('WeightAim "false"',self.f)
  self.assertIn('WeaponRoll ""',self.f)
  self.assertIn('WeaponDirLr "0.0"',self.f);self.assertIn('WeaponDirUd "0.0"',self.f)
  self.assertIn('IkconfigName "ML33_FinalGripConfig"',self.f)
  for target in ['ikpose_chainoffset = RightHandOrigin','ikpose_weaponoffset = RightHand_Dummy','ikpose_secchainoffset = LeftHandIKTarget','chain = RightArm, RightArmRoll, RightForeArm, RightForeArmRoll, RightHand','secchain = LeftArm, LeftArmRoll, LeftForeArm, LeftForeArmRoll, LeftHand']:self.assertIn(target,self.f)
  self.assertIn('outputweaponoffsettobuffer = true',self.f)
  self.assertEqual(self.s.count('outputweaponoffsettobuffer = true'),1)
 def test_shared_chain_weights_follow_reference_hold_activation(self):
  primary=re.search(r'WeightPrimaryChain "([^"]+)"',self.f)[1];secondary=re.search(r'WeightSecondaryChain "([^"]+)"',self.f)[1];self.assertEqual(primary,secondary)
  for amount,gate,speed,enabled,want in [(-1,1,1,1,1),(1,1,1,1,0),(-1,1,0,1,0),(-1,0,1,1,0),(-1,1,1,0,0),(-.5,1,1,1,.5)]:
   result=base.expression(primary,dict(MLADSLeanAmount=amount,MLADSLeanGate=gate,MovementSpeed=speed,MLADSLeanWeaponShift=enabled,clamp=lambda x,a,b:max(a,min(b,x))))
   self.assertIsInstance(result,bool)
   self.assertEqual(result,bool(want))
  self.assertNotIn('MLADSLeanCanary',primary)
 def test_world_controller_range_and_authoring_values_unchanged(self):
  for p in list((OLD/'LogicSource/Scripts/4_World').glob('*.c'))+[OLD/'Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual(p.read_text().replace('MLADSLEAN33','MLADSLEAN34').replace('lean v33','lean v34'),(KIT/p.relative_to(OLD)).read_text())
  self.assertEqual((OLD/'Reference-Hold-v32.json').read_bytes(),(KIT/'Reference-Hold-v32.json').read_bytes())
 def test_only_boolean_fields_change_in_final_solver(self):
  old=self.a['ML33_FinalGripIK'];new=self.f
  old=old.replace('WeightAim "0.0"','WeightAim "false"')
  for field in ['WeightPrimaryChain','WeightSecondaryChain']:
   old=re.sub(field+r' "([^\"]+)"',lambda m:field+' "('+m[1]+') > 0.001"',old)
  self.assertEqual(old,new)
 def test_packed_graph_and_integrity(self):
  _,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes())
  self.assertEqual(entries['MLADSLeanLocomotion_v34.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertIn(b'MLADSLeanLocomotion_v34.agf',entries['player_main.agr'])
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('Mosin-Lean-v34-Logs',(KIT/'Collect-Logs.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests);suite.addTests(loader.loadTestsFromTestCase(FinalGripTests));return suite
if __name__=='__main__':unittest.main()
