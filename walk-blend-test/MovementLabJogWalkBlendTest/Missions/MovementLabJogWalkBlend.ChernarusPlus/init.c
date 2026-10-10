// Standalone native movement: only the jog-to-walk handoff is changed.
class MovementLabJogWalkBlendMission extends MissionGameplay
{
    override void OnInit()
    {
        super.OnInit();
        if (GetGame().IsMultiplayer())
            return;

        MovementLabStartGate.Enabled = true;
        GetGame().GetWorld().SetDate(2026, 6, 15, 12, 0);
        vector spawn = "14017.8 0 2959.1";
        spawn[1] = GetGame().SurfaceY(spawn[0], spawn[2]) + 0.2;
        PlayerBase player = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Mirek", spawn, 0, "NONE"));
        if (!player)
        {
            Print("[MovementLab] Could not create the offline character.");
            return;
        }
        player.GetInventory().CreateInInventory("TShirt_Grey");
        player.GetInventory().CreateInInventory("CargoPants_Black");
        player.GetInventory().CreateInInventory("AthleticShoes_Black");
        player.SetAllowDamage(false);
        player.GetStatWater().Set(player.GetStatWater().GetMax());
        player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
        GetGame().SelectPlayer(null, player);
    }


    override void OnKeyPress(int key)
    {
        super.OnKeyPress(key);
        if (key == KeyCode.KC_F7 && !GetGame().IsMultiplayer())
        {
            MovementLabStartGate.Enabled = !MovementLabStartGate.Enabled;
            PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
            if (player)
            {
                player.MovementLabCancelWalkBlend();
                if (MovementLabStartGate.Enabled)
                    player.MessageStatus("Jog-to-walk blend ON. Jog, then hold Ctrl. F7 compares vanilla.");
                else
                    player.MessageStatus("Jog-to-walk blend OFF: vanilla movement.");
            }
        }
    }

    override void OnMissionFinish()
    {
        MovementLabStartGate.Enabled = false;
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (player)
            player.MovementLabCancelWalkBlend();
        super.OnMissionFinish();
    }
}

Mission CreateCustomMission(string path)
{
    return new MovementLabJogWalkBlendMission();
}
