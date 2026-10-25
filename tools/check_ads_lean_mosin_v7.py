"""Retain pose/launcher coverage and check the NPC raised-stance regression."""
import unittest
from pathlib import Path
import check_ads_lean_mosin_v6 as previous
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v7'
previous.KIT=KIT
previous.previous.KIT=KIT
class NPCRaisedStanceRegression(unittest.TestCase):
 def test_native_raise_lock_is_scoped_and_released(self):
  code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  update=code.split('protected void MLADSLeanUpdateDemoInput',1)[1].split('override void CommandHandler',1)[0]
  self.assertLess(update.index('if (!m_MLADSLeanDemo || GetGame().IsMultiplayer())'),update.index('move.ForceStance(DayZPlayerConstants.STANCEIDX_RAISEDERECT)'))
  stop=code.split('void MLADSLeanStopDemo()',1)[1].split('protected void MLADSLeanUpdateDemoInput',1)[0]
  self.assertIn('move.ForceStance(-1)',stop)
  self.assertIn('raised = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;',code)
  self.assertNotIn('raised = true;',code)
  for item in ['native_ADS=', 'native_raised=', 'raise_complete=']:self.assertIn(item,code)
 def test_animation_assets_equal_previous_release(self):
  old=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v6'
  for name in ['WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','Pose-Snapshot.json','Pose-Spec.json']:
   self.assertEqual((KIT/name).read_bytes(),(old/name).read_bytes())
def load_tests(loader,tests,pattern):
 suite=previous.load_tests(loader,tests,pattern)
 suite.addTests(loader.loadTestsFromTestCase(NPCRaisedStanceRegression));return suite
if __name__=='__main__':unittest.main()
