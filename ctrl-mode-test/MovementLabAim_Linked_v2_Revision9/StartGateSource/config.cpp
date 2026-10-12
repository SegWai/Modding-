class CfgPatches
{
    class MovementLabStartGate
    {
        units[] = {"MovementLabTestBackpack"};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] = {"DZ_Data", "DZ_Scripts", "DZ_Characters_Backpacks", "MovementLabCrouchWheelWorkspace"};
    };
};
class CfgMods
{
    class MovementLabStartGate
    {
        name = "MovementLab Ctrl walking and jogging modes";
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

class CfgVehicles
{
    class AliceBag_Green;
    class MovementLabTestBackpack: AliceBag_Green
    {
        scope = 2;
        displayName = "MovementLab Field Backpack";
        descriptionShort = "Shooting test backpack: 90 cargo slots and two weapon attachments.";
        itemsCargoSize[] = {10,9};
        attachments[] = {"Shoulder", "Melee"};
    };
};
