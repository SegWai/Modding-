class CfgPatches
{
 class MLADSLeanLogic
 {
  units[] = {};
  weapons[] = {};
  requiredVersion = 0.1;
  requiredAddons[] = {"DZ_Data", "DZ_Scripts", "DZ_Anims_Cfg"};
 };
};
class CfgMods
{
 class MLADSLeanLogic
 {
  name = "MovementLab Mosin ADS Lean Test v5";
  dir = "MLADSLeanLogic";
  type = "mod";
  dependencies[] = {"World", "Mission"};
  class defs
  {
   class worldScriptModule { value = ""; files[] = {"MLADSLeanLogic/Scripts/4_World"}; };
   class missionScriptModule { value = ""; files[] = {"MLADSLeanLogic/Scripts/5_Mission"}; };
  };
 };
};
