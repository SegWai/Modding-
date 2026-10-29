// Shared-clock standing unarmed raised-only previews: native red and editable custom blue.
class MLADSLeanMosinMission : MissionGameplay
{
 protected bool m_MLADSLeanSpawned;
 protected bool m_MLADSLeanClosing;
 protected Weapon_Base m_ML105StartingWeapon;
 protected int m_ML105EquipAttempts;
 protected ref array<PlayerBase> m_ML206Actors = new array<PlayerBase>;
 protected vector m_MLADSLeanTargetPosition;
 protected vector m_MLADSLeanTargetOrientation;
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
  vector facing = player.GetDirection();
  facing[1] = 0;
  facing.Normalize();
  m_MLADSLeanTargetPosition = spawn + facing * 8;
  m_MLADSLeanTargetPosition[1] = GetGame().SurfaceY(m_MLADSLeanTargetPosition[0], m_MLADSLeanTargetPosition[2]) + 0.2;
  m_MLADSLeanTargetOrientation = player.GetOrientation();
  m_MLADSLeanTargetOrientation[0] = m_MLADSLeanTargetOrientation[0] + 180;
  ML181SpawnCrouchPair();
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
 PlayerBase ML206CreatePreview(vector position, string itemType, string clothing, bool walking = true, bool raised = false, bool crouch = false)
 {
  PlayerBase actor = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Denis", position, 0, "NONE"));
  if (!actor)
   return null;
  actor.SetOrientation(m_MLADSLeanTargetOrientation);
  actor.GetInventory().CreateInInventory(clothing);
  actor.GetInventory().CreateInInventory("Jeans_Blue");
  actor.GetInventory().CreateInInventory("Sneakers_Black");
  actor.SetAllowDamage(false);
  actor.GetStatWater().Set(actor.GetStatWater().GetMax());
  actor.GetStatEnergy().Set(actor.GetStatEnergy().GetMax());
  if (itemType != "")
  {
   EntityAI item = actor.GetHumanInventory().CreateInHands(itemType);
   Weapon_Base gun = Weapon_Base.Cast(item);
   if (gun)
   {
    if (itemType == "AK74")
    {
     MLADSLeanRangeAmmo.AttachPart(gun, "AK_PlasticBttstck");
     MLADSLeanRangeAmmo.AttachPart(gun, "AK_RailHndgrd");
     MLVanillaLoadout156.Load(gun, "Mag_AK74_30Rnd");
    }
    else if (itemType == "MP5K")
    {
     MLADSLeanRangeAmmo.AttachPart(gun, "MP5_PlasticHndgrd");
     MLADSLeanRangeAmmo.AttachPart(gun, "MP5k_Stock");
     MLVanillaLoadout156.Load(gun, "Mag_MP5_30Rnd");
    }
    else if (itemType == "SVD")
     MLVanillaLoadout156.Load(gun, "Mag_SVD_10Rnd");
    else if (itemType == "Glock19")
     MLVanillaLoadout156.Load(gun, "Mag_Glock_15Rnd");
    else if (itemType == "UMP45")
     MLVanillaLoadout156.Load(gun, "Mag_UMP_25Rnd");
    else
     MLVanillaLoadout156.Load(gun, "");
   }
   if (item && itemType == "Flashlight")
    item.GetInventory().CreateAttachment("Battery9V");
   if (!item)
    Print("[MLLINEUP206] failed item=" + itemType);
  }
  if (itemType == "SodaCan_Cola")
   actor.ML214EnableCanEditor();
  if (raised)
   actor.ML213StartRaisedLineup(crouch, walking);
  else
   actor.ML213StartLoweredLineup(walking);
  m_ML206Actors.Insert(actor);
  return actor;
 }
 void ML213SpawnRow(TStringArray items, vector origin, vector right, bool walking, string clothing)
 {
  float centre = (items.Count() - 1) * 0.5;
  for (int index = 0; index < items.Count(); index++)
  {
   float slot = index - centre;
   vector position = origin + right * (slot * 0.95);
   position[1] = GetGame().SurfaceY(position[0], position[2]) + 0.2;
   string actorClothing = clothing;
   if (items[index] == "BandageDressing")
    actorClothing = "Hoodie_Blue";
   PlayerBase preview = ML206CreatePreview(position, items[index], actorClothing, walking);
   if (walking && items[index] == "SodaCan_Cola")
    MLADSLeanSettings.DemoActor = preview;
   Print("[MLLINEUP213] walking=" + walking + " item=" + items[index]);
  }
 }
 void ML181SpawnCrouchPair()
 {
  ML181CrouchCycle.Begin();
  ML206LineupClock.Begin();
  float yaw = m_MLADSLeanTargetOrientation[0] * Math.DEG2RAD;
  vector forward = Vector(Math.Sin(yaw), 0, Math.Cos(yaw));
  vector right = Vector(forward[2], 0, -forward[0]);
  TStringArray items = new TStringArray;
  items.Insert("SodaCan_Cola");
  items.Insert("BandageDressing");
  ML213SpawnRow(items, m_MLADSLeanTargetPosition, right, true, "Hoodie_Grey");
  MLADSLeanSettings.WalkingActor = null;
 }
 override void OnMissionFinish()
 {
  m_MLADSLeanClosing = true;
  foreach (PlayerBase preview : m_ML206Actors)
  {
   if (!preview)
    continue;
   preview.MLADSLeanStopDemo();
   GetGame().ObjectDelete(preview);
  }
  m_ML206Actors.Clear();
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
  ML190WeaponState.Open = false;
  ML190BodyState.Open = false;
  ML190WeaponState.KeyDown = false;
  ML190BodyState.KeyDown = false;
  ML214WeaponState.Open = false;
  ML214BodyState.Open = false;
  ML214WeaponState.KeyDown = false;
  ML214BodyState.KeyDown = false;
  ML211WeaponState.Open = false;
  ML211BodyState.Open = false;
  ML211WeaponState.KeyDown = false;
  ML211BodyState.KeyDown = false;
  ML209WeaponState.Open = false;
  ML209BodyState.Open = false;
  ML209WeaponState.KeyDown = false;
  ML209BodyState.KeyDown = false;
  ML207WeaponState.Open = false;
  ML207BodyState.Open = false;
  ML207WeaponState.KeyDown = false;
  ML207BodyState.KeyDown = false;
  ML204WeaponState.Open = false;
  ML204BodyState.Open = false;
  ML204WeaponState.KeyDown = false;
  ML204BodyState.KeyDown = false;
  ML202WeaponState.Open = false;
  ML202BodyState.Open = false;
  ML202WeaponState.KeyDown = false;
  ML202BodyState.KeyDown = false;
  ML200WeaponState.Open = false;
  ML200BodyState.Open = false;
  ML200WeaponState.KeyDown = false;
  ML200BodyState.KeyDown = false;
  ML193WeaponState.Open = false;
  ML193BodyState.Open = false;
  ML193WeaponState.KeyDown = false;
  ML193BodyState.KeyDown = false;
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
