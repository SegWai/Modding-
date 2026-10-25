// Standalone native-Mosin pose test. No SNAFU or other workshop mods required.
class MLADSLeanMosinMission : MissionGameplay
{
 protected bool m_MLADSLeanSpawned;
 override void OnInit()
 {
  super.OnInit();
  if (GetGame().IsMultiplayer() || m_MLADSLeanSpawned)
   return;
  m_MLADSLeanSpawned = true;
  GetGame().GetWorld().SetDate(2026, 6, 15, 12, 0);
  vector spawn = "4440 0 10240";
  spawn[1] = GetGame().SurfaceY(spawn[0], spawn[2]) + 0.2;
  Print("[MLADSLEAN1] stage=create_player");
  PlayerBase player = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Mirek", spawn, 0, "NONE"));
  if (!player)
  {
   Print("[MLADSLEAN1] ERROR player creation failed");
   return;
  }
  GetGame().SelectPlayer(null, player);
  player.SetOrientation("145 0 0");
  player.GetInventory().CreateInInventory("TShirt_Grey");
  player.GetInventory().CreateInInventory("Jeans_Blue");
  player.GetInventory().CreateInInventory("Sneakers_Black");
  player.GetInventory().CreateInInventory("HuntingBag");
  Weapon_Base mosin = Weapon_Base.Cast(player.GetHumanInventory().CreateInHands("Mosin9130"));
  if (mosin)
   mosin.SpawnAmmo("Ammo_762x54");
  player.GetInventory().CreateInInventory("PUScopeOptic");
  player.GetInventory().CreateInInventory("AmmoBox_762x54_20Rnd");
  player.GetInventory().CreateInInventory("AmmoBox_762x54_20Rnd");
  player.SetAllowDamage(false);
  player.GetStatWater().Set(player.GetStatWater().GetMax());
  player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
  Print("[MLADSLEAN1] stage=ready weapon=Mosin9130. F7=native/custom; F8=third-person inspection.");
  GetGame().GetCallQueue(CALL_CATEGORY_GUI).CallLater(MLADSLeanWelcome, 2500, false);
 }
 void MLADSLeanWelcome()
 {
  NotificationSystem.AddNotificationExtended(10, "Mosin ADS lean test v1", "Stand still; ADS + Q/E. F7: native/custom. F8: third-person inspection. PU scope is in the bag.");
 }
};
Mission CreateCustomMission(string path)
{
 return new MLADSLeanMosinMission();
}
