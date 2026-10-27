// Offline Mosin range. Shared custom lean, one live target and bounded corpses.
class MLADSLeanMosinMission : MissionGameplay
{
 protected bool m_MLADSLeanSpawned;
 protected Weapon_Base m_ML105StartingWeapon;
 protected int m_ML105EquipAttempts;
 protected bool m_MLADSLeanClosing;
 protected bool m_MLADSLeanRespawnPending;
 protected PlayerBase m_MLADSLeanNPC;
 protected PlayerBase m_ML114Woman;
 protected vector m_ML114WomanHome;
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
  EntityAI wornBackpack = player.FindAttachmentBySlotName("Back");
  if (!wornBackpack)
   wornBackpack = player.GetInventory().CreateAttachment("AliceBag_Green");
  if (!wornBackpack)
   wornBackpack = player.GetInventory().CreateAttachment("MountainBag_Green");
  string backpackType = "none";
  if (wornBackpack)
   backpackType = wornBackpack.GetType();
  Print("[MLLOADOUT104] worn_backpack=" + backpackType);
  m_ML105StartingWeapon = MLADSLeanAJ107.Equip(player);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(ML105EquipStartingWeapon, 500, false);
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
  // Ten metres to the male NPC's own right, anchored at his patrol centre.
  vector npcForward = facing * -1;
  if (m_MLADSLeanNPC)
   npcForward = m_MLADSLeanNPC.GetDirection();
  vector npcRight = Vector(npcForward[2], 0, -npcForward[0]);
  npcRight.Normalize();
  m_ML114WomanHome = m_MLADSLeanTargetPosition + npcRight * 10;
  m_ML114WomanHome[1] = GetGame().SurfaceY(m_ML114WomanHome[0], m_ML114WomanHome[2]) + 0.2;
  MLADSLeanSettings.Mimic = new MLMimic114Controller;
  ML114SpawnWoman();
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(MLADSLeanRefreshAmmo, 100, true);

 }
 void ML105EquipStartingWeapon()
 {
  if (m_MLADSLeanClosing || GetGame().IsMultiplayer() || !m_ML105StartingWeapon)
   return;
  PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
  if (!player || !player.IsAlive())
   return;
  EntityAI held = player.GetHumanInventory().GetEntityInHands();
  if (held && held != m_ML105StartingWeapon)
  {
   Print("[MLHANDS105] startup equip skipped: player already holds " + held.GetType());
   return;
  }
  if (!held && m_ML105EquipAttempts < 3)
  {
   m_ML105EquipAttempts++;
   bool canTake = player.GetHumanInventory().CanAddEntityInHands(m_ML105StartingWeapon);
   Print("[MLHANDS105] attempt=" + m_ML105EquipAttempts + " can_take=" + canTake);
   if (canTake)
    player.LocalTakeEntityToHands(m_ML105StartingWeapon);
   GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(ML105EquipStartingWeapon, 500, false);
   return;
  }
  string heldType = "empty";
  if (held)
   heldType = held.GetType();
  bool firearm = Weapon_Base.Cast(held) != null;
  bool weaponCommand = player.GetCommandModifier_Weapons() != null;
  string report = "[MLHANDS105] actual_hands=" + heldType;
  report += " firearm=" + firearm;
  report += " weapon_command=" + weaponCommand;
  Print(report);

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
   Print("[MLADSLEAN104] ERROR target creation failed");
   return;
  }
  m_MLADSLeanNPC.SetOrientation(m_MLADSLeanTargetOrientation);
  m_MLADSLeanNPC.GetInventory().CreateInInventory("Hoodie_Red");
  m_MLADSLeanNPC.GetInventory().CreateInInventory("Jeans_Blue");
  m_MLADSLeanNPC.GetInventory().CreateInInventory("Sneakers_Black");
  Weapon_Base npcMosin = Weapon_Base.Cast(m_MLADSLeanNPC.GetHumanInventory().CreateInHands("AK74"));
  if (npcMosin)
   MLADSLeanRangeAmmo.EquipAK74(npcMosin);
  m_MLADSLeanNPC.SetAllowDamage(true);
  m_MLADSLeanNPC.GetStatWater().Set(m_MLADSLeanNPC.GetStatWater().GetMax());
  m_MLADSLeanNPC.GetStatEnergy().Set(m_MLADSLeanNPC.GetStatEnergy().GetMax());
  m_MLADSLeanNPC.MLADSLeanEnableRangeTarget();
  MLADSLeanSettings.DemoActor = m_MLADSLeanNPC;
  if (npcMosin)
   m_MLADSLeanNPC.MLADSLeanStartDemo();
  Print("[MLADSLEAN104] target_spawned at_ms=" + GetGame().GetTime());
 }
 void ML114SpawnWoman()
 {
  if (m_MLADSLeanClosing || m_ML114Woman || GetGame().IsMultiplayer())
   return;
  m_ML114Woman = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorF_Eva", m_ML114WomanHome, 0, "NONE"));
  if (!m_ML114Woman)
  {
   Print("[MLMIMIC114] female_spawn_failed");
   return;
  }
  m_ML114Woman.SetOrientation(m_MLADSLeanTargetOrientation);
  m_ML114Woman.GetInventory().CreateInInventory("Hoodie_Blue");
  m_ML114Woman.GetInventory().CreateInInventory("Jeans_Blue");
  m_ML114Woman.GetInventory().CreateInInventory("Sneakers_Black");
  Weapon_Base weapon = Weapon_Base.Cast(m_ML114Woman.GetHumanInventory().CreateInHands("AK74"));
  if (weapon)
   MLADSLeanRangeAmmo.EquipAK74(weapon);
  m_ML114Woman.SetAllowDamage(true);
  m_ML114Woman.GetStatWater().Set(m_ML114Woman.GetStatWater().GetMax());
  m_ML114Woman.GetStatEnergy().Set(m_ML114Woman.GetStatEnergy().GetMax());
  m_ML114Woman.MLADSLeanEnableRangeTarget();
  if (MLADSLeanSettings.Mimic)
   MLADSLeanSettings.Mimic.AttachActor(m_ML114Woman, m_ML114WomanHome, m_MLADSLeanTargetOrientation);
  Print("[MLMIMIC114] female_spawned home=" + m_ML114WomanHome);
 }
 void MLADSLeanOnDemoKilled(PlayerBase corpse)
 {
  if (!m_MLADSLeanClosing && corpse && corpse == m_ML114Woman)
  {
   if (MLADSLeanSettings.Mimic)
    MLADSLeanSettings.Mimic.AttachActor(null, m_ML114WomanHome, m_MLADSLeanTargetOrientation);
   m_ML114Woman = null;
   m_MLADSLeanCorpses.Insert(corpse);
   while (m_MLADSLeanCorpses.Count() > 4)
    MLADSLeanDeleteCorpse(m_MLADSLeanCorpses[0]);
   GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(MLADSLeanDeleteCorpse, 10000, false, corpse);
   GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(ML114SpawnWoman, 1000, false);
   return;
  }
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
  Print("[MLADSLEAN104] target_respawn_queued delay_ms=1000 death_at_ms=" + GetGame().GetTime());
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
 override void OnMissionFinish()
 {
  m_MLADSLeanClosing = true;
  MLADSLeanSettings.DemoKilled.Remove(MLADSLeanOnDemoKilled);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(ML114SpawnWoman);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(ML105EquipStartingWeapon);
  if (MLADSLeanSettings.Mimic)
  {
   MLADSLeanSettings.Mimic.Reset();
   MLADSLeanSettings.Mimic.AttachActor(null, m_ML114WomanHome, m_MLADSLeanTargetOrientation);
   MLADSLeanSettings.Mimic = null;
  }
  if (m_ML114Woman)
  {
   m_ML114Woman.ML114DisableMimic();
   m_ML114Woman.MLADSLeanRangeCleanup();
   GetGame().ObjectDelete(m_ML114Woman);
   m_ML114Woman = null;
  }
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
