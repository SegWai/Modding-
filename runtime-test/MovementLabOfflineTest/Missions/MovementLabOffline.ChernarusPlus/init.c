// A small offline animation diagnostic. No economy or persistent character.
class MovementLabOfflineMission extends MissionGameplay
{
    override void OnInit()
    {
        super.OnInit();

        if (GetGame().IsMultiplayer())
        {
            Print("[MovementLab] This diagnostic mission requires single-player mode.");
            return;
        }

        GetGame().GetWorld().SetDate(2026, 6, 15, 12, 0);
        vector spawn = "14017.8 0 2959.1";
        spawn[1] = GetGame().SurfaceY(spawn[0], spawn[2]) + 0.2;
        PlayerBase player = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Mirek", spawn, 0, "NONE"));
        if (!player)
        {
            Print("[MovementLab] Failed to create the offline test character.");
            return;
        }

        player.GetInventory().CreateInInventory("TShirt_Grey");
        player.GetInventory().CreateInInventory("CargoPants_Black");
        player.GetInventory().CreateInInventory("AthleticShoes_Black");
        player.SetAllowDamage(false);
        player.GetStatWater().Set(player.GetStatWater().GetMax());
        player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
        GetGame().SelectPlayer(null, player);
        Print("[MovementLab] Offline character selected. Stand with empty hands and press F6 for the greeting test.");
    }

    override void OnKeyPress(int key)
    {
        super.OnKeyPress(key);
        if (key != KeyCode.KC_F6 || GetGame().IsMultiplayer())
            return;

        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (!player || !player.GetEmoteManager())
            return;
        if (player.GetItemInHands())
        {
            Print("[MovementLab] Empty your hands before the greeting test.");
            return;
        }

        player.GetEmoteManager().CreateEmoteCBFromMenu(EmoteConstants.ID_EMOTE_GREETING, true);
        Print("[MovementLab] Greeting requested. Baseline uses the original greeting; the test mod replaces its standing loop.");
    }
}

Mission CreateCustomMission(string path)
{
    return new MovementLabOfflineMission();
}
