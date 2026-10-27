// Exact weapon and magazine names from the user-supplied Panacea types.xml.
class MLADSLeanPanacea104
{
 static void Equip(PlayerBase player)
 {
  EquipOne(player, "PNC_W_SCARH", "PNC_SCARH_20Rnd", 0);
  EquipOne(player, "PNC_W_HoneyBadger", "PNC_HoneyBadger_30Rnd", 1);
  EquipOne(player, "PNC_W_AWM", "PNC_Mag_AWM_5Rnd", 2);
  EquipOne(player, "PNC_W_Origin_12ga", "PNC_Origin_Mag", 3);
 }
 static void EquipOne(PlayerBase player, string weaponType, string magazineType, int slot)
 {
  if (!GetGame().ConfigIsExisting("CfgWeapons " + weaponType))
  {
   Print("[MLPANACEA104] MISSING weapon=" + weaponType);
   NotificationSystem.AddNotificationExtended(15, "Panacea weapon missing", weaponType + ": check that The Panacea Weapons is installed and loaded.");
   return;
  }
  Weapon_Base weapon;
  if (slot == 0)
   weapon = Weapon_Base.Cast(player.GetHumanInventory().CreateInHands(weaponType));
  else
   weapon = MLADSLeanRangeAmmo.CreateStoredWeapon(player, weaponType, slot == 1);
  if (!weapon)
  {
   Print("[MLPANACEA104] FAILED spawn=" + weaponType);
   return;
  }
  AttachCompatibleParts(weapon);
  bool loaded = weapon.SpawnAmmo(magazineType);
  player.SetQuickBarEntityShortcut(weapon, slot, true);
  MLADSLeanRangeAmmo.SpareMagazine(player, magazineType);
  Print("[MLPANACEA104] equipped=" + weaponType + " magazine=" + magazineType + " ammo=" + loaded);
 }
 static void AttachCompatibleParts(Weapon_Base weapon)
 {
  TStringArray slots = new TStringArray;
  GetGame().ConfigGetTextArray("CfgWeapons " + weapon.GetType() + " attachments", slots);
  TStringArray parts = {"PNC_Suppressor_408Cheytac", "PNC_Suppressor556mm", "PNC_Suppressor556mm_2", "PNC_Aurora_Suppressor", "PNC_BarretM82A1_Suppressor", "PNC_BarretM82A1_Suppressor_black", "PNC_BarretM82A1_Suppressor_desert", "PNC_Suppressor_338", "PNC_Fal_Compensator_1", "PNC_Fal_Compensator_2", "PNC_Fal_RISHndgrd", "PNC_Fal_PlasticHndgrd", "PNC_Fal_WoodenHndgrd", "PNC_Suppressor_762x39mm_Legion", "PNC_Fal_OeBttstckWooden", "PNC_Fal_OeBttstck", "PNC_Suppressor_65_Creedmore", "PNC_Suppressor_65_Creedmore_tan", "PNC_Suppressor_65_Creedmore_Green", "ACOGOptic", "HuntingOptic", "ReflexOptic", "M4_T3NRDSOptic", "UniversalLight"};
  foreach (string partType : parts)
  {
   string config = "CfgVehicles " + partType;
   if (!GetGame().ConfigIsExisting(config))
    continue;
   TStringArray partSlots = new TStringArray;
   GetGame().ConfigGetTextArray(config + " inventorySlot", partSlots);
   foreach (string slot : partSlots)
   {
    if (slots.Find(slot) == -1 || weapon.FindAttachmentBySlotName(slot))
     continue;
    EntityAI part = weapon.GetInventory().CreateAttachment(partType);
    if (part)
    {
     Print("[MLPANACEA104] weapon=" + weapon.GetType() + " attachment=" + partType);
     if (part.GetCompEM())
      part.GetInventory().CreateAttachment("Battery9V");
     break;
    }
   }
  }
 }
};
