"""AK74 full-auto/loadout/ammo coverage plus shared reference-head correction."""
import sys,unittest,re,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v22'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v21'
base.KIT=KIT
class AK74AndReferenceHeadTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.player=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  cls.ammo=(KIT/'LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c').read_text()
  cls.mission=(KIT/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
 def test_both_actors_use_same_ak_attachment_helper(self):
  m=self.mission;a=self.ammo
  self.assertIn('player.GetHumanInventory().CreateInHands("AK74")',m)
  self.assertIn('m_MLADSLeanNPC.GetHumanInventory().CreateInHands("AK74")',m)
  self.assertIn('MLADSLeanRangeAmmo.EquipAK74(ak)',m)
  self.assertIn('MLADSLeanRangeAmmo.EquipAK74(npcMosin)',m)
  for item in ['AK74_WoodBttstck','AK74_Hndgrd','AK_Suppressor','KobraOptic','Battery9V']:
   self.assertIn('CreateAttachment("'+item+'")',a)
  self.assertIn('SpawnAmmo("Mag_AK74_30Rnd")',a)
  self.assertIn('player.GetInventory().CreateAttachment("Mosin9130")',m)
  self.assertIn('CreateInInventory("PSO1Optic")',m)
 def test_select_actual_automatic_mode_not_assumed_index(self):
  a=self.ammo.split('static void EquipAK74',1)[1]
  self.assertIn('mode < weapon.GetMuzzleModeCount(muzzle)',a)
  self.assertIn('weapon.SetCurrentMode(muzzle, mode)',a)
  self.assertIn('if (weapon.GetCurrentModeAutoFire(muzzle))',a)
  self.assertIn('automatic = true;\n    break;',a)
  self.assertIn('if (!automatic)\n   weapon.SetCurrentMode(muzzle, originalMode);',a)
  self.assertNotIn('weapon.SetCurrentMode(muzzle, 1)',a)
 def test_full_auto_refill_precedes_busy_fsm_guard(self):
  a=self.ammo.split('static void EquipAK74',1)[0]
  self.assertIn('!weapon.IsKindOf("Mosin9130") && !weapon.IsKindOf("AK74")',a)
  self.assertLess(a.index('if (magazine)'),a.index('GetWeaponManager().IsRunning()'))
  for call in ['magazine.ServerSetAmmoMax()','magazine.LocalSetAmmoMax()']:
   self.assertIn(call,a)
  self.assertIn('PushCartridgeToInternalMagazine',a) # preserve Mosin reserve
  self.assertNotIn('PushCartridgeToChamber',a)
  self.assertIn('CallLater(MLADSLeanRefreshAmmo, 100, true)',self.mission)
 def test_ak74_and_mosin_use_same_existing_pose_gate(self):
  self.assertIn('bool mosin = held && (held.IsKindOf("Mosin9130") || held.IsKindOf("AK74"));',self.player)
  target=re.search(r'bool target = ([^;]+);',self.player)[1]
  self.assertIn('&& mosin &&',target)
  self.assertIn('m_MLADSLeanDemoNativeBound && mosin;',self.player)
  self.assertIn('if (localPlayer && mosin && raised',self.player)
 def test_marked_head_adjustments_only(self):
  old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
  self.assertEqual(set(old),set(new))
  self.assertEqual({n for n in old if not n.startswith('{') and old[n]!=new[n]}, {'ML20_RightLeanHeadExposure','ML21_RightMovingHeadLift'})
  self.assertEqual(new['ML20_RightLeanHeadExposure'],old['ML20_RightLeanHeadExposure'].replace('Amount -0.025','Amount -0.035'))
  self.assertEqual(new['ML21_RightMovingHeadLift'],old['ML21_RightMovingHeadLift'].replace('Amount 0.006','Amount 0.026'))
  for n in ['NormalWeaponIK','MovementRasIK','ML5_StandWalk_left_Pelvis_Translate_Y','ML5_StandWalk_right_Pelvis_Translate_Y']:
   self.assertEqual(new[n],old[n])
  self.assertEqual((KIT/'WorkspaceSource/player_main.agr').read_bytes(),(OLD/'WorkspaceSource/player_main.agr').read_bytes())
 def test_ragdoll_respawn_and_footwork_preserved(self):
  old=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  new=self.player.replace('MLADSLEAN22','MLADSLEAN21')
  self.assertEqual(new.split('protected bool m_MLADSLeanRangeTarget;',1)[1],old.split('protected bool m_MLADSLeanRangeTarget;',1)[1])
  for item in ['CallLater(MLADSLeanSpawnTarget, 1000, false)','m_MLADSLeanCorpses.Count() > 4','m_MLADSLeanNPC.SetAllowDamage(true)']:
   self.assertIn(item,self.mission)
  self.assertIn('GetBoneTransformMS(headIndex, headBasis)',self.player)
  for axis in ['x','y','z']:self.assertIn('head_basis_'+axis+'_ms=',self.player)
 def test_native_control_schema_and_layer_regressions_remain_fixed(self):
  self.assertEqual(self.player.count('modded class PlayerBase'),1)
  self.assertIn('void MLADSLeanRangeSampleMotion()',self.player)
  self.assertNotIn('(GetPosition() - m_MLADSLeanRangeLastPosition) /',self.player)
  self.assertNotIn('MLADSLeanDemoActive',(KIT/'WorkspaceSource/locomotion.agf').read_text())
 def test_pbos_launcher_and_current_log_label(self):
  validation=json.loads((KIT/'validation.json').read_text())
  for p,h in validation['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertIn('Mosin-Lean-v22-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(AK74AndReferenceHeadTests));return suite
if __name__=='__main__':unittest.main()
