// Classify the real held firearm, including modded subclasses. No classname allowlist.
class MLADSLeanWeaponSupport106
{
 // 0 unsupported, 1 shouldered firearm, 2 handgun.
 static int Profile(EntityAI item)
 {
  Weapon_Base weapon = Weapon_Base.Cast(item);
  if (!weapon || weapon.GetMuzzleCount() < 1 || weapon.IsKindOf("Archery_Base"))
   return 0;
  if (weapon.IsKindOf("Pistol_Base") || weapon.IsKindOf("Magnum_Base"))
   return 2;
  if (GetGame().IsKindOf(weapon.GetType(), "PistolCore"))
   return 2;
  return 1;
 }
 static bool Supported(EntityAI item)
 {
  return Profile(item) > 0;
 }
};
