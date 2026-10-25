// Offline Mosin range. Shared custom lean, one live target and bounded corpses.
class MLADSLeanMosinMission : MissionGameplay
{
 protected bool m_MLADSLeanSpawned;
 protected bool m_MLADSLeanClosing;
 protected bool m_MLADSLeanRespawnPending;
 protected PlayerBase m_MLADSLeanNPC;
 protected vector m_MLADSLeanTargetPosition;
 protected vector m_MLADSLeanTargetOrientation;
 protected ref array<PlayerBase> m_MLADSLeanCorpses = new array<PlayerBase>();
 override void OnInit()
 {
  super.OnInit();
  if (GetGame().IsMultiplayer() || m_MLADSLeanSpawned)
   return;
  m_MLADSLeanSpawned = true;
  GetGame().GetWorld().SetDate(2026, 6, 15, 12, 0);
  vector spawn = "4440 0 10240";
  spawn[1] = GetGame().SurfaceY(spawn[0], spawn[2]) + 0.2;
  PlayerBase player = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Mirek", spawn, 0, "NONE"));
  if (!player)
   return;
  GetGame().SelectPlayer(null, player);
  player.SetOrientation("145 0 0");
  player.GetInventory().CreateInInventory("TShirt_Grey");
  player.GetInventory().CreateInInventory("Jeans_Blue");
  player.GetInventory().CreateInInventory("Sneakers_Black");
  player.GetInventory().CreateInInventory("HuntingBag");
  Weapon_Base mosin = Weapon_Base.Cast(player.GetHumanInventory().CreateInHands("Mosin9130"));
  if (mosin)
  {
   mosin.SpawnAmmo("Ammo_762x54");
   EntityAI scope = mosin.GetInventory().CreateAttachment("PUScopeOptic");
   EntityAI silencer = mosin.GetInventory().CreateAttachment("ImprovisedSuppressor");
   Print("[MLADSLEAN21] player_scope_attached=" + (scope != null));
   Print("[MLADSLEAN21] player_suppressor_attached=" + (silencer != null));
  }
  player.SetAllowDamage(false);
  player.GetStatWater().Set(player.GetStatWater().GetMax());
  player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
  vector facing = player.GetDirection();
  facing[1] = 0;
  facing.Normalize();
  m_MLADSLeanTargetPosition = spawn + facing * 8;
  m_MLADSLeanTargetPosition[1] = GetGame().SurfaceY(m_MLADSLeanTargetPosition[0], m_MLADSLeanTargetPosition[2]) + 0.2;
  m_MLADSLeanTargetOrientation = player.GetOrientation();
  m_MLADSLeanTargetOrientation[0] = m_MLADSLeanTargetOrientation[0] + 180;
  MLADSLeanSettings.DemoKilled.Insert(MLADSLeanOnDemoKilled);
  MLADSLeanSpawnTarget();
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(MLADSLeanRefreshAmmo, 100, true);
  GetGame().GetCallQueue(CALL_CATEGORY_GUI).CallLater(MLADSLeanWelcome, 2500, false);
 }
 void MLADSLeanRefreshAmmo()
 {
  if (!m_MLADSLeanClosing)
   MLADSLeanRangeAmmo.Refresh(PlayerBase.Cast(GetGame().GetPlayer()));
 }
 void MLADSLeanSpawnTarget()
 {
  if (m_MLADSLeanClosing || GetGame().IsMultiplayer() || m_MLADSLeanNPC)
   return;
  m_MLADSLeanRespawnPending = false;
  m_MLADSLeanNPC = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Denis", m_MLADSLeanTargetPosition, 0, "NONE"));
  if (!m_MLADSLeanNPC)
  {
   Print("[MLADSLEAN21] ERROR target creation failed");
   return;
  }
  m_MLADSLeanNPC.SetOrientation(m_MLADSLeanTargetOrientation);
  m_MLADSLeanNPC.GetInventory().CreateInInventory("Hoodie_Red");
  m_MLADSLeanNPC.GetInventory().CreateInInventory("Jeans_Blue");
  m_MLADSLeanNPC.GetInventory().CreateInInventory("Sneakers_Black");
  Weapon_Base npcMosin = Weapon_Base.Cast(m_MLADSLeanNPC.GetHumanInventory().CreateInHands("Mosin9130"));
  if (npcMosin)
   npcMosin.SpawnAmmo("Ammo_762x54");
  m_MLADSLeanNPC.SetAllowDamage(true);
  m_MLADSLeanNPC.GetStatWater().Set(m_MLADSLeanNPC.GetStatWater().GetMax());
  m_MLADSLeanNPC.GetStatEnergy().Set(m_MLADSLeanNPC.GetStatEnergy().GetMax());
  m_MLADSLeanNPC.MLADSLeanEnableRangeTarget();
  MLADSLeanSettings.DemoActor = m_MLADSLeanNPC;
  if (npcMosin)
   m_MLADSLeanNPC.MLADSLeanStartDemo();
  Print("[MLADSLEAN21] target_spawned at_ms=" + GetGame().GetTime());
 }
 void MLADSLeanOnDemoKilled(PlayerBase corpse)
 {
  if (m_MLADSLeanClosing || !corpse || corpse != m_MLADSLeanNPC || m_MLADSLeanRespawnPending)
   return;
  m_MLADSLeanRespawnPending = true;
  m_MLADSLeanNPC = null;
  MLADSLeanSettings.DemoActor = null;
  m_MLADSLeanCorpses.Insert(corpse);
  // Keep a few bodies briefly for ragdoll inspection without accumulating them.
  while (m_MLADSLeanCorpses.Count() > 4)
   MLADSLeanDeleteCorpse(m_MLADSLeanCorpses[0]);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(MLADSLeanDeleteCorpse, 10000, false, corpse);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(MLADSLeanSpawnTarget, 1000, false);
  Print("[MLADSLEAN21] target_respawn_queued delay_ms=1000 death_at_ms=" + GetGame().GetTime());
 }
 void MLADSLeanDeleteCorpse(PlayerBase corpse)
 {
  int index = m_MLADSLeanCorpses.Find(corpse);
  if (index >= 0)
   m_MLADSLeanCorpses.Remove(index);
  if (corpse)
  {
   corpse.MLADSLeanRangeCleanup();
   GetGame().ObjectDelete(corpse);
  }
 }
 void MLADSLeanWelcome()
 {
  NotificationSystem.AddNotificationExtended(10, "Mosin lean v21", "Scoped/suppressed Mosin: unlimited reserve. Kill target: ragdoll + 1s respawn. F10 pause. F6 head; F7 lean; F8 inspect; F9 measure.");
 }
 override void OnMissionFinish()
 {
  m_MLADSLeanClosing = true;
  MLADSLeanSettings.DemoKilled.Remove(MLADSLeanOnDemoKilled);
  GetGame().GetCallQueue(CALL_CATEGORY_GUI).Remove(MLADSLeanWelcome);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(MLADSLeanRefreshAmmo);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(MLADSLeanSpawnTarget);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(MLADSLeanDeleteCorpse);
  if (m_MLADSLeanNPC)
  {
   m_MLADSLeanNPC.MLADSLeanStopDemo();
   m_MLADSLeanNPC.MLADSLeanRangeCleanup();
   GetGame().ObjectDelete(m_MLADSLeanNPC);
   m_MLADSLeanNPC = null;
  }
  while (m_MLADSLeanCorpses.Count() > 0)
   MLADSLeanDeleteCorpse(m_MLADSLeanCorpses[0]);
  MLADSLeanSettings.DemoActor = null;
  super.OnMissionFinish();
 }
};
Mission CreateCustomMission(string path)
{
 return new MLADSLeanMosinMission();
}
