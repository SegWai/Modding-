"""Regress repeated NPC stance requests and fake readiness from v9 logs."""
import sys,unittest,re,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v7 as previous
from check_ads_lean_mosin_v5 import expression
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v10'
previous.KIT=KIT
previous.previous.KIT=KIT
previous.previous.previous.KIT=KIT
class NPCStanceLifecycleRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
 def test_request_once_and_reset_on_command_restart(self):
  c=self.code;u=c.split('protected void MLADSLeanUpdateDemoInput',1)[1].split('override void CommandHandler',1)[0]
  guard=re.search(r'if \((move && !m_MLADSLeanDemoStanceRequested)\)\s*\{\s*move.ForceStance\(DayZPlayerConstants.STANCEIDX_RAISEDERECT\);\s*m_MLADSLeanDemoStanceRequested = true;',u)
  self.assertIsNotNone(guard)
  requested=False;calls=0
  # Replaying alternating observed stances must not issue another force each tick.
  for stance in [0,3]*150:
   if expression(guard[1],{'move':True,'m_MLADSLeanDemoStanceRequested':requested}):calls+=1;requested=True
  self.assertEqual(calls,1)
  self.assertIn('if (!GetCommand_Move())\n  {\n   m_MLADSLeanDemoStanceRequested = false;',u)
  self.assertIn('move.ForceStance(-1)',c)
  self.assertNotIn('OverrideRaise(HumanInputControllerOverrideType.ENABLED',c)
 def test_movement_and_ads_wait_for_real_completion(self):
  c=self.code
  block=c.split('if (m_MLADSLeanDemo)\n  {\n   raised =',1)[1].split('bool actorReady',1)[0]
  self.assertIn('ready = IsWeaponRaiseCompleted();',block)
  self.assertNotIn('ready = raised;',block)
  self.assertNotIn('ready = true;',block)
  self.assertIn('m_MLADSLeanDemoReady = raised && ready;',block)
  guard=re.search(r'if \((m_MLADSLeanDemoPaused \|\| !m_MLADSLeanDemoReady)\)\s*speed = 0;',c)
  self.assertIsNotNone(guard)
  for paused,ready,stopped in [(False,False,True),(True,True,True),(False,True,False)]:
   self.assertEqual(expression(guard[1],{'m_MLADSLeanDemoPaused':paused,'m_MLADSLeanDemoReady':ready}),stopped)
  self.assertIn('AnimSetBool(m_MLADSLeanDemoADS, m_MLADSLeanDemoReady)',c)
  self.assertIn('weapons.SetADS(m_MLADSLeanDemoReady)',c)
  self.assertIn('if (m_MLADSLeanDemoReady)\n   {\n    // Aim bit 0',c)
  for name in ['Aim','AimIK','AimUD']:self.assertIn('AnimSetFloat(m_MLADSLeanDemo'+name+', 0)',c)
 def test_npc_logs_rate_limited_with_small_diagnostics(self):
  c=self.code
  self.assertIn('if (now >= m_MLADSLeanNextReport || (localPlayer && target != m_MLADSLeanLastTarget))',c)
  for name in ['patrol_ready=','raise_transitions=','position=']:self.assertIn(name,c)
  lines=[s for s in c.splitlines() if 'string status =' in s or 'status +=' in s]
  self.assertTrue(all(s.count('+')<=2 for s in lines))
 def test_safe_default_and_measured_player_gait(self):
  c=self.code
  self.assertIn('static int DemoGait = 1;',c)
  self.assertIn('if (localPlayer && mosin && raised && (aiming || MLADSLeanSettings.Inspection))',c)
  self.assertIn('if (state.m_iMovement == 1 || state.m_iMovement == 2)',c)
  self.assertIn('MLADSLeanSettings.DemoGait = state.m_iMovement;',c)
  self.assertIn('float speed = MLADSLeanSettings.DemoGait;',c)
 def test_pose_graph_unchanged_and_packaged_hashes_current(self):
  old=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v9'
  for name in ['WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','Pose-Snapshot.json','Pose-Spec.json','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo']:
   self.assertEqual((KIT/name).read_bytes(),(old/name).read_bytes())
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
def load_tests(loader,tests,pattern):
 suite=previous.load_tests(loader,tests,pattern)
 suite.addTests(loader.loadTestsFromTestCase(NPCStanceLifecycleRegression));return suite
if __name__=='__main__':unittest.main()
