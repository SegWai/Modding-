// Offline Mosin reserve refill helper.
class MLADSLeanRangeAmmo
{
 static void Refresh(PlayerBase player)
 {
  if (!player || GetGame().IsMultiplayer() || GetGame().GetPlayer() != player || !player.IsAlive())
   return;
  Weapon_Base weapon = Weapon_Base.Cast(player.GetHumanInventory().GetEntityInHands());
  if (!weapon)
   return;
  bool supportedAmmo = weapon.IsKindOf("Mosin9130") || weapon.IsKindOf("AK74");
  supportedAmmo = supportedAmmo || weapon.IsKindOf("MP5K") || weapon.IsKindOf("FNX45") || weapon.IsKindOf("SVD");
  if (!supportedAmmo)
   return;
  weapon.SetHealthMax("", "Health");
  ItemBase suppressor = weapon.GetAttachedSuppressor();
  if (suppressor)
   suppressor.SetHealthMax("", "Health");
  int muzzle = weapon.GetCurrentMuzzle();
  Magazine magazine = weapon.GetMagazine(muzzle);
  // Refill the AK's attached magazine during sustained automatic fire too.
  if (magazine)
  {
   if (GetGame().IsServer())
    magazine.ServerSetAmmoMax();
   else
    magazine.LocalSetAmmoMax();
   return;
  }
  // Preserve the Mosin's native bolt/FSM and chamber; refill internal reserve.
  if (player.GetWeaponManager() && player.GetWeaponManager().IsRunning())
   return;
  int maximum = weapon.GetInternalMagazineMaxCartridgeCount(muzzle);
  int current = weapon.GetInternalMagazineCartridgeCount(muzzle);
  string ammo = weapon.GetRandomChamberableAmmoTypeName(muzzle);
  if (ammo == "")
   return;
  for (int i = current; i < maximum; i++)
  {
   if (!weapon.PushCartridgeToInternalMagazine(muzzle, 0, ammo))
    break;
  }
 }
 static EntityAI AttachPart(EntityAI host, string partType)
 {
  if (!host)
   return null;
  EntityAI part = host.GetInventory().CreateAttachment(partType);
  string result = "[MLLOADOUT102] host=" + host.GetType();
  result += " part=" + partType;
  result += " attached=" + (part != null);
  Print(result);
  return part;
 }
 static void AttachPoweredPart(EntityAI host, string partType)
 {
  EntityAI part = AttachPart(host, partType);
  if (part)
   AttachPart(part, "Battery9V");
 }
 static Weapon_Base CreateStoredWeapon(PlayerBase player, string weaponType, bool shoulder)
 {
  if (!player)
   return null;
  Weapon_Base weapon;
  if (shoulder)
   weapon = Weapon_Base.Cast(player.GetInventory().CreateAttachment(weaponType));
  if (!weapon)
   weapon = Weapon_Base.Cast(player.GetInventory().CreateInInventory(weaponType));
  bool onGround = false;
  if (!weapon)
  {
   vector groundPosition = player.GetPosition() + Vector(1, 0, 0);
   weapon = Weapon_Base.Cast(GetGame().CreateObjectEx(weaponType, groundPosition, ECE_PLACE_ON_SURFACE));
   onGround = weapon != null;
  }
  string result = "[MLLOADOUT102] weapon=" + weaponType;
  result += " created=" + (weapon != null);
  result += " on_ground=" + onGround;
  Print(result);
  return weapon;
 }
 static void SetAutomatic(Weapon_Base weapon)
 {
  if (!weapon)
   return;
  int muzzle = weapon.GetCurrentMuzzle();
  int originalMode = weapon.GetCurrentMode(muzzle);
  for (int mode = 0; mode < weapon.GetMuzzleModeCount(muzzle); mode++)
  {
   weapon.SetCurrentMode(muzzle, mode);
   if (weapon.GetCurrentModeAutoFire(muzzle))
    return;
  }
  weapon.SetCurrentMode(muzzle, originalMode);
 }
 static void EquipMP5(Weapon_Base weapon)
 {
  if (!weapon)
   return;
  AttachPart(weapon, "MP5k_StockBttstck");
  AttachPart(weapon, "MP5_RailHndgrd");
  AttachPart(weapon, "PistolSuppressor");
  AttachPoweredPart(weapon, "ReflexOptic");
  AttachPoweredPart(weapon, "UniversalLight");
  weapon.SpawnAmmo("Mag_MP5_30Rnd");
  SetAutomatic(weapon);
 }
 static void EquipFNX(Weapon_Base weapon)
 {
  if (!weapon)
   return;
  AttachPart(weapon, "PistolSuppressor");
  AttachPoweredPart(weapon, "FNP45_MRDSOptic");
  AttachPoweredPart(weapon, "TLRLight");
  weapon.SpawnAmmo("Mag_FNX45_15Rnd");
 }
 static void EquipSVD(Weapon_Base weapon)
 {
  if (!weapon)
   return;
  AttachPart(weapon, "AK_Suppressor");
  AttachPoweredPart(weapon, "PSO1Optic");
  weapon.SpawnAmmo("Mag_SVD_10Rnd");
 }
 static void SpareMagazine(PlayerBase player, string magazineType)
 {
  Magazine magazine = Magazine.Cast(player.GetInventory().CreateInInventory(magazineType));
  if (!magazine)
   return;
  if (GetGame().IsServer())
   magazine.ServerSetAmmoMax();
  else
   magazine.LocalSetAmmoMax();
 }
 static void EquipAK74(Weapon_Base weapon)
 {
  if (!weapon || !weapon.IsKindOf("AK74") || GetGame().IsMultiplayer())
   return;
  weapon.GetInventory().CreateAttachment("AK74_WoodBttstck");
  weapon.GetInventory().CreateAttachment("AK74_Hndgrd");
  EntityAI suppressor = weapon.GetInventory().CreateAttachment("AK_Suppressor");
  EntityAI optic = weapon.GetInventory().CreateAttachment("KobraOptic");
  if (optic)
   optic.GetInventory().CreateAttachment("Battery9V");
  weapon.SpawnAmmo("Mag_AK74_30Rnd");
  int muzzle = weapon.GetCurrentMuzzle();
  int originalMode = weapon.GetCurrentMode(muzzle);
  bool automatic = false;
  for (int mode = 0; mode < weapon.GetMuzzleModeCount(muzzle); mode++)
  {
   weapon.SetCurrentMode(muzzle, mode);
   if (weapon.GetCurrentModeAutoFire(muzzle))
   {
    automatic = true;
    break;
   }
  }
  if (!automatic)
   weapon.SetCurrentMode(muzzle, originalMode);
  Print("[MLADSLEAN102] ak74_full_auto=" + automatic);
  Print("[MLADSLEAN102] ak74_optic_attached=" + (optic != null));
  Print("[MLADSLEAN102] ak74_suppressor_attached=" + (suppressor != null));
 }
};
