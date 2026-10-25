"""Offline range invariants, head-only graph changes, native-API/package checks."""
import sys,unittest,json,re,math,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes,end
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v17'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v16'
base.KIT=KIT
class RangeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.world=(KIT/'LogicSource/Scripts/4_World/MLADSLeanRangeTarget.c').read_text()
  cls.mission=(KIT/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
  cls.player=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
 def test_only_right_head_graph_changes(self):
  old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
  changed={n for n in old if not n.startswith('{') and old[n]!=new[n]}
  expected={f'ML5_{mode}_right_Head_Rotate_Z' for mode in ['StandIdle','StandWalk','CrouchIdle','CrouchWalk']}
  self.assertEqual(changed,expected);self.assertEqual(set(old),set(new))
  for n in expected:
   a=float(re.search(r'Amount ([-+0-9.eE]+)',old[n])[1]);b=float(re.search(r'Amount ([-+0-9.eE]+)',new[n])[1])
   self.assertAlmostEqual(math.degrees(b-a),-5,places=6)
  self.assertEqual((KIT/'WorkspaceSource/player_main.agr').read_bytes(),(OLD/'WorkspaceSource/player_main.agr').read_bytes())
 def test_equipment_is_attached_and_only_npc_damage_enabled(self):
  m=self.mission
  for item in ['PUScopeOptic','ImprovisedSuppressor']:self.assertIn('mosin.GetInventory().CreateAttachment("'+item+'")',m)
  self.assertIn('player.SetAllowDamage(false)',m)
  self.assertIn('m_MLADSLeanNPC.SetAllowDamage(true)',m)
  self.assertNotIn('m_MLADSLeanNPC.SetAllowDamage(false)',m)
  self.assertIn('m_MLADSLeanNPC.MLADSLeanEnableRangeTarget()',m)
 def test_ammo_refills_only_local_mosin_reserve_without_fsm_or_chamber_reset(self):
  a=self.world.split('class MLADSLeanRangeAmmo',1)[1]
  self.assertIn('GetGame().IsMultiplayer() || GetGame().GetPlayer() != player',a)
  self.assertIn('!weapon.IsKindOf("Mosin9130")',a)
  self.assertIn('player.GetWeaponManager().IsRunning()',a)
  self.assertIn('GetRandomChamberableAmmoTypeName(muzzle)',a)
  self.assertIn('for (int i = current; i < maximum; i++)',a)
  self.assertIn('if (!weapon.PushCartridgeToInternalMagazine(muzzle, 0, ammo))\n    break;',a)
  for forbidden in ['PushCartridgeToChamber','PopCartridgeFromChamber','SpawnAmmo','ResetFSM','SetWeaponFSM','OnFire(','EEFired(']:self.assertNotIn(forbidden,a)
  self.assertIn('CallLater(MLADSLeanRefreshAmmo, 100, true)',self.mission)
 def test_respawn_uses_death_event_exact_delay_and_rejects_duplicate_or_stale_death(self):
  w=self.world;m=self.mission
  self.assertIn('override void EEKilled(Object killer)',w)
  self.assertIn('MLADSLeanSettings.DemoKilled.Invoke(this)',w)
  self.assertIn('DemoKilled.Insert(MLADSLeanOnDemoKilled)',m)
  handler=m.split('void MLADSLeanOnDemoKilled',1)[1].split('void MLADSLeanDeleteCorpse',1)[0]
  self.assertIn('corpse != m_MLADSLeanNPC || m_MLADSLeanRespawnPending',handler)
  self.assertIn('m_MLADSLeanNPC = null;',handler)
  self.assertEqual(handler.count('CallLater(MLADSLeanSpawnTarget, 1000, false)'),1)
  self.assertIn('if (m_MLADSLeanClosing || GetGame().IsMultiplayer() || m_MLADSLeanNPC)',m)
  self.assertIn('m_MLADSLeanRespawnPending = false;',m)
 def test_human_ragdoll_fallback_and_single_horizontal_momentum_transfer(self):
  w=self.world
  self.assertIn('DisableSimulation(false);\n  PhysicsSetRagdoll(true);',w)
  self.assertIn('CallLater(MLADSLeanRangeRetryRagdoll, 50, false)',w)
  impulse=w.split('protected void MLADSLeanRangeTransferMomentum()',1)[1].split('override bool HandleDeath',1)[0]
  self.assertIn('m_MLADSLeanRangeImpulseApplied || !PhysicsIsRagdoll()',impulse)
  self.assertIn('m_MLADSLeanRangeImpulseApplied = true;',impulse)
  self.assertIn('delta[1] = 0;',impulse)
  self.assertEqual(impulse.count('dBodyApplyImpulse('),1)
  death=w.split('override bool HandleDeath',1)[1].split('void MLADSLeanRangeCleanup',1)[0]
  self.assertIn('m_MLADSLeanRangeRagdoll',death)
  self.assertIn('return super.HandleDeath(pCurrentCommandID)',death)
  self.assertNotIn('MovementLabHermitPhysicsCorpse',w)
 def test_cleanup_cancels_callbacks_and_bounds_corpses_and_ground_weapons(self):
  m=self.mission;w=self.world
  self.assertIn('m_MLADSLeanCorpses.Count() > 4',m)
  self.assertIn('CallLater(MLADSLeanDeleteCorpse, 10000, false, corpse)',m)
  finish=m.split('override void OnMissionFinish()',1)[1]
  self.assertIn('m_MLADSLeanClosing = true;',finish)
  self.assertIn('DemoKilled.Remove(MLADSLeanOnDemoKilled)',finish)
  for callback in ['MLADSLeanWelcome','MLADSLeanRefreshAmmo','MLADSLeanSpawnTarget','MLADSLeanDeleteCorpse']:self.assertIn('Remove('+callback+')',finish)
  self.assertIn('Remove(MLADSLeanRangeRetryRagdoll)',w)
  self.assertIn('!m_MLADSLeanRangeRifle.GetHierarchyParent()',w)
 def test_scope_of_player_controller_changes_and_script_structure(self):
  old=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  normalized=self.player.replace('MLADSLEAN17','MLADSLEAN16').replace('lean v17','lean v16')
  normalized=normalized.replace(' static ref ScriptInvoker DemoKilled = new ScriptInvoker();\n','').replace('  MLADSLeanRangeSampleMotion();\n','')
  self.assertEqual(normalized,old)
  for p in (KIT/'LogicSource/Scripts').rglob('*.c'):
   s=p.read_text()
   for match in re.finditer(r'(?:modded )?class \w+',s):self.assertGreater(end(s,match.start()),match.start())
 def test_packaged_hashes_and_launcher_preferences(self):
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v17-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(RangeTests));return suite
if __name__=='__main__':unittest.main()
