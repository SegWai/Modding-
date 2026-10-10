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
    protected float m_MovementLabBrakeTarget;
    protected float m_MovementLabBrakeDuration;
    protected float m_MovementLabBrakeSpeed;
    protected bool m_MovementLabWasTurbo;
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
        m_MovementLabWasTurbo = false;
    }

    protected void MovementLabBeginBrake(PlayerBase player, float start, float target, float duration)
    {
        m_MovementLabBraking = true;
        m_MovementLabBrakePlayer = player;
        m_MovementLabBrakeStart = start;
        m_MovementLabBrakeSpeed = start;
        m_MovementLabBrakeTarget = target;
        m_MovementLabBrakeDuration = duration;
        m_MovementLabBrakeTime = 0;
        Print("[MovementLab v3] Braking input target=" + target + ", duration=" + duration);
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
        bool turbo = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
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
        if (m_MovementLabBraking && forward > 0.05 && (m_MovementLabBrakeTarget == 0 || turbo))
        {
            // Resume movement immediately; keeping W down during Shift braking
            // does not cancel the sprint-to-jog transition.
            MovementLabCancelBrake();
        }
        if (m_MovementLabBraking && m_MovementLabBrakeTarget > 0 && forward <= 0.05)
        {
            // Releasing W during the Shift ramp continues from the current
            // request, avoiding a jump back up to full sprint.
            float duration = Math.Max(1.0, 2.2 * m_MovementLabBrakeSpeed / 3.0);
            MovementLabBeginBrake(player, m_MovementLabBrakeSpeed, 0, duration);
        }
        if (!m_MovementLabBraking && m_MovementLabWasForward && m_MovementLabLastSpeed > 2.5)
        {
            if (forward <= 0.05)
                MovementLabBeginBrake(player, 3.0, 0, 2.2);
            else if (m_MovementLabWasTurbo && !turbo)
                MovementLabBeginBrake(player, 3.0, 2.0, 1.6);
        }
        if (!m_MovementLabBraking && forward > 0.05)
        {
            m_MovementLabWasForward = true;
            m_MovementLabWasTurbo = turbo;
            m_MovementLabLastSpeed = 0;
            if (state.m_iMovement == DayZPlayerConstants.MOVEMENTIDX_SPRINT)
                m_MovementLabLastSpeed = 3.0;
            return;
        }
        m_MovementLabWasForward = false;
        m_MovementLabWasTurbo = false;
        m_MovementLabLastSpeed = 0;
        if (!m_MovementLabBraking)
            return;
        if (m_MovementLabBrakePlayer != player)
        {
            MovementLabCancelBrake();
            return;
        }
        m_MovementLabBrakeTime = m_MovementLabBrakeTime + Math.Max(timeslice, 0);
        float fraction = Math.Clamp(m_MovementLabBrakeTime / m_MovementLabBrakeDuration, 0, 1);
        if (fraction >= 1)
        {
            MovementLabCancelBrake();
            return;
        }
        // 3 = sprint, 2 = jog, 1 = walk, 0 = idle (not metres/second).
        // Let the native controller animate/collide; never move the entity directly.
        // Full-stop ramp stays faster for longer than v2's linear curve.
        // Shift-only ramp eases at both ends into continued jogging.
        float blend = fraction * fraction;
        if (m_MovementLabBrakeTarget > 0)
            blend = fraction * fraction * (3.0 - 2.0 * fraction);
        m_MovementLabBrakeSpeed = m_MovementLabBrakeStart + (m_MovementLabBrakeTarget - m_MovementLabBrakeStart) * blend;
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ONE_FRAME, m_MovementLabBrakeSpeed);
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
            string message = "[MovementLab v3] " + mode + " - F7 switches mode. Test Shift release, then W + Shift release.";
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
