// Offline Mosin lean test with one native-walking comparison actor.
class MLADSLeanMosinMission : MissionGameplay
{
 protected bool m_MLADSLeanSpawned;
 protected PlayerBase m_MLADSLeanNPC;
 override void OnInit()
 {
  super.OnInit();
  if (GetGame().IsMultiplayer() || m_MLADSLeanSpawned)
   return;
  m_MLADSLeanSpawned = true;
  GetGame().GetWorld().SetDate(2026, 6, 15, 12, 0);
  vector spawn = "4440 0 10240";
  spawn[1] = GetGame().SurfaceY(spawn[0], spawn[2]) + 0.2;
  Print("[MLADSLEAN5] stage=create_player");
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
   mosin.SpawnAmmo("Ammo_762x54");
  player.GetInventory().CreateInInventory("PUScopeOptic");
  player.GetInventory().CreateInInventory("AmmoBox_762x54_20Rnd");
  player.SetAllowDamage(false);
  player.GetStatWater().Set(player.GetStatWater().GetMax());
  player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
  vector facing = player.GetDirection();
  facing[1] = 0;
  facing.Normalize();
  vector npcPosition = spawn + facing * 8;
  npcPosition[1] = GetGame().SurfaceY(npcPosition[0], npcPosition[2]) + 0.2;
  m_MLADSLeanNPC = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Denis", npcPosition, 0, "NONE"));
  if (m_MLADSLeanNPC)
  {
   vector npcOrientation = player.GetOrientation();
   npcOrientation[0] = npcOrientation[0] + 180;
   m_MLADSLeanNPC.SetOrientation(npcOrientation);
   m_MLADSLeanNPC.GetInventory().CreateInInventory("Hoodie_Red");
   m_MLADSLeanNPC.GetInventory().CreateInInventory("Jeans_Blue");
   m_MLADSLeanNPC.GetInventory().CreateInInventory("Sneakers_Black");
   Weapon_Base npcMosin = Weapon_Base.Cast(m_MLADSLeanNPC.GetHumanInventory().CreateInHands("Mosin9130"));
   if (npcMosin)
    npcMosin.SpawnAmmo("Ammo_762x54");
   else
    Print("[MLADSLEAN5] ERROR demo Mosin creation failed");
   m_MLADSLeanNPC.SetAllowDamage(false);
   m_MLADSLeanNPC.GetStatWater().Set(m_MLADSLeanNPC.GetStatWater().GetMax());
   m_MLADSLeanNPC.GetStatEnergy().Set(m_MLADSLeanNPC.GetStatEnergy().GetMax());
   if (npcMosin)
   {
    MLADSLeanSettings.DemoActor = m_MLADSLeanNPC;
    m_MLADSLeanNPC.MLADSLeanStartDemo();
   }
  }
  else
   Print("[MLADSLEAN5] ERROR demo spawn failed");
  Print("[MLADSLEAN5] ready. ADS lean stand/walk/crouch. F7 compare, F8 inspect, F9 measurements, F10 pause NPC.");
  GetGame().GetCallQueue(CALL_CATEGORY_GUI).CallLater(MLADSLeanWelcome, 2500, false);
 }
 void MLADSLeanWelcome()
 {
  NotificationSystem.AddNotificationExtended(10, "Mosin lean v5", "ADS + Q/E: stand, walk or crouch. Red NPC patrols +/-2m. F7 compare; F8 inspect; F9 measure; F10 pause NPC.");
 }
 override void OnMissionFinish()
 {
  GetGame().GetCallQueue(CALL_CATEGORY_GUI).Remove(MLADSLeanWelcome);
  if (m_MLADSLeanNPC)
  {
   m_MLADSLeanNPC.MLADSLeanStopDemo();
   GetGame().ObjectDelete(m_MLADSLeanNPC);
   m_MLADSLeanNPC = null;
  }
  MLADSLeanSettings.DemoActor = null;
  super.OnMissionFinish();
 }
};
Mission CreateCustomMission(string path)
{
 return new MLADSLeanMosinMission();
}
