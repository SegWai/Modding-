"""Check native head-tilt suppression eligibility, restoration and head-only graph scope."""
import sys,unittest,re,json,math,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v15'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v14'
base.KIT=KIT
class NativeHeadTiltTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  cls.graph=(KIT/'WorkspaceSource/locomotion.agf').read_text()
 def suppress(self,**overrides):
  env={'MLADSLeanSettings.HeadCorrection':True,'MLADSLeanSettings.Enabled':True,'m_MLADSLeanBound':True,'m_MLADSLeanGate':1,'m_MLADSLeanAmount':-1}
  env.update(overrides)
  text=self.code.split('bool suppressHeadTilt =',1)[1].split('bool requestedHeadADS',1)[0]
  expressions=re.findall(r'(?:suppressHeadTilt =)?\s*([^;]+);',text)
  for expr in expressions:
   expr=expr.strip()
   if expr.startswith('suppressHeadTilt ='):expr=expr.split('=',1)[1]
   expr=expr.replace('Math.AbsFloat','abs')
   # Replace dotted settings with legal Python names.
   values={'abs':abs}
   for i,key in enumerate(env):expr=expr.replace(key,'value_'+str(i));values['value_'+str(i)]=env[key]
   values['suppressHeadTilt']=env.get('suppressHeadTilt',False)
   env['suppressHeadTilt']=bool(base.expression(expr,values))
  return env['suppressHeadTilt']
 def test_suppression_only_during_custom_nonzero_lean(self):
  for lean in [-1,-.5,.5,1]:self.assertTrue(self.suppress(m_MLADSLeanAmount=lean))
  for key,value in [('MLADSLeanSettings.HeadCorrection',False),('MLADSLeanSettings.Enabled',False),('m_MLADSLeanBound',False),('m_MLADSLeanGate',0),('m_MLADSLeanAmount',0)]:
   self.assertFalse(self.suppress(**{key:value}),key)
 def test_shared_post_native_control_and_restoration(self):
  c=self.code
  self.assertLess(c.index('super.CommandHandler('),c.index('bool suppressHeadTilt ='))
  start=c.index('bool suppressHeadTilt =');end=c.index('// Keep each diagnostic expression',start)
  block=c[start:end]
  self.assertIn('bool requestedHeadADS = nativeADS;',block)
  self.assertIn('if (m_MLADSLeanDemo)\n   requestedHeadADS = m_MLADSLeanDemoReady;',block)
  self.assertIn('weapons.SetADS(requestedHeadADS && !suppressHeadTilt);',block)
  for ads in [False,True]:
   for suppressed in [False,True]:
    result=base.expression('requestedHeadADS && !suppressHeadTilt',{'requestedHeadADS':ads,'suppressHeadTilt':suppressed})
    self.assertEqual(result,ads and not suppressed)
  self.assertNotIn('weapons.SetADS(m_MLADSLeanDemoReady)',c)
  self.assertEqual(c.count('GetCommandModifier_Weapons()'),2)
  old=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  for call in ['SetIronsights(','ExitSights(','ResetADS(','SelectPlayer(']:self.assertEqual(c.count(call),old.count(call))
 def test_head_roll_removed_and_forward_nod_retained(self):
  n=newnodes(self.graph);old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text())
  self.assertNotIn('ML14_HeadCounterRoll',self.graph)
  self.assertIn('Child "ML15_HeadForwardNod"',n['SickHotColdQ'])
  node=n['ML15_HeadForwardNod']
  self.assertIn('Child "NormalWeaponIK"',node)
  self.assertEqual(re.findall(r'Bone "([^"]+)"',node),['Head'])
  self.assertIn('Expression "abs(MLADSLeanAmount)*MLADSLeanGate"',node)
  amount=float(re.search(r'Amount ([-0-9.eE]+)',node)[1])
  self.assertAlmostEqual(math.degrees(amount),-5,places=6)
  for name,body in old.items():
   if name.startswith('{') or name in ['ML14_HeadCounterRoll','ML14_HeadForwardNod','SickHotColdQ']:continue
   self.assertEqual(n[name],body,name)
 def test_working_gct_legs_and_gun_preserved(self):
  for name in ['WorkspaceSource/player_main.agr','Static-Pose-Snapshot.json','Pose-Snapshot.json','Mode-Coverage.json']:
   self.assertEqual((KIT/name).read_bytes(),(OLD/name).read_bytes(),name)
  self.assertIn('WeaponRoll "8.0*MLADSLeanAmount*MLADSLeanGate"',self.graph)
  self.assertNotIn('MLADSLeanDemoActive',self.graph)
 def test_f6_comparison_and_diagnostics(self):
  keys=(KIT/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
  self.assertIn('if (key == KeyCode.KC_F6 && !m_MLADSLeanF6Down)',keys)
  self.assertIn('m_MLADSLeanF6Down = true;',keys)
  self.assertIn('MLADSLeanSettings.HeadCorrection = !MLADSLeanSettings.HeadCorrection;',keys)
  self.assertIn('if (key == KeyCode.KC_F6)\n   m_MLADSLeanF6Down = false;',keys)
  self.assertIn('static bool HeadCorrection = true;',self.code)
  self.assertIn('head_tilt_suppressed=',self.code)
  for s in self.code.splitlines():
   if 'string status =' in s or 'status +=' in s:self.assertLessEqual(s.count('+'),2)
 def test_current_pbo_hashes_and_direct_launcher(self):
  data=json.loads((KIT/'validation.json').read_text())
  for p,h in data['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  cmd=(KIT/'Launch-Mosin-Lean-Test.cmd').read_text()
  self.assertNotRegex(cmd.lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v15-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(NativeHeadTiltTests));return suite
if __name__=='__main__':unittest.main()
