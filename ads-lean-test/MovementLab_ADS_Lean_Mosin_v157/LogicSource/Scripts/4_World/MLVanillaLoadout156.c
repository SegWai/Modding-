// Native DayZ firearms only; no Workshop weapon or framework dependency.
class MLVanillaLoadout156
{
 static Weapon_Base Create(PlayerBase player, string type, int slot)
 {
  Weapon_Base weapon;
  if (slot == 0)
   weapon = Weapon_Base.Cast(player.GetHumanInventory().CreateInHands(type));
  else
   weapon = MLADSLeanRangeAmmo.CreateStoredWeapon(player, type, slot == 1);
  if (!weapon)
   return null;
  if (!weapon.CanProcessWeaponEvents())
  {
   Print("[MLLOADOUT156] native FSM unavailable: " + type);
   GetGame().ObjectDelete(weapon);
   return null;
  }
  player.SetQuickBarEntityShortcut(weapon, slot, true);
  return weapon;
 }
 static void Load(Weapon_Base weapon, string magazine)
 {
  if (!weapon)
   return;
  bool loaded = weapon.SpawnAmmo(magazine);
  if (!loaded)
   loaded = weapon.SpawnAmmo();
  Print("[MLLOADOUT156] weapon=" + weapon.GetType() + " loaded=" + loaded);
 }
 static Weapon_Base Equip(PlayerBase player)
 {
  if (!player || GetGame().IsMultiplayer())
   return null;
  Weapon_Base ak = Create(player, "AK74", 0);
  if (ak)
  {
   MLADSLeanRangeAmmo.AttachPart(ak, "AK_PlasticBttstck");
   MLADSLeanRangeAmmo.AttachPart(ak, "AK_RailHndgrd");
   MLADSLeanRangeAmmo.AttachPart(ak, "AK_Suppressor");
   MLADSLeanRangeAmmo.AttachPoweredPart(ak, "KobraOptic");
   MLADSLeanRangeAmmo.AttachPoweredPart(ak, "UniversalLight");
   Load(ak, "Mag_AK74_30Rnd");
   MLADSLeanRangeAmmo.SetAutomatic(ak);
  }
  Weapon_Base sks = Create(player, "SKS", 1);
  if (sks)
  {
   MLADSLeanRangeAmmo.AttachPart(sks, "PUScopeOptic");
   MLADSLeanRangeAmmo.AttachPart(sks, "SKS_Bayonet");
   // Attach only if accepted by the native weapon/attachment configuration.
   MLADSLeanRangeAmmo.AttachPart(sks, "ImprovisedSuppressor");
   Load(sks, "");
  }
  Weapon_Base glock = Create(player, "Glock19", 2);
  if (glock)
  {
   MLADSLeanRangeAmmo.AttachPart(glock, "PistolSuppressor");
   MLADSLeanRangeAmmo.AttachPoweredPart(glock, "TLRLight");
   Load(glock, "Mag_Glock_15Rnd");
  }
  for (int spare = 0; spare < 3; spare++)
  {
   MLADSLeanRangeAmmo.SpareMagazine(player, "Mag_AK74_30Rnd");
   MLADSLeanRangeAmmo.SpareMagazine(player, "Mag_Glock_15Rnd");
   player.GetInventory().CreateInInventory("AmmoBox_762x39_20Rnd");
  }
  return ak;
 }
};
