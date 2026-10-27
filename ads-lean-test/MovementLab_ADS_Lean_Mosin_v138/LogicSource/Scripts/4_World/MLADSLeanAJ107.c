// Weapon/attachment names come from the loaded AJ configuration, not guesses.
class MLAJPart107
{
 string ClassName;
 bool External;
 ref TStringArray Slots;
};
class MLADSLeanAJ107
{
 static ref array<ref MLAJPart107> s_Parts;
 static bool ExternalModel(string model)
 {
  model.ToLower();
  model.Replace("/", "\\");
  while (model.Length() > 0 && model.IndexOf("\\") == 0)
   model = model.Substring(1, model.Length() - 1);
  return model != "" && model.IndexOf("dz\\") != 0;
 }
 static typename ScriptFor(string type)
 {
  typename missing;
  TStringArray lineage = new TStringArray;
  GetGame().ConfigGetFullPath("CfgWeapons " + type, lineage);
  foreach (string ancestor : lineage)
  {
   typename scriptType = ancestor.ToType();
   if (!scriptType)
    continue;
   // Reject generic fallback classes without a concrete weapon implementation.
   if (ancestor == "Rifle_Base" || ancestor == "BoltActionRifle_Base" || ancestor == "Weapon_Base" || ancestor == "BoltRifle_Base")
    return missing;
   if (scriptType.IsInherited(Weapon_Base))
    return scriptType;
   return missing;
  }
  return missing;
 }
 static int Role(string type, string model, typename scriptType)
 {
  if (scriptType.IsInherited(Pistol_Base) || scriptType.IsInherited(Magnum_Base) || GetGame().IsKindOf(type, "PistolCore"))
   return 2;
  if (scriptType.IsInherited(BoltActionRifle_Base))
   return 3;
  string hint = type + " " + model;
  hint.ToLower();
  if (hint.Contains("smg") || hint.Contains("mp5") || hint.Contains("mp7") || hint.Contains("mp9") || hint.Contains("ump") || hint.Contains("p90") || hint.Contains("vector") || hint.Contains("uzi"))
   return 1;
  if (hint.Contains("sniper") || hint.Contains("dmr") || hint.Contains("m110") || hint.Contains("sr25"))
   return 3;
  return 0;
 }
 static Weapon_Base Equip(PlayerBase player)
 {
  TStringArray types = new TStringArray;
  TStringArray models = new TStringArray;
  TIntArray roles = new TIntArray;
  int count = GetGame().ConfigGetChildrenCount("CfgWeapons");
  for (int index = 0; index < count; index++)
  {
   string type;
   GetGame().ConfigGetChildName("CfgWeapons", index, type);
   string config = "CfgWeapons " + type;
   if (GetGame().ConfigGetInt(config + " scope") != 2)
    continue;
   string model;
   GetGame().ConfigGetText(config + " model", model);
   if (!ExternalModel(model))
    continue;
   typename scriptType = ScriptFor(type);
   if (!scriptType || scriptType.IsInherited(Archery_Base))
    continue;
   model.ToLower();
   types.Insert(type);
   models.Insert(model);
   roles.Insert(Role(type, model, scriptType));
   Print("[MLAJ107] available=" + type + " script=" + scriptType.ToString());
  }
  Print("[MLAJ107] candidate_count=" + types.Count());
  TStringArray usedModels = new TStringArray;
  Weapon_Base primary;
  int attempts;
  int equipped;
  // Prefer a rifle, SMG, handgun and precision rifle, then fill missing roles
  // from other distinct models actually present in AJ's installed version.
  for (int pass = 0; pass < 2; pass++)
  {
   for (int slot = 0; slot < 4; slot++)
   {
    if (pass == 1 && equipped >= 4)
     break;
    for (int candidate = 0; candidate < types.Count(); candidate++)
    {
     if (equipped >= 4 || attempts >= 12)
      break;
     if (pass == 0 && roles[candidate] != slot)
      continue;
     if (usedModels.Find(models[candidate]) != -1)
      continue;
     usedModels.Insert(models[candidate]);
     attempts++;
     Weapon_Base weapon = EquipOne(player, types[candidate], equipped);
     if (!weapon)
      continue;
     if (!primary)
      primary = weapon;
     equipped++;
     if (pass == 0)
      break;
    }
   }
  }
  Print("[MLAJ107] equipped_count=" + equipped);
  if (!primary)
   Print("[MLAJ107] no_usable_weapons_found");
  return primary;
 }
 static Weapon_Base EquipOne(PlayerBase player, string type, int slot)
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
   Print("[MLAJ107] rejected_nonrunning_fsm=" + type + " script=" + weapon.Type().ToString());
   GetGame().ObjectDelete(weapon);
   return null;
  }
  AttachCompatibleParts(weapon);
  string magazine = weapon.GetMaxMagazineTypeName(0);
  bool loaded = weapon.SpawnAmmo(magazine);
  if (!loaded)
   loaded = weapon.SpawnAmmo();
  if (!loaded)
  {
   Print("[MLAJ107] rejected_unloaded=" + type);
   GetGame().ObjectDelete(weapon);
   return null;
  }
  MLADSLeanRangeAmmo.SetAutomatic(weapon);
  player.SetQuickBarEntityShortcut(weapon, slot, true);
  Magazine attached = weapon.GetMagazine(0);
  if (attached)
   MLADSLeanRangeAmmo.SpareMagazine(player, attached.GetType());
  Print("[MLAJ107] equipped=" + type + " quickbar=" + (slot + 1) + " loaded=" + loaded);
  return weapon;
 }
 static void CacheParts()
 {
  if (s_Parts)
   return;
  s_Parts = new array<ref MLAJPart107>;
  int count = GetGame().ConfigGetChildrenCount("CfgVehicles");
  for (int index = 0; index < count; index++)
  {
   string type;
   GetGame().ConfigGetChildName("CfgVehicles", index, type);
   string config = "CfgVehicles " + type;
   if (GetGame().ConfigGetInt(config + " scope") != 2)
    continue;
   TStringArray slots = new TStringArray;
   GetGame().ConfigGetTextArray(config + " inventorySlot", slots);
   if (slots.Count() == 0)
    continue;
   string model;
   GetGame().ConfigGetText(config + " model", model);
   MLAJPart107 part = new MLAJPart107;
   part.ClassName = type;
   part.External = ExternalModel(model);
   part.Slots = slots;
   s_Parts.Insert(part);
  }
 }
 static void AttachCompatibleParts(Weapon_Base weapon)
 {
  CacheParts();
  TStringArray allowed = new TStringArray;
  GetGame().ConfigGetTextArray("CfgWeapons " + weapon.GetType() + " attachments", allowed);
  for (int pass = 0; pass < 2; pass++)
  {
   foreach (MLAJPart107 candidate : s_Parts)
   {
    if ((pass == 0 && !candidate.External) || (pass == 1 && candidate.External))
     continue;
    foreach (string slot : candidate.Slots)
    {
     if (allowed.Find(slot) == -1 || weapon.FindAttachmentBySlotName(slot))
      continue;
     EntityAI part = weapon.GetInventory().CreateAttachment(candidate.ClassName);
     if (!part)
      continue;
     if (part.GetCompEM())
      part.GetInventory().CreateAttachment("Battery9V");
     Print("[MLAJ107] weapon=" + weapon.GetType() + " attachment=" + candidate.ClassName);
     break;
    }
   }
  }
 }
};
