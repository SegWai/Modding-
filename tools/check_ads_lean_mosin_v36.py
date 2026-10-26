"""Walking-height controller, native foot-solver ordering and unchanged successful gun pose."""
import sys,unittest,json,re,math,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v36';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v35';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class CommonTargetTests(base.ExpandedLeanTests):
 def test_crouch_legs_and_walking_steps_remain_native(self):
  actual=self.nodes['MovementRasIK']
  try:
   # The only intended foot-node change is its new upstream pelvis stage.
   self.nodes['MovementRasIK']=actual.replace('Child "ML36_WalkingHeight95"','Child "MovementRasSTM"')
   super().test_crouch_legs_and_walking_steps_remain_native()
  finally:self.nodes['MovementRasIK']=actual
 def test_one_common_weapon_roll_target(self):self.assertEqual(re.findall(r'WeaponRoll "([^\"]+)"',self.graph),['8.0*MLADSLeanAmount*MLADSLeanGate']*2)
class WalkingHeightTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.n=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text());cls.a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());cls.c=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
 def test_only_shared_walking_pelvis_stage_added_before_existing_native_foot_ik(self):
  self.assertEqual({n for n in self.a if n in self.n and not n.startswith('{') and self.a[n]!=self.n[n]},{'MovementRasIK'})
  self.assertIn('Child "ML36_WalkingHeight95"',self.n['MovementRasIK']);self.assertIn('Child "MovementRasSTM"',self.n['ML36_WalkingHeight95'])
  self.assertEqual(self.n['MovementRasIK'].replace('Child "ML36_WalkingHeight95"','Child "MovementRasSTM"'),self.a['MovementRasIK'])
  for node in ['NormalWeaponIK','ML33_FinalGripIK']+[n for n in self.a if n.startswith('ML32_ReferenceHold_')]:self.assertEqual(self.a[node],self.n[node],node)
  self.assertRegex(self.n['ML36_WalkingHeight95'],r'Bone "Pelvis"\s+Axis Y\s+Space Model\s+Op Translate\s+Amount 1.0')
 def test_scope_is_both_lean_sides_but_not_crouch_idle_or_native_comparison(self):
  expr=re.search(r'Expression "([^\"]+)"',self.n['ML36_WalkingHeight95'])[1]
  for lean,gate,speed,stance,lift,wanted in [(-1,1,1,0,.08,.08),(1,1,1,0,.08,.08),(-1,1,0,0,.08,0),(-1,1,1,1,.08,0),(-1,0,1,0,.08,0),(0,1,1,0,.08,0),(.5,1,1,0,.08,.04)]:
   self.assertAlmostEqual(base.expression(expr,dict(MLADSLeanHeightLift=lift,MLADSLeanAmount=lean,MLADSLeanGate=gate,MovementSpeed=speed,Stance=stance,abs=abs,clamp=lambda x,a,b:max(a,min(b,x)))),wanted)
  self.assertNotIn('MLADSLeanCanary',expr)
 def test_registration_preserves_existing_variable_order_and_safe_writes(self):
  a=(OLD/'WorkspaceSource/player_main.agr').read_text();b=(KIT/'WorkspaceSource/player_main.agr').read_text()
  self.assertEqual(re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',b)[:-1],re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',a))
  self.assertRegex(b,r'AnimSrcGCTVarFloat MLADSLeanHeightLift \{\s+DefaultValue 0\s+MinValue -0.06\s+MaxValue 0.15')
  for other in ['m_MLADSLeanGateVar','m_MLADSLeanCanaryVar','m_MLADSLeanAmountVar','m_MLADSLeanNativeLeanVar','m_MLADSLeanNativeMoveVar','m_MLADSLeanWeaponShiftVar']:self.assertIn('m_MLADSLeanHeightVar != '+other,self.c)
  self.assertIn('m_MLADSLeanHeightVar >= 0',self.c)
  handler=self.c.split('override void CommandHandler',1)[1].split('protected void MLADSLeanCalibrateStandingHeight',1)[0]
  self.assertLess(handler.index('super.CommandHandler('),handler.index('AnimSetFloat(m_MLADSLeanHeightVar, m_MLADSLeanHeightLift)'))
 def test_shared_calibration_has_neutral_standing_guard_and_observed_ratio(self):
  cal=self.c.split('protected void MLADSLeanCalibrateStandingHeight()',1)[1].split('// These are observed',1)[0]
  for text in ['m_iMovement != 0','m_fLeaning) > 0.02','referenceHead[1] < 1.25','m_MLADSLeanStandingHeadY = referenceHead[1]']:self.assertIn(text,cal)
  self.assertIn('MLADSLeanCalibrateStandingHeight();',self.c)
  self.assertIn('m_MLADSLeanStandingHeadY * 0.95',self.c)
  self.assertIn('observed_head_height_ratio=',self.c)
  for line in self.c.splitlines():
   if 'status +=' in line or 'referenceMessage +=' in line:self.assertLessEqual(line.count('+'),2)
 def test_controller_converges_retains_gait_bob_and_respects_limits(self):
  # Evaluate the actual scalar source expressions under a simple delayed plant.
  src=self.c
  def rhs(var):return re.search(r'(?:float )?'+var+r' = ([^;]+);',src)[1]
  clamp=lambda x,a,b:max(a,min(b,x))
  def step(lift,reference,observed,dt):
   env=dict(pDt=dt,m_MLADSLeanStandingHeadY=reference,m_MLADSLeanCurrentHeadY=observed,m_MLADSLeanHeightLift=lift,Math=type('M',(),{'Clamp':staticmethod(clamp)}))
   for var in ['heightStep','heightTarget','heightError','heightGain','heightChange']:
    env[var]=base.expression(rhs(var),env)
   # First height-lift assignment is the active controller branch.
   return base.expression(rhs('m_MLADSLeanHeightLift'),env)
  self.assertAlmostEqual(step(0,1.6,.1,1/30),.12/30)
  for reference in [1.55,1.7]:
   lift=0;values=[]
   for i in range(360):
    native=reference*.90+.015*math.sin(i/30*math.tau*2)
    observed=native+lift;values.append(observed)
    lift=step(lift,reference,observed,1/30)
    self.assertTrue(-.06<=lift<=.15)
   self.assertAlmostEqual(sum(values[-30:])/30/reference,.95,delta=.001)
   self.assertGreater(max(values[-30:])-min(values[-30:]),.02)
  lift=0
  for i in range(300):lift=step(lift,1.6,.9+lift,1/30)
  self.assertAlmostEqual(lift,.15)
 def test_range_and_packed_integrity_preserved(self):
  p='LogicSource/Scripts/4_World/MLADSLeanPlayer.c'
  self.assertEqual((OLD/p).read_text().split('protected bool m_MLADSLeanRangeTarget;',1)[1].replace('MLADSLEAN35','MLADSLEAN36'),(KIT/p).read_text().split('protected bool m_MLADSLeanRangeTarget;',1)[1])
  for p in ['Missions/MLADSLeanMosin.ChernarusPlus/init.c','LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c']:self.assertEqual((OLD/p).read_text().replace('MLADSLEAN35','MLADSLEAN36').replace('lean v35','lean v36'),(KIT/p).read_text())
  _,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes());self.assertEqual(entries['MLADSLeanLocomotion_v36.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(CommonTargetTests);suite.addTests(loader.loadTestsFromTestCase(WalkingHeightTests));return suite
if __name__=='__main__':unittest.main()
