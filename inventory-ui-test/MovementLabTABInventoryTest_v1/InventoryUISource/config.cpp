class CfgPatches
{
    class MovementLabInventoryUI
    {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] = {"DZ_Data", "DZ_Scripts"};
    };
};
class CfgMods
{
    class MovementLabInventoryUI
    {
        name = "MovementLab reference-style TAB inventory";
        dir = "MovementLabInventoryUI";
        type = "mod";
        dependencies[] = {"Mission"};
        class defs
        {
            class missionScriptModule
            {
                value = "";
                files[] = {"MovementLabInventoryUI/Scripts/5_Mission"};
            };
        };
    };
};
