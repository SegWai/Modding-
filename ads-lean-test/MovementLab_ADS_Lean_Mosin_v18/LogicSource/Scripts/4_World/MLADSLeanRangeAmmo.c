// Offline Mosin reserve refill helper.
class MLADSLeanRangeAmmo
{
 static void Refresh(PlayerBase player)
 {
  if (!player || GetGame().IsMultiplayer() || GetGame().GetPlayer() != player || !player.IsAlive())
   return;
  Weapon_Base weapon = Weapon_Base.Cast(player.GetHumanInventory().GetEntityInHands());
  if (!weapon || !weapon.IsKindOf("Mosin9130"))
   return;
  weapon.SetHealthMax("", "Health");
  ItemBase suppressor = weapon.GetAttachedSuppressor();
  if (suppressor)
   suppressor.SetHealthMax("", "Health");
  // Preserve the native bolt/FSM and chamber. Refill only the internal reserve.
  if (player.GetWeaponManager() && player.GetWeaponManager().IsRunning())
   return;
  int muzzle = weapon.GetCurrentMuzzle();
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
};
