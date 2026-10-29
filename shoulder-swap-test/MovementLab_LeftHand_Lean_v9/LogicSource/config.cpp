class CfgPatches
{
 class MLAmbidextrousLogic
 {
  units[] = {};
  weapons[] = {};
  requiredVersion = 0.1;
  requiredAddons[] = {"DZ_Data", "DZ_Scripts", "DZ_Anims_Cfg"};
 };
};
class CfgMods
{
 class MLAmbidextrousLogic
 {
  name = "MovementLab Fixed Left-Hand Lean - Experimental v9";
  dir = "MLAmbidextrousLogic";
  type = "mod";
  dependencies[] = {"World", "Mission"};
  class defs
  {
   class worldScriptModule { value = ""; files[] = {"MLAmbidextrousLogic/Scripts/4_World"}; };
   class missionScriptModule { value = ""; files[] = {"MLAmbidextrousLogic/Scripts/5_Mission"}; };
  };
 };
};
