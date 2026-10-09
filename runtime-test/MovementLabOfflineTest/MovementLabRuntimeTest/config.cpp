class CfgPatches
{
    class MovementLabRuntimeTest
    {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] = {"DZ_Data", "DZ_Scripts", "DZ_Anims_Anm_Player", "DZ_Anims_Cfg"};
    };
};

class CfgMods
{
    class MovementLabRuntimeTest
    {
        name = "MovementLab arm-lift diagnostic";
        dir = "MovementLabRuntimeTest";
        type = "mod";
        dependencies[] = {"World"};
        class defs
        {
            class worldScriptModule
            {
                value = "";
                files[] = {"MovementLabRuntimeTest/Scripts/4_World"};
            };
        };
    };
};
