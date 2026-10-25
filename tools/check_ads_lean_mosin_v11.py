"""Persistent NPC raise input initialized once; preserve genuine readiness gate."""
import sys,unittest,re
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v10 as previous
from check_ads_lean_mosin_v5 import expression
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v11'
module=previous
while module:
 module.KIT=KIT
 module=getattr(module,'previous',None)
class NPCPersistentRaiseRegression(previous.NPCStanceLifecycleRegression):
 def test_request_once_and_reset_on_command_restart(self):
  c=self.code
  u=c.split('protected void MLADSLeanUpdateDemoInput',1)[1].split('override void CommandHandler',1)[0]
  match=re.search(r'if \((move && !m_MLADSLeanDemoStanceRequested)\)\s*\{([^{}]+)\}',u)
  self.assertIsNotNone(match)
  block=match[2]
  self.assertIn('move.ForceStance(DayZPlayerConstants.STANCEIDX_RAISEDERECT)',block)
  call='input.OverrideRaise(HumanInputControllerOverrideType.ENABLED, true);'
  self.assertEqual(c.count(call),1)
  self.assertIn(call,block)
  self.assertIn('m_MLADSLeanDemoStanceRequested = true;',block)
  requested=False;stance_calls=0;raise_calls=0
  for frame in range(300):
   if expression(match[1],{'move':True,'m_MLADSLeanDemoStanceRequested':requested}):
    stance_calls+=1;raise_calls+=1;requested=True
  self.assertEqual((stance_calls,raise_calls),(1,1))
  self.assertIn('if (!GetCommand_Move())\n  {\n   m_MLADSLeanDemoStanceRequested = false;',u)
  stop=c.split('void MLADSLeanStopDemo()',1)[1].split('protected void MLADSLeanUpdateDemoInput',1)[0]
  self.assertIn('input.OverrideRaise(HumanInputControllerOverrideType.DISABLED, false)',stop)
  self.assertIn('move.ForceStance(-1)',stop)
 def test_only_expected_startup_and_logging_changes(self):
  old=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v10'
  for name in ['WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','Pose-Snapshot.json','Pose-Spec.json']:
   self.assertEqual((old/name).read_bytes(),(KIT/name).read_bytes())
  for field in ['native_raise_input=','changing_stance=','demo_native_raise_complete patrol_start_allowed']:
   self.assertIn(field,self.code)
def load_tests(loader,tests,pattern):
 suite=previous.previous.load_tests(loader,tests,pattern)
 suite.addTests(loader.loadTestsFromTestCase(NPCPersistentRaiseRegression));return suite
if __name__=='__main__':unittest.main()
