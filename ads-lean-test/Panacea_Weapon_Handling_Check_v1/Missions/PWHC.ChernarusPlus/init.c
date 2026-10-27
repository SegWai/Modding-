// A separate native handling check. No custom workspace, PlayerBase, camera,
// weapon-profile registration, input overrides, or repeating ammo refill.
class PWHCMission : MissionGameplay
{
 protected bool m_Started;
 protected bool m_Closing;
 protected int m_Samples;
 override void OnInit()
 {
  super.OnInit();
  if (GetGame().IsMultiplayer() || m_Started)
   return;
  m_Started = true;
  GetGame().GetWorld().SetDate(2026, 6, 15, 12, 0);
  vector spawn = "4440 0 10240";
  spawn[1] = GetGame().SurfaceY(spawn[0], spawn[2]) + 0.2;
  PlayerBase player = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Mirek", spawn, 0, "NONE"));
  if (!player)
   return;
  GetGame().SelectPlayer(null, player);
  player.GetInventory().CreateInInventory("TShirt_Grey");
  player.GetInventory().CreateInInventory("Jeans_Blue");
  player.GetInventory().CreateInInventory("Sneakers_Black");
  player.GetInventory().CreateAttachment("AliceBag_Green");
  player.SetAllowDamage(false);
  player.GetStatWater().Set(player.GetStatWater().GetMax());
  player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
  SpawnWeapon(player, "AK74", "Mag_AK74_30Rnd", 0);
  SpawnWeapon(player, "PNC_W_SCARH", "PNC_SCARH_20Rnd", 1);
  SpawnWeapon(player, "PNC_W_AWM", "PNC_Mag_AWM_5Rnd", 2);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(SampleHands, 1000, true);
  GetGame().GetCallQueue(CALL_CATEGORY_GUI).CallLater(Welcome, 2500, false);
 }
 void SpawnWeapon(PlayerBase player, string weaponType, string magazineType, int slot)
 {
  if (!GetGame().ConfigIsExisting("CfgWeapons " + weaponType))
  {
   Print("[PWHC] MISSING class=" + weaponType);
   return;
  }
  EntityAI entity;
  if (slot == 0)
   entity = player.GetHumanInventory().CreateInHands(weaponType);
  else if (slot == 1)
   entity = player.GetInventory().CreateAttachment(weaponType);
  else
   entity = player.GetInventory().CreateInInventory(weaponType);
  if (!entity)
  {
   vector position = player.GetPosition() + Vector(slot, 0, 0);
   entity = EntityAI.Cast(GetGame().CreateObjectEx(weaponType, position, ECE_PLACE_ON_SURFACE));
   Print("[PWHC] storage failed, placed on ground=" + weaponType);
  }
  Weapon_Base weapon = Weapon_Base.Cast(entity);
  Print("[PWHC] spawn=" + weaponType + " entity=" + (entity != null) + " firearm=" + (weapon != null));
  if (!weapon)
   return;
  bool ammo = weapon.SpawnAmmo(magazineType);
  player.SetQuickBarEntityShortcut(weapon, slot, true);
  Print("[PWHC] quickbar=" + (slot + 1) + " weapon=" + weaponType + " loaded=" + ammo);
  TStringArray lineage = new TStringArray;
  GetGame().ConfigGetFullPath("CfgWeapons " + weaponType, lineage);
  foreach (string ancestor : lineage)
   Print("[PWHC] ancestry " + weaponType + " -> " + ancestor);
 }
 void Welcome()
 {
  NotificationSystem.AddNotificationExtended(15, "Native weapon handling check", "1 AK74 control, 2 SCAR-H, 3 AWM. Try raise, ADS, fire, and switching. No custom lean or camera scripts loaded.");
 }
 void SampleHands()
 {
  if (m_Closing)
   return;
  m_Samples++;
  if (m_Samples >= 120)
   GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(SampleHands);
  PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
  if (!player)
   return;
  EntityAI held = player.GetHumanInventory().GetEntityInHands();
  string heldType = "empty";
  if (held)
   heldType = held.GetType();
  bool command = player.GetCommandModifier_Weapons() != null;
  bool firearm = Weapon_Base.Cast(held) != null;
  bool busy = false;
  if (player.GetWeaponManager())
   busy = player.GetWeaponManager().IsRunning();
  string report = "[PWHC] t=" + GetGame().GetTime();
  report += " hands=" + heldType;
  report += " firearm=" + firearm;
  report += " native_weapon_command=" + command;
  report += " raised=" + player.IsRaised();
  report += " raise_complete=" + player.IsWeaponRaiseCompleted();
  report += " ads=" + player.IsInIronsights();
  report += " weapon_manager_busy=" + busy;
  Print(report);
 }
 override void OnMissionFinish()
 {
  m_Closing = true;
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(SampleHands);
  GetGame().GetCallQueue(CALL_CATEGORY_GUI).Remove(Welcome);
  super.OnMissionFinish();
 }
};
Mission CreateCustomMission(string path)
{
 return new PWHCMission();
}
