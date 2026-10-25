"""Check explicit NPC graph ownership and unchanged player expression semantics."""
import sys,unittest,re,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v13'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v11'
base.KIT=KIT
class RegisteredDemoControllerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  cls.graph=(KIT/'WorkspaceSource/locomotion.agf').read_text()
 def test_player_graph_is_recoverable_exactly_when_demo_disabled(self):
  # Simplify each newly introduced identity at DemoActive=0.
  g=self.graph
  for variable in ['Raised','ADS']:
   g=g.replace('('+variable+' || MLADSLeanCanary > 0.9)',variable)
  for variable in ['AimX','AimY','AimIKX']:
   g=g.replace('('+variable+'*(1.0-clamp((MLADSLeanCanary-0.8)*5.0, 0.0, 1.0)))',variable)
  for bit in range(3):
   g=g.replace('(isbitset(ArmIK, '+str(bit)+') || MLADSLeanCanary > 0.9)','isbitset(ArmIK, '+str(bit)+')')
  self.assertNotIn('MLADSLeanDemoActive',g)
  self.assertEqual(g,(OLD/'WorkspaceSource/locomotion.agf').read_text())
 def test_demo_selects_same_ads_branches_when_native_flags_false(self):
  routes=json.loads((KIT/'Demo-Graph-Routing.json').read_text())['changed_expressions']
  tested=0
  for route in routes:
   if route['property']!='Condition' or route['before'] not in ['Raised','ADS','!Raised','!ADS']:continue
   for active in [0,1]:
    got=base.expression(route['after'],{'Raised':False,'ADS':False,'MLADSLeanCanary':1 if active else .731})
    self.assertEqual(bool(got),bool(active) != route['before'].startswith('!'))
   tested+=1
  self.assertGreater(tested,12)
  old=(OLD/'WorkspaceSource/locomotion.agf').read_text()
  self.assertEqual(re.findall(r'Child[01]? "([^\"]+)"',old),re.findall(r'Child[01]? "([^\"]+)"',self.graph))
 def test_existing_registered_control_and_template_used(self):
  agr=(KIT/'WorkspaceSource/player_main.agr').read_bytes()
  self.assertEqual(agr,(OLD/'WorkspaceSource/player_main.agr').read_bytes())
  self.assertNotIn('MLADSLeanDemoActive',self.graph)
  self.assertNotIn('MLADSLeanDemoActive',self.code)
  self.assertIn('float demoGraphValue = 0.731;',self.code)
  self.assertIn('demoGraphValue = 1;',self.code)
  self.assertIn('AnimSetFloat(m_MLADSLeanCanaryVar, demoGraphValue)',self.code)
  self.assertIn('if (m_MLADSLeanDemo && m_MLADSLeanDemoNativeBound)',self.code)
 def test_no_native_raise_wait_or_repeated_force(self):
  c=self.code
  self.assertNotIn('ForceStance(',c)
  self.assertNotIn('OverrideRaise(HumanInputControllerOverrideType.ENABLED',c)
  demo=c.split('bool demoControllerActive = false;',1)[1].split('bool actorReady',1)[0]
  self.assertNotIn('IsWeaponRaiseCompleted()',demo)
  self.assertIn('m_MLADSLeanDemoReady = demoControllerActive && m_MLADSLeanDemoWarmup >= 0.4;',demo)
  self.assertIn('raised = demoControllerActive;',demo)
  # It is an explicit graph warmup, never logged as native weapon completion.
  self.assertNotIn('demo_native_raise_complete',c)
  self.assertIn('" raise_complete=" + IsWeaponRaiseCompleted()',c)
  for active,seconds,expected in [(False,10,False),(True,.39,False),(True,.4,True),(True,10,True)]:
   self.assertEqual(base.expression('demoControllerActive && m_MLADSLeanDemoWarmup >= 0.4',{'demoControllerActive':active,'m_MLADSLeanDemoWarmup':seconds}),expected)
 def test_demo_cleanup_and_rate_limit(self):
  c=self.code
  stop=c.split('void MLADSLeanStopDemo()',1)[1].split('protected void MLADSLeanUpdateDemoInput',1)[0]
  self.assertIn('m_MLADSLeanDemoGraphNeedsReset = true;',stop)
  handler=c.split('override void CommandHandler',1)[1]
  self.assertLess(handler.index('AnimSetFloat(m_MLADSLeanCanaryVar, 0.731)'),handler.index('(!localPlayer && !m_MLADSLeanDemo)'))
  self.assertIn('(localPlayer && target != m_MLADSLeanLastTarget)',handler)
  for line in c.splitlines():
   if 'status +=' in line or 'string status =' in line:self.assertLessEqual(line.count('+'),2)
 def test_authored_pose_and_native_walking_ik_unchanged(self):
  for file in ['Pose-Snapshot.json','Pose-Spec.json','Symmetry-Measurements.json','Mode-Coverage.json']:
   self.assertEqual((KIT/file).read_bytes(),(OLD/file).read_bytes())
  nodes=newnodes(self.graph);old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text())
  self.assertEqual(nodes['MovementRasIK'],old['MovementRasIK'])
  for name in nodes:
   if name.startswith('ML5_'):self.assertEqual(nodes[name],old[name],name)
  self.assertIn('WeaponRoll "8.0*MLADSLeanAmount*MLADSLeanGate"',self.graph)
 def test_change_detection_arguments_match_known_good_graph(self):
  def arguments(g):return re.findall(r'HasVariableChanged\(\s*([^,)\n]+)',g)
  def valid(g):return all(re.fullmatch(r'[A-Za-z_]\w*',v.strip()) for v in arguments(g))
  broken=(ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v12/WorkspaceSource/locomotion.agf').read_text()
  self.assertFalse(valid(broken))
  self.assertTrue(valid(self.graph))
  self.assertEqual(arguments(self.graph),arguments((OLD/'WorkspaceSource/locomotion.agf').read_text()))
 def test_every_custom_expression_control_exists_in_restored_schema(self):
  agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
  declared=set(re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr))
  exprs=re.findall(r'(?m)^\s*(?:Expression|Condition|StartCondition|InterruptExpr|BlendWeight|Weight\w+|Weapon\w+|Value[XY]) "(.*)"',self.graph)
  refs=set(re.findall(r'\bMLADSLean\w+\b',' '.join(exprs)))
  self.assertEqual(refs,{'MLADSLeanGate','MLADSLeanCanary','MLADSLeanAmount'})
  self.assertTrue(refs <= declared)
 def test_direct_launcher_correct_log_version_and_pbos(self):
  cmd=(KIT/'Launch-Mosin-Lean-Test.cmd').read_text()
  self.assertNotRegex(cmd.lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertIn('Mosin-Lean-v13-Logs',(KIT/'Collect-Logs.ps1').read_text())
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(RegisteredDemoControllerTests));return suite
if __name__=='__main__':unittest.main()
