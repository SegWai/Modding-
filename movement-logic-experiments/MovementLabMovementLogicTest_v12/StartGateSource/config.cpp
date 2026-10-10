class CfgPatches
{
    class MovementLabStartGate
    {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] = {"DZ_Data", "DZ_Scripts"};
    };
};
class CfgMods
{
    class MovementLabStartGate
    {
        name = "MovementLab walking start gate";
        dir = "MovementLabStartGate";
        type = "mod";
        dependencies[] = {"World"};
        class defs
        {
            class worldScriptModule
            {
                value = "";
                files[] = {"MovementLabStartGate/Scripts/4_World"};
            };
        };
    };
};
