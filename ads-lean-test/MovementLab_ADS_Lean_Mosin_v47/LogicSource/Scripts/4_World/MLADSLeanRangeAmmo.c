// Offline Mosin reserve refill helper.
class MLADSLeanRangeAmmo
{
 static void Refresh(PlayerBase player)
 {
  if (!player || GetGame().IsMultiplayer() || GetGame().GetPlayer() != player || !player.IsAlive())
   return;
  Weapon_Base weapon = Weapon_Base.Cast(player.GetHumanInventory().GetEntityInHands());
  if (!weapon || (!weapon.IsKindOf("Mosin9130") && !weapon.IsKindOf("AK74")))
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
  Print("[MLADSLEAN47] ak74_full_auto=" + automatic);
  Print("[MLADSLEAN47] ak74_optic_attached=" + (optic != null));
  Print("[MLADSLEAN47] ak74_suppressor_attached=" + (suppressor != null));
 }
};
