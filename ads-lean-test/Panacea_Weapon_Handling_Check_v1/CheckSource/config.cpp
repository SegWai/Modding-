class CfgPatches
{
 class PWHC { units[] = {}; weapons[] = {}; requiredVersion = 0.1; requiredAddons[] = {"DZ_Data", "DZ_Scripts"}; };
};
class CfgMods
{
 class PWHC
 {
  name = "Panacea Native Weapon Handling Check";
  dir = "PWHC";
  type = "mod";
  dependencies[] = {"World"};
  class defs { class worldScriptModule { value = ""; files[] = {"PWHC/Scripts/4_World"}; }; };
 };
};
