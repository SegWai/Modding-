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
    class AssaultBag_Black;
    class MovementLabTestBackpack: AssaultBag_Black
    {
        scope = 2;
        displayName = "MovementLab Black Assault Backpack";
        descriptionShort = "Shooting test backpack: 42 cargo slots and two weapon attachments.";
        itemsCargoSize[] = {7,6};
        attachments[] = {"Shoulder", "Melee"};
    };
};
