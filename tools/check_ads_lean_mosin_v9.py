"""NPC input corrections with preserved pose, launcher and lifecycle coverage."""
import sys,unittest,re,json
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v7 as previous
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v9'
previous.KIT=KIT
previous.previous.KIT=KIT
previous.previous.previous.KIT=KIT
class NPCInputRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
 def test_forward_aim_and_both_weapon_hands(self):
  c=self.code
  self.assertIn('BindVariableInt("ArmIK")',c)
  self.assertIn('m_MLADSLeanDemoNativeBound = m_MLADSLeanDemoArmIK >= 0',c)
  block=c.split('if (m_MLADSLeanDemo && m_MLADSLeanDemoNativeBound)',1)[1].split('string status',1)[0]
  self.assertIn('AnimSetInt(m_MLADSLeanDemoArmIK, 7)',block)
  for field in ['Aim','AimIK','AimUD']:self.assertIn('AnimSetFloat(m_MLADSLeanDemo'+field+', 0)',block)
  self.assertNotIn('90 * m_MLADSLeanDemoAmount',c)
  graph=(KIT/'WorkspaceSource/locomotion.agf').read_text()
  for bit in range(3):self.assertIn('isbitset(ArmIK, '+str(bit)+')',graph)
 def test_remembers_only_moving_local_raised_mosin_gait(self):
  c=self.code
  self.assertIn('static int DemoGait = 2;',c)
  self.assertIn('if (localPlayer && mosin && raised && (aiming || MLADSLeanSettings.Inspection))',c)
  self.assertIn('if (state.m_iMovement == 1 || state.m_iMovement == 2)',c)
  self.assertIn('MLADSLeanSettings.DemoGait = state.m_iMovement;',c)
  self.assertIn('float speed = MLADSLeanSettings.DemoGait;',c)
  self.assertIn('if (m_MLADSLeanDemoPaused)\n   speed = 0;',c)
  update=c.split('protected void MLADSLeanUpdateDemoInput',1)[1].split('override void CommandHandler',1)[0]
  self.assertIn('if (!m_MLADSLeanDemo || GetGame().IsMultiplayer())',update)
  self.assertNotIn('SetPosition(',c)
 def test_diagnostics_stay_small(self):
  lines=[s for s in self.code.splitlines() if 'string status =' in s or 'status +=' in s]
  self.assertGreaterEqual(len(lines),9)
  self.assertTrue(all(s.count('+')<=2 for s in lines))
 def test_graph_pose_and_workspace_pbo_unchanged(self):
  old=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v8'
  for name in ['WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','Pose-Snapshot.json','Pose-Spec.json','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo']:
   self.assertEqual((old/name).read_bytes(),(KIT/name).read_bytes(),name)
 def test_packed_files_match_validation_hashes(self):
  import hashlib
  d=json.loads((KIT/'validation.json').read_text())
  for path,digest in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/path).read_bytes()).hexdigest(),digest)
def load_tests(loader,tests,pattern):
 suite=previous.load_tests(loader,tests,pattern)
 suite.addTests(loader.loadTestsFromTestCase(NPCInputRegression));return suite
if __name__=='__main__':unittest.main()
