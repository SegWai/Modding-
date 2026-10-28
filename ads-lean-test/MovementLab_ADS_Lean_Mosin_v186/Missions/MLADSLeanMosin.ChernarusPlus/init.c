// Player-only test: all approved banks route from native stance/gait/hands.
class MLADSLeanMosinMission : MissionGameplay
{
 protected bool m_MLADSLeanSpawned;
 protected bool m_MLADSLeanClosing;
 protected Weapon_Base m_ML105StartingWeapon;
 protected int m_ML105EquipAttempts;
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
  m_ML105StartingWeapon = MLVanillaLoadout156.Equip(player);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(ML105EquipStartingWeapon, 500, false);
  player.SetAllowDamage(false);
  player.GetStatWater().Set(player.GetStatWater().GetMax());
  player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
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
 override void OnMissionFinish()
 {
  m_MLADSLeanClosing = true;
  ML144State.Open = false;
  ML149State.Open = false;
  ML149State.KeyDown = false;
  ML149State.Bound = false;
  ML144State.KeyDown = false;
  ML144State.Bound = false;
  ML144State.ArmsReady = false;
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(ML105EquipStartingWeapon);
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(MLADSLeanRefreshAmmo);
#ifdef DIAG_DEVELOPER
  MLFreeze135.Cancel();
#endif
  ML183WeaponState.Open = false;
  ML183BodyState.Open = false;
  ML183WeaponState.KeyDown = false;
  ML183BodyState.KeyDown = false;
  ML182WeaponState.Open = false;
  ML182BodyState.Open = false;
  ML182WeaponState.KeyDown = false;
  ML182BodyState.KeyDown = false;
  ML173WeaponState.Open = false;
  ML173BodyState.Open = false;
  ML173BodyState.KeyDown = false;
  ML173WeaponState.KeyDown = false;
  MLADSLeanSettings.WalkingActor = null;
  MLADSLeanSettings.DemoActor = null;
  super.OnMissionFinish();
 }
};
Mission CreateCustomMission(string path)
{
 return new MLADSLeanMosinMission();
}
