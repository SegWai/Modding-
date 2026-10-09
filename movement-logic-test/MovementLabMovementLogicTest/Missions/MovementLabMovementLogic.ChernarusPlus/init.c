// Offline A/B experiment with native movement filters and vanilla animations.
class MovementLabMovementLogicMission extends MissionGameplay
{
    protected bool m_MovementLabHeavy = true;
    protected bool m_MovementLabOwnsFilters;
    protected bool m_MovementLabOriginalStaminaInertia;
    protected bool m_MovementLabAnnounce = true;
    protected bool m_MovementLabWasForward;
    protected float m_MovementLabLastSpeed;
    protected bool m_MovementLabBraking;
    protected float m_MovementLabBrakeTime;
    protected float m_MovementLabBrakeStart;
    protected PlayerBase m_MovementLabBrakePlayer;

    protected void MovementLabCancelBrake()
    {
        // Clear only an override this mission actually started.
        if (m_MovementLabBraking && m_MovementLabBrakePlayer)
        {
            HumanInputController input = m_MovementLabBrakePlayer.GetInputController();
            if (input)
            {
                input.OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
                input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
            }
        }
        m_MovementLabBraking = false;
        m_MovementLabBrakePlayer = null;
        m_MovementLabBrakeTime = 0;
        m_MovementLabWasForward = false;
        m_MovementLabLastSpeed = 0;
    }

    protected void MovementLabUpdateBrake(PlayerBase player, float timeslice)
    {
        if (!m_MovementLabHeavy || !player || !player.IsAlive() || !player.GetCommand_Move() || player.IsUnconscious() || player.IsRaised() || player.IsEmotePlaying() || GetUIManager().GetMenu() || IsPaused() || timeslice > 0.25)
        {
            MovementLabCancelBrake();
            return;
        }
        HumanMovementState state = new HumanMovementState();
        player.GetMovementState(state);
        if (state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT)
        {
            MovementLabCancelBrake();
            return;
        }

        // Read physical movement actions, not GetMovement during the override:
        // otherwise the generated coast could feed back and keep itself alive.
        float forward = GetUApi().GetInputByID(UAMoveForward).LocalValue();
        bool otherDirection = GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05;
        if (otherDirection)
        {
            MovementLabCancelBrake();
            return;
        }
        HumanInputController input = player.GetInputController();
        if (!input)
        {
            MovementLabCancelBrake();
            return;
        }
        if (forward > 0.05)
        {
            // A fresh movement input immediately takes control back.
            if (m_MovementLabBraking)
                MovementLabCancelBrake();
            m_MovementLabWasForward = true;
            m_MovementLabLastSpeed = 0;
            if (state.m_iMovement == DayZPlayerConstants.MOVEMENTIDX_SPRINT)
                m_MovementLabLastSpeed = 3.0;
            return;
        }
        if (m_MovementLabWasForward && m_MovementLabLastSpeed > 2.5)
        {
            m_MovementLabBraking = true;
            m_MovementLabBrakePlayer = player;
            m_MovementLabBrakeStart = m_MovementLabLastSpeed;
            m_MovementLabBrakeTime = 0;
            Print("[MovementLab v2] Sprint release: starting 0.85-second braking input ramp.");
        }
        m_MovementLabWasForward = false;
        m_MovementLabLastSpeed = 0;
        if (!m_MovementLabBraking)
            return;
        if (m_MovementLabBrakePlayer != player)
        {
            MovementLabCancelBrake();
            return;
        }
        m_MovementLabBrakeTime = m_MovementLabBrakeTime + Math.Max(timeslice, 0);
        float fraction = Math.Clamp(m_MovementLabBrakeTime / 0.85, 0, 1);
        if (fraction >= 1)
        {
            MovementLabCancelBrake();
            return;
        }
        // 3 = sprint, 2 = jog, 1 = walk, 0 = idle (not metres/second).
        // Let the native controller animate/collide; never move the entity directly.
        float speed = m_MovementLabBrakeStart * (1.0 - fraction);
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ONE_FRAME, speed);
        input.OverrideMovementAngle(HumanInputControllerOverrideType.ONE_FRAME, 0);
    }

    override void OnInit()
    {
        super.OnInit();
        if (GetGame().IsMultiplayer())
            return;

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

    // PlayerBase normally reapplies three stamina modifiers each command tick.
    // Take over those modifiers for this mission, preserving the same formula.
    protected void MovementLabApplyFilters(PlayerBase player, bool heavy)
    {
        HumanCommandMove move = player.GetCommand_Move();
        if (!move)
            return;

        float sprintInertia = 1.0;
        float runSprint = 1.0;
        if (m_MovementLabOriginalStaminaInertia && player.GetStaminaHandler())
        {
            sprintInertia = 2.0 - player.GetStaminaHandler().GetSyncedStaminaNormalized();
            runSprint = sprintInertia * 0.5;
        }

        float direction = 1.0;
        float turn = 1.0;
        float sprintDirection = sprintInertia;
        float sprintTurn = sprintInertia;
        if (heavy)
        {
            runSprint = runSprint * 4.0;
            direction = 2.5;
            sprintDirection = sprintDirection * 2.0;
            turn = 2.5;
            sprintTurn = sprintTurn * 2.5;
        }
        move.SetRunSprintFilterModifier(runSprint);
        move.SetDirectionFilterModifier(direction);
        move.SetDirectionSprintFilterModifier(sprintDirection);
        move.SetTurnSpanModifier(turn);
        move.SetTurnSpanSprintModifier(sprintTurn);
    }

    override void OnUpdate(float timeslice)
    {
        super.OnUpdate(timeslice);
        if (GetGame().IsMultiplayer())
            return;
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        MovementLabUpdateBrake(player, timeslice);
        if (!player || !player.IsAlive() || !player.GetCommand_Move())
            return;
        if (!m_MovementLabOwnsFilters)
        {
            m_MovementLabOriginalStaminaInertia = CfgGameplayHandler.GetAllowStaminaAffectInertia();
            CfgGameplayHandler.m_Data.PlayerData.MovementData.allowStaminaAffectInertia = false;
            m_MovementLabOwnsFilters = true;
        }
        MovementLabApplyFilters(player, m_MovementLabHeavy);
        if (m_MovementLabAnnounce)
        {
            string mode = "VANILLA FILTERS";
            if (m_MovementLabHeavy)
                mode = "HEAVIER + SPRINT BRAKING";
            string message = "[MovementLab v2] " + mode + " - F7 switches mode. Sprint straight, then release W and Shift.";
            player.MessageStatus(message);
            Print(message);
            m_MovementLabAnnounce = false;
        }
    }

    override void OnKeyPress(int key)
    {
        super.OnKeyPress(key);
        if (key == KeyCode.KC_F7 && !GetGame().IsMultiplayer())
        {
            m_MovementLabHeavy = !m_MovementLabHeavy;
            MovementLabCancelBrake();
            m_MovementLabAnnounce = true;
        }
    }

    override void OnMissionFinish()
    {
        MovementLabCancelBrake();
        if (m_MovementLabOwnsFilters)
        {
            PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
            if (player)
                MovementLabApplyFilters(player, false);
            CfgGameplayHandler.m_Data.PlayerData.MovementData.allowStaminaAffectInertia = m_MovementLabOriginalStaminaInertia;
            m_MovementLabOwnsFilters = false;
        }
        super.OnMissionFinish();
    }
}

Mission CreateCustomMission(string path)
{
    return new MovementLabMovementLogicMission();
}
