// Offline A/B experiment with native movement filters and vanilla animations.
class MovementLabMovementLogicMission extends MissionGameplay
{
    protected bool m_MovementLabHeavy = true;
    protected bool m_MovementLabOwnsFilters;
    protected bool m_MovementLabOriginalStaminaInertia;
    protected bool m_MovementLabAnnounce = true;
    protected bool m_MovementLabWasMoving;
    protected float m_MovementLabLastSpeed;
    protected bool m_MovementLabBraking;
    protected float m_MovementLabBrakeTime;
    protected float m_MovementLabBrakeStart;
    protected float m_MovementLabBrakeTarget;
    protected float m_MovementLabBrakeDuration;
    protected float m_MovementLabBrakeSpeed;
    protected bool m_MovementLabWasTurbo;
    protected float m_MovementLabSprintExposure;
    protected float m_MovementLabBrakeStopDuration;
    protected float m_MovementLabLastAngle;
    protected float m_MovementLabBrakeAngle;
    protected int m_MovementLabLastKeys;
    protected int m_MovementLabBrakeKeys;
    protected PlayerBase m_MovementLabBrakePlayer;
    protected void MovementLabCancelStart()
    {
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (player)
            player.MovementLabCancelStart();
    }

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
        if (m_MovementLabBrakePlayer)
            m_MovementLabBrakePlayer.MovementLabSetBrakingActive(false);
        m_MovementLabBraking = false;
        m_MovementLabBrakePlayer = null;
        m_MovementLabBrakeTime = 0;
        m_MovementLabWasMoving = false;
        m_MovementLabLastSpeed = 0;
        m_MovementLabWasTurbo = false;
        m_MovementLabSprintExposure = 0;
    }

    protected void MovementLabBeginBrake(PlayerBase player, float start, float target, float duration)
    {
        if (!m_MovementLabBraking)
        {
            m_MovementLabBrakeAngle = m_MovementLabLastAngle;
            m_MovementLabBrakeKeys = m_MovementLabLastKeys;
            // A/D-only stopping must retain the input's sideways direction,
            // rather than a possibly forward-facing current animation angle.
            if (m_MovementLabBrakeKeys == 4)
                m_MovementLabBrakeAngle = -90.0;
            else if (m_MovementLabBrakeKeys == 8)
                m_MovementLabBrakeAngle = 90.0;
            else if (m_MovementLabBrakeKeys == 2)
                m_MovementLabBrakeAngle = 180.0;
        }
        player.MovementLabSetBrakingActive(true);
        m_MovementLabBraking = true;
        m_MovementLabBrakePlayer = player;
        m_MovementLabBrakeStart = start;
        m_MovementLabBrakeSpeed = start;
        m_MovementLabBrakeTarget = target;
        m_MovementLabBrakeDuration = duration;
        m_MovementLabBrakeTime = 0;
        Print("[MovementLab v13] Braking input start=" + start + ", target=" + target + ", duration=" + duration + ", angle=" + m_MovementLabBrakeAngle);
    }

    protected void MovementLabUpdateBrake(PlayerBase player, float timeslice)
    {
        if (!m_MovementLabHeavy || !player || !player.IsAlive() || !player.GetCommand_Move() || player.IsUnconscious() || player.IsRaised() || player.IsEmotePlaying() || GetUIManager().GetMenu() || IsPaused() || timeslice > 0.25)
        {
            MovementLabCancelStart();
            MovementLabCancelBrake();
            return;
        }
        HumanMovementState state = new HumanMovementState();
        player.GetMovementState(state);
        if (state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT)
        {
            MovementLabCancelStart();
            MovementLabCancelBrake();
            return;
        }

        // Read physical movement actions, not GetMovement during the override:
        // otherwise the generated coast could feed back and keep itself alive.
        // Direction keys are sampled independently from the generated coast.
        // Keep diagonals eligible; v4 wrongly canceled on every A/D press.
        int movementKeys = 0;
        if (GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05)
            movementKeys = movementKeys + 1;
        if (GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05)
            movementKeys = movementKeys + 2;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05)
            movementKeys = movementKeys + 4;
        if (GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            movementKeys = movementKeys + 8;
        bool movingInput = movementKeys != 0;
        bool turbo = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
        HumanInputController input = player.GetInputController();
        if (!input)
        {
            MovementLabCancelStart();
            MovementLabCancelBrake();
            return;
        }
        if (m_MovementLabBraking && movingInput && (m_MovementLabBrakeTarget == 0 || turbo || movementKeys != m_MovementLabBrakeKeys))
        {
            // New input takes control back. The original held diagonal keys
            // do not cancel a Shift-only sprint-to-jog transition.
            MovementLabCancelBrake();
        }
        if (m_MovementLabBraking && m_MovementLabBrakeTarget > 0 && !movingInput)
        {
            // Releasing all movement keys during the Shift ramp continues from the current
            // request, avoiding a jump back up to full sprint.
            float duration = Math.Max(0.18, m_MovementLabBrakeStopDuration * m_MovementLabBrakeSpeed / m_MovementLabBrakeStart);
            MovementLabBeginBrake(player, m_MovementLabBrakeSpeed, 0, duration);
        }
        if (!m_MovementLabBraking && m_MovementLabWasMoving && m_MovementLabLastSpeed > 2.05 && m_MovementLabSprintExposure > 0)
        {
            // Use the achieved gait, not the sprint command/state or a fixed 3.
            // A brief Shift tap must not get a full-sprint braking tail.
            float sprintAmount = Math.Clamp(m_MovementLabLastSpeed - 2.0, 0, 1);
            float sustained = Math.Clamp(m_MovementLabSprintExposure / 0.45, 0, 1);
            float weight = sprintAmount * sustained;
            m_MovementLabBrakeStopDuration = 0.18 + 0.97 * weight;
            if (!movingInput)
                MovementLabBeginBrake(player, m_MovementLabLastSpeed, 0, m_MovementLabBrakeStopDuration);
            else if (m_MovementLabWasTurbo && !turbo && movementKeys == m_MovementLabLastKeys)
                MovementLabBeginBrake(player, m_MovementLabLastSpeed, 2.0, 0.12 + 0.33 * weight);
        }
        if (!m_MovementLabBraking && m_MovementLabWasMoving && !movingInput && m_MovementLabLastSpeed >= 1.75 && m_MovementLabLastSpeed <= 2.05)
        {
            // A small settling tail for achieved jogging, in any direction.
            // Do not require Shift, promote walking, or reuse sprint exposure.
            m_MovementLabBrakeStopDuration = 0.42 * Math.Min(m_MovementLabLastSpeed / 2.0, 1.0);
            // Backward jogging settles almost immediately: a brief walk back
            // before idle, shorter than the lateral walking tail.
            if (m_MovementLabLastKeys == 2)
                m_MovementLabBrakeStopDuration = 0.18 * Math.Min(m_MovementLabLastSpeed / 2.0, 1.0);
            MovementLabBeginBrake(player, m_MovementLabLastSpeed, 0, m_MovementLabBrakeStopDuration);
        }
        if (!m_MovementLabBraking && movingInput)
        {
            m_MovementLabWasMoving = true;
            m_MovementLabLastKeys = movementKeys;
            m_MovementLabLastAngle = player.GetCommand_Move().GetCurrentMovementAngle();
            m_MovementLabWasTurbo = turbo;
            m_MovementLabLastSpeed = Math.Clamp(player.GetCommand_Move().GetCurrentMovementSpeed(), 0, 3);
            // A starting walk/jog request cannot count as achieved sprint just
            // because native state briefly precedes the first override frame.
            if (player.MovementLabIsStarting())
                m_MovementLabLastSpeed = Math.Min(m_MovementLabLastSpeed, player.MovementLabGetStartSpeed());
            if (turbo && m_MovementLabLastSpeed > 2.05)
                m_MovementLabSprintExposure = Math.Min(0.45, m_MovementLabSprintExposure + Math.Max(timeslice, 0));
            else
                m_MovementLabSprintExposure = 0;
            return;
        }
        m_MovementLabWasMoving = false;
        m_MovementLabWasTurbo = false;
        m_MovementLabLastSpeed = 0;
        m_MovementLabSprintExposure = 0;
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
        // Slow down immediately: do not linger at sprint at the start.
        // Ease toward the final gait as the remaining input approaches zero.
        float blend = 2.0 * fraction - fraction * fraction;
        m_MovementLabBrakeSpeed = m_MovementLabBrakeStart + (m_MovementLabBrakeTarget - m_MovementLabBrakeStart) * blend;
        // Redistribute an achieved near/full-sprint stop's existing time:
        // prompt sprint-to-jog, longer jog, then a short walking finish.
        // The duration/deadline and all lower-gait stops stay unchanged.
        if (m_MovementLabBrakeTarget == 0 && m_MovementLabBrakeStart >= 2.5)
        {
            if (fraction < 0.18)
            {
                float sprintBlend = fraction / 0.18;
                sprintBlend = 2.0 * sprintBlend - sprintBlend * sprintBlend;
                m_MovementLabBrakeSpeed = m_MovementLabBrakeStart + (2.0 - m_MovementLabBrakeStart) * sprintBlend;
            }
            else if (fraction < 0.62)
                m_MovementLabBrakeSpeed = 2.0;
            else if (fraction < 0.82)
            {
                float jogBlend = (fraction - 0.62) / 0.20;
                jogBlend = jogBlend * jogBlend * (3.0 - 2.0 * jogBlend);
                m_MovementLabBrakeSpeed = 2.0 - jogBlend;
            }
            else if (fraction < 0.92)
                m_MovementLabBrakeSpeed = 1.0;
            else
            {
                float walkBlend = (fraction - 0.92) / 0.08;
                walkBlend = 2.0 * walkBlend - walkBlend * walkBlend;
                m_MovementLabBrakeSpeed = 1.0 - walkBlend;
            }
        }
        // During the settling portion of a pure lateral stop, request the
        // actual walk gait (1) instead of a fractional sub-walk/idle blend.
        // At the existing deadline, releasing the override allows full idle.
        if (m_MovementLabBrakeTarget == 0 && (m_MovementLabBrakeKeys == 4 || m_MovementLabBrakeKeys == 8))
            m_MovementLabBrakeSpeed = Math.Max(1.0, m_MovementLabBrakeSpeed);
        // S-only: request the vanilla backward walk immediately for the very
        // short tail, then release to idle. Never boost a slower starting gait.
        if (m_MovementLabBrakeTarget == 0 && m_MovementLabBrakeKeys == 2)
            m_MovementLabBrakeSpeed = Math.Min(1.0, m_MovementLabBrakeStart);
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ONE_FRAME, m_MovementLabBrakeSpeed);
        input.OverrideMovementAngle(HumanInputControllerOverrideType.ONE_FRAME, m_MovementLabBrakeAngle);
    }

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
        // Preserve startup filters, but do not let their long sprint span
        // fight the braking request after the user has released Shift/W.
        if (m_MovementLabBraking)
            runSprint = 0.35;
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
                mode = "HEAVIER + STARTS + BRAKING";
            string message = "[MovementLab v13] " + mode + " - F7 switches mode. F8 toggles 0.32s native bracing on A/D and W/S reversals.";
            player.MessageStatus(message);
            Print(message);
            m_MovementLabAnnounce = false;
        }
    }

    override void OnKeyPress(int key)
    {
        super.OnKeyPress(key);
        if (key == KeyCode.KC_F8 && !GetGame().IsMultiplayer())
        {
            MovementLabPoseSettings.Enabled = !MovementLabPoseSettings.Enabled;
            PlayerBase posePlayer = PlayerBase.Cast(GetGame().GetPlayer());
            if (posePlayer)
                posePlayer.MessageStatus("[MovementLab v13] Reversal pose enabled=" + MovementLabPoseSettings.Enabled + ", hold=0.32s. V11 movement timings retained.");
        }
        if (key == KeyCode.KC_F7 && !GetGame().IsMultiplayer())
        {
            m_MovementLabHeavy = !m_MovementLabHeavy;
            MovementLabStartGate.Enabled = m_MovementLabHeavy;
            MovementLabCancelStart();
            MovementLabCancelBrake();
            m_MovementLabAnnounce = true;
        }
    }

    override void OnMissionFinish()
    {
        MovementLabStartGate.Enabled = false;
        MovementLabCancelStart();
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
