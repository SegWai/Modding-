class CfgPatches
{
    class MovementLabStartGate
    {
        units[] = {"MovementLabTestBackpack", "MovementLabArmsPreviewItem"};
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
        dependencies[] = {"World", "Mission"};
        class defs
        {
            class missionScriptModule
            {
                value = "";
                files[] = {"MovementLabStartGate/Scripts/5_Mission"};
            };
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
    class Inventory_Base;
    class MovementLabArmsPreviewItem: Inventory_Base
    {
        scope = 2;
        displayName = "MovementLab static arms renderer diagnostic";
        descriptionShort = "Local renderer fixture, not equipment.";
        model = "\MovementLabStartGate\Models\arms_only.p3d";
        itemSize[] = {1,1};
        weight = 1;
        rotationFlags = 0;
    };
    class AssaultBag_Black;
    class MovementLabTestBackpack: AssaultBag_Black
    {
        scope = 2;
        displayName = "MovementLab Black Assault Backpack";
        descriptionShort = "Shooting test backpack: 100 cargo slots and two weapon attachments.";
        itemsCargoSize[] = {10,10};
        attachments[] = {"Shoulder", "Melee"};
    };
};
