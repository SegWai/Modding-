// Loaded before the loose mission. Only its offline mission enables the gate.
class MovementLabStartGate
{
    static bool Enabled;
}

modded class PlayerBase
{
    protected int m_MovementLabWalkLevelVar = -1;
    protected int m_MovementLabWalkLevel = 1;
    protected int m_MovementLabJogLevel = 2;
    protected bool m_MovementLabScrollSprint;
    protected int m_MovementLabSprintLevel = 2;
    protected float m_MovementLabTravelProbeTime;
    protected float m_MovementLabTravelProbeBase;
    protected float m_MovementLabTravelProbeApplied;
    protected bool m_MovementLabGroundSampleKnown;
    protected int m_MovementLabGroundSampleLevel;
    protected float m_MovementLabGroundX;
    protected float m_MovementLabGroundZ;
    protected float m_MovementLabGroundTime;
    protected float m_MovementLabGroundDistance;
    protected bool m_MovementLabWalkBindReported;
    protected int m_MovementLabWalkReportedLevel;
    protected bool m_MovementLabWalkWheelWasCrouching;
    protected bool m_MovementLabStartOwnsSpeed;
    protected bool m_MovementLabIdleArmed;
    protected bool m_MovementLabStarting;
    protected bool m_MovementLabWasInput;
    protected bool m_MovementLabBrakeActive;
    protected float m_MovementLabStartTime;
    protected float m_MovementLabStartSpeed;
    protected bool m_MovementLabWalkMode;
    protected bool m_MovementLabCtrlDown;
    protected float m_MovementLabLastWantedGait = 2.0;
    protected bool m_MovementLabModeDecreasePending;
    protected bool m_MovementLabWasCrouching;
    protected bool m_MovementLabFastCrouch;
    protected bool m_MovementLabCrouchShiftConsumed;

    protected int m_MovementLabSlowLastSide;
    protected float m_MovementLabSlowGap;
    protected float m_MovementLabSlowHeld;
    protected bool m_MovementLabStrafeSlow;

    protected bool m_MovementLabWheelWasCrouching;
    protected bool m_MovementLabWheelStandingSprint;
    protected int m_MovementLabCrouchLevel = 3;
    protected int m_MovementLabCrouchLevelVar = -1;
    protected bool m_MovementLabCrouchBindReported;

    protected void MovementLabApplyStandingWheelBoundaries()
    {
        if (m_MovementLabWalkMode && m_MovementLabWalkLevel >= 4)
        {
            // Walking121% is a mode boundary: native jogging, not a faster walk.
            m_MovementLabWalkLevel = 3;
            m_MovementLabJogLevel = 2;
            m_MovementLabWalkMode = false;
            Print("[MovementLab Linked Wheel] Walk121% boundary -> jog80%");
        }
        else if (m_MovementLabScrollSprint && m_MovementLabSprintLevel <= 1)
        {
            m_MovementLabScrollSprint = false;
            m_MovementLabSprintLevel = 2;
            m_MovementLabJogLevel = 3;
            m_MovementLabWalkMode = false;
            Print("[MovementLab Linked Wheel] Sprint99% -> jog100%");
        }
        else if (!m_MovementLabWalkMode && !m_MovementLabScrollSprint && m_MovementLabJogLevel <= 1)
        {
            m_MovementLabJogLevel = 2;
            m_MovementLabWalkLevel = 1;
            m_MovementLabWalkMode = true;
            Print("[MovementLab Linked Wheel] Jog79% -> walk~85%");
        }
        else if (!m_MovementLabWalkMode && !m_MovementLabScrollSprint)
        {
            if (m_MovementLabJogLevel >= 4)
            {
                m_MovementLabJogLevel = 3;
                m_MovementLabSprintLevel = 2;
                m_MovementLabScrollSprint = true;
                Print("[MovementLab Linked Wheel] Jog101% -> sprint100%");
            }
        }
    }

    protected void MovementLabUpdateStandingWalkWheel(float dt, int command)
    {
        if (m_MovementLabWalkLevelVar < 0 && GetAnimInterface())
            m_MovementLabWalkLevelVar = GetAnimInterface().BindVariableFloat("MovementLabWalkLevel");
        if (!m_MovementLabWalkBindReported)
        {
            Print("[MovementLab Walk Wheel v3] Graph variable binding=" + m_MovementLabWalkLevelVar);
            m_MovementLabWalkBindReported = true;
        }
        HumanMovementState walkWheelState = new HumanMovementState();
        GetMovementState(walkWheelState);
        bool walkWheelCrouching = walkWheelState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH;
        bool walkWheelErect = walkWheelState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
        bool walkWheelReset = m_MovementLabWalkWheelWasCrouching && walkWheelErect;
        if (walkWheelReset)
        {
            m_MovementLabWalkLevel = 1;
            Print("[MovementLab Walk Wheel] Crouch exit: walking level1 ~85%");
        }
        m_MovementLabWalkWheelWasCrouching = walkWheelCrouching;
        bool walkWheelAllowed = MovementLabCanUseModes(dt, command);
        // One wheel reader owns both standing modes, preventing a boundary
        // crossing from processing the same notch again in the destination mode.
        if (walkWheelAllowed && !walkWheelReset)
        {
            if (GetUApi().GetInputByID(UATurbo).LocalValue() <= 0.05)
            {
                int walkWheelChange = 0;
                if (GetUApi().GetInputByID(UAPrevAction).LocalPress())
                    walkWheelChange = 1;
                else if (GetUApi().GetInputByID(UANextAction).LocalPress())
                    walkWheelChange = -1;
                if (walkWheelChange != 0)
                {
                    if (m_MovementLabScrollSprint)
                        m_MovementLabSprintLevel = Math.Clamp(m_MovementLabSprintLevel + walkWheelChange, 1, 3);
                    else if (m_MovementLabWalkMode)
                        m_MovementLabWalkLevel = Math.Clamp(m_MovementLabWalkLevel + walkWheelChange, 1, 4);
                    else
                        m_MovementLabJogLevel = Math.Clamp(m_MovementLabJogLevel + walkWheelChange, 1, 4);
                    Print("[MovementLab Linked Wheel] Walk=" + m_MovementLabWalkLevel + ", jog=" + m_MovementLabJogLevel);
                }
            }
            MovementLabApplyStandingWheelBoundaries();
        }
        if (m_MovementLabWalkLevelVar >= 0)
        {
            // Selector2 is native; erect levels use reversed encoding3/2/1.
            float walkWheelSelected = 2;
            if (MovementLabStartGate.Enabled && !GetGame().IsMultiplayer())
            {
                walkWheelSelected = 4 - m_MovementLabWalkLevel;
                if (m_MovementLabJogLevel == 2)
                    walkWheelSelected = walkWheelSelected + 3;
            }
            AnimSetFloat(m_MovementLabWalkLevelVar, walkWheelSelected);
            if (m_MovementLabWalkReportedLevel != m_MovementLabWalkLevel)
            {
                Print("[MovementLab Walk Wheel v3] Level=" + m_MovementLabWalkLevel + ", graph=" + walkWheelSelected);
                m_MovementLabWalkReportedLevel = m_MovementLabWalkLevel;
            }
        }
    }

    protected void MovementLabUpdateCrouchWheel(float dt, int command)
    {
        if (m_MovementLabCrouchLevelVar < 0 && GetAnimInterface())
            m_MovementLabCrouchLevelVar = GetAnimInterface().BindVariableFloat("MovementLabCrouchLevel");
        if (!m_MovementLabCrouchBindReported)
        {
            Print("[MovementLab Wheel] Graph variable binding=" + m_MovementLabCrouchLevelVar);
            m_MovementLabCrouchBindReported = true;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        bool wheelCrouching = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH;
        if (!wheelCrouching)
        {
            // Do not mistake the first upright sample of fast crouch for
            // full standing sprint. Transition commands retain prior evidence.
            if (m_MovementLabWheelWasCrouching || state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT)
                m_MovementLabWheelStandingSprint = false;
            else if (command == DayZPlayerConstants.COMMANDID_MOVE && GetCommand_Move())
                m_MovementLabWheelStandingSprint = GetCommand_Move().GetCurrentMovementSpeed() >= 2.90;
        }
        else if (!m_MovementLabWheelWasCrouching)
        {
            m_MovementLabCrouchLevel = 3;
            if (m_MovementLabWheelStandingSprint)
                m_MovementLabCrouchLevel = 6;
            Print("[MovementLab Crouch Entry] Default level=" + m_MovementLabCrouchLevel);
            MessageStatus("Crouch speed level " + m_MovementLabCrouchLevel + "/6");
        }
        m_MovementLabWheelWasCrouching = wheelCrouching;
        if (MovementLabCrouchAllowed(dt, command) && state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH)
        {
            int change = 0;
            if (GetUApi().GetInputByID(UAPrevAction).LocalPress())
                change = 1;
            else if (GetUApi().GetInputByID(UANextAction).LocalPress())
                change = -1;
            if (change != 0)
            {
                m_MovementLabCrouchLevel = Math.Clamp(m_MovementLabCrouchLevel + change, 1, 6);
                Print("[MovementLab Wheel] Crouch level=" + m_MovementLabCrouchLevel);
                MessageStatus("Crouch speed level " + m_MovementLabCrouchLevel + "/6");
            }
        }
        if (m_MovementLabCrouchLevelVar >= 0)
        {
            float selected = m_MovementLabCrouchLevel;
            if (GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05)
                selected = 6;
            AnimSetFloat(m_MovementLabCrouchLevelVar, selected);
        }
    }

    void MovementLabCancelStart()
    {
        if (m_MovementLabStartOwnsSpeed && GetInputController())
            GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
        m_MovementLabStartOwnsSpeed = false;
        m_MovementLabIdleArmed = false;
        m_MovementLabStarting = false;
        m_MovementLabStartTime = 0;
    }

    void MovementLabSetBrakingActive(bool active)
    {
        if (active)
        {
            MovementLabCancelStart();
            m_MovementLabModeDecreasePending = false;
        }
        m_MovementLabBrakeActive = active;
    }

    // Called before both command and mission movement processing. The
    // standing v4 path is untouched unless a crouch exit must select its mode.
    bool MovementLabUpdateCrouchRules(float dt, int command)
    {
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        bool crouching = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH;
        if (!crouching && !m_MovementLabWasCrouching)
            return false;
        if (!MovementLabCrouchAllowed(dt, command))
        {
            m_MovementLabWasCrouching = false;
            m_MovementLabFastCrouch = false;
            m_MovementLabCrouchShiftConsumed = false;
            return false;
        }
        bool moving = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            moving = true;
        bool shift = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
        if (crouching && m_MovementLabCrouchLevel == 6)
            shift = true;
        if (crouching)
        {
            m_MovementLabScrollSprint = false;
            m_MovementLabSprintLevel = 2;
            MovementLabCancelStart();
            m_MovementLabModeDecreasePending = false;
            m_MovementLabWasInput = false;
            m_MovementLabWasCrouching = true;
            // Current crouch state, not an "ever used Shift" latch.
            m_MovementLabFastCrouch = shift && moving;
            m_MovementLabCrouchShiftConsumed = false;
            m_MovementLabLastWantedGait = MovementLabWantedGait();
            if (moving && !shift)
            {
                // Slow crouch uses the saved wheel level. Held Shift is
                // explicitly fast below, independent of native input filtering.
                m_MovementLabStartOwnsSpeed = true;
                GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 1.0);
            }
            if (moving && shift)
            {
                m_MovementLabStartOwnsSpeed = true;
                GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 3.0);
            }
            return true;
        }
        if (state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT)
        {
            if (m_MovementLabFastCrouch)
            {
                m_MovementLabWalkMode = false;
                // The SAME Shift hold used for crouch must not become an
                // upright sprint. Release it before requesting sprint again.
                m_MovementLabCrouchShiftConsumed = shift;
            }
            // Slow crouch preserves m_MovementLabWalkMode (rule 4).
            m_MovementLabLastWantedGait = MovementLabWantedGait();
            m_MovementLabModeDecreasePending = false;
            m_MovementLabWasInput = moving;
        }
        m_MovementLabWasCrouching = false;
        m_MovementLabFastCrouch = false;
        return false;
    }

    protected bool MovementLabCrouchAllowed(float dt, int command)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer())
            return false;
        if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
            return false;
        if (IsRaised() || IsEmotePlaying())
            return false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
            return false;
        if (!GetInputController() || dt > 0.25)
            return false;
        if (GetGame().GetUIManager().GetMenu())
            return false;
        if (GetGame().GetMission())
        {
            if (GetGame().GetMission().IsPaused())
                return false;
        }
        return true;
    }

    bool MovementLabIsStarting()
    {
        return m_MovementLabStarting;
    }

    float MovementLabGetStartSpeed()
    {
        return m_MovementLabStartSpeed;
    }

    bool MovementLabIsScrollSprinting()
    {
        return m_MovementLabScrollSprint;
    }

    float MovementLabBaseGait()
    {
        if (m_MovementLabWalkMode)
            return 1.0;
        return 2.0;
    }

    float MovementLabWantedGait()
    {
        bool shift = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
        if (!shift)
            m_MovementLabCrouchShiftConsumed = false;
        if (shift && !m_MovementLabCrouchShiftConsumed)
            return 3.0;
        if (m_MovementLabScrollSprint)
            return 3.0;
        return MovementLabBaseGait();
    }

    protected bool MovementLabCanUseModes(float dt, int command)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer())
            return false;
        if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
            return false;
        if (IsRaised() || IsEmotePlaying())
            return false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
            return false;
        if (!GetInputController() || dt > 0.25)
            return false;
        if (GetGame().GetUIManager().GetMenu())
            return false;
        if (GetGame().GetMission())
        {
            if (GetGame().GetMission().IsPaused())
                return false;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        return state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
    }

    protected void MovementLabCommandStart(float dt, int command)
    {
        bool ctrl = GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05;
        bool press = ctrl && !m_MovementLabCtrlDown;
        m_MovementLabCtrlDown = ctrl;
        if (MovementLabUpdateCrouchRules(dt, command))
            return;
        if (!MovementLabCanUseModes(dt, command))
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = false;
            m_MovementLabModeDecreasePending = false;
            m_MovementLabLastWantedGait = MovementLabWantedGait();
            return;
        }
        // Preserve the pre-sprint mode: Ctrl during held Shift is ignored.
        if (press && (GetUApi().GetInputByID(UATurbo).LocalValue() <= 0.05 || m_MovementLabCrouchShiftConsumed))
        {
            m_MovementLabScrollSprint = false;
            m_MovementLabSprintLevel = 2;
            m_MovementLabWalkMode = !m_MovementLabWalkMode;
            Print("[MovementLab Ctrl Modes v4] Base gait=" + MovementLabBaseGait());
        }
        float wanted = MovementLabWantedGait();
        float previousWanted = m_MovementLabLastWantedGait;
        m_MovementLabLastWantedGait = wanted;
        if (wanted < previousWanted)
            m_MovementLabModeDecreasePending = true;
        bool movingInput = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05;
        HumanInputController input = GetInputController();
        // Retain v11's single braking owner in the mission.
        if (m_MovementLabBrakeActive)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = movingInput;
            return;
        }
        float achieved = GetCommand_Move().GetCurrentMovementSpeed();
        if (!movingInput)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = false;
            m_MovementLabModeDecreasePending = false;
            if (achieved <= 0.1)
            {
                m_MovementLabIdleArmed = true;
                m_MovementLabStartOwnsSpeed = true;
                input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 0);
            }
            return;
        }
        if (m_MovementLabModeDecreasePending && wanted < achieved - 0.05)
        {
            // Hold current gait until the mission starts its timed slowdown.
            // Never emit one walking frame ahead of the brake controller.
            MovementLabCancelStart();
            m_MovementLabWasInput = true;
            m_MovementLabStartOwnsSpeed = true;
            input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, achieved);
            return;
        }
        m_MovementLabModeDecreasePending = false;
        if (wanted == 1.0)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = true;
            m_MovementLabStartOwnsSpeed = true;
            input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 1.0);
            return;
        }
        if (!m_MovementLabStarting)
        {
            if (m_MovementLabIdleArmed || (!m_MovementLabWasInput && achieved <= 0.1))
            {
                m_MovementLabStarting = true;
                m_MovementLabIdleArmed = false;
                m_MovementLabStartTime = 0;
            }
            else if (previousWanted == 1.0 && wanted > 1.0 && achieved < 1.75)
            {
                // Only a real walk-to-jog/sprint MODE change starts this blend.
                // Native turn/backward gait dips must not restart it each cycle.
                m_MovementLabStarting = true;
                m_MovementLabStartTime = 0.10;
            }
        }
        m_MovementLabWasInput = true;
        if (m_MovementLabStarting && m_MovementLabStartTime < 0.35)
        {
            float blend = Math.Clamp((m_MovementLabStartTime - 0.10) / 0.18, 0, 1);
            blend = blend * blend * (3.0 - 2.0 * blend);
            m_MovementLabStartSpeed = 1.0 + blend;
            m_MovementLabStartOwnsSpeed = true;
            input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, m_MovementLabStartSpeed);
            m_MovementLabStartTime = m_MovementLabStartTime + Math.Max(dt, 0);
            return;
        }
        if (m_MovementLabStarting)
            MovementLabCancelStart();
        // Persistent mode ownership replaces Ctrl-hold with Ctrl-toggle.
        m_MovementLabStartOwnsSpeed = true;
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, wanted);
    }

    protected void MovementLabUpdateStrafeSlow(float dt, int command)
    {
        if (!MovementLabCanUseModes(dt, command) || MovementLabWantedGait() < 2.0)
        {
            m_MovementLabSlowLastSide = 0;
            m_MovementLabStrafeSlow = false;
            m_MovementLabSlowHeld = 0;
            m_MovementLabSlowGap = 0;
            return;
        }
        bool left = GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05;
        bool right = GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05;
        bool longitudinal = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05;
        float step = Math.Max(dt, 0);
        int side = 0;
        if (left && !right)
            side = -1;
        else if (right && !left)
            side = 1;
        if (longitudinal)
        {
            m_MovementLabStrafeSlow = false;
            m_MovementLabSlowLastSide = 0;
            return;
        }
        if (side == 0)
        {
            m_MovementLabSlowHeld = 0;
            m_MovementLabSlowGap = m_MovementLabSlowGap + step;
            if (!left && !right)
                m_MovementLabStrafeSlow = false;
            if (m_MovementLabSlowGap > 0.18)
                m_MovementLabSlowLastSide = 0;
            if (left && right && m_MovementLabStrafeSlow && !m_MovementLabBrakeActive)
                GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 0.15);
            return;
        }
        bool reversed = m_MovementLabSlowLastSide != 0 && side != m_MovementLabSlowLastSide;
        if (reversed)
        {
            m_MovementLabStrafeSlow = true;
            m_MovementLabSlowHeld = 0;
        }
        else
            m_MovementLabSlowHeld = m_MovementLabSlowHeld + step;
        m_MovementLabSlowLastSide = side;
        m_MovementLabSlowGap = 0;
        if (!m_MovementLabStrafeSlow || m_MovementLabBrakeActive)
            return;
        MovementLabApplyStrafeSlow();
    }

    void MovementLabApplyStrafeSlow()
    {
        if (!m_MovementLabStrafeSlow || m_MovementLabBrakeActive)
            return;
        // Near-stop movement, never a frozen pose or angle override.
        // A fresh reversal resets ONLY stable-hold age, keeping speed low.
        float blend = Math.Clamp((m_MovementLabSlowHeld - 0.30) / 0.08, 0, 1);
        blend = blend * blend * (3.0 - 2.0 * blend);
        m_MovementLabStartOwnsSpeed = true;
        float gait = 0.15 + (MovementLabWantedGait() - 0.15) * blend;
        GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, gait);
        if (blend >= 1)
            m_MovementLabStrafeSlow = false;
    }

    protected void MovementLabRecordSprintTravel(float dt)
    {
        bool groundEligible = MovementLabCanUseModes(dt, GetCurrentCommandID());
        if (!m_MovementLabScrollSprint || m_MovementLabBrakeActive)
            groundEligible = false;
        if (dt <= 0 || dt > 0.1)
            groundEligible = false;
        if (GetCommand_Move())
        {
            if (GetCommand_Move().GetCurrentMovementSpeed() < 2.90)
                groundEligible = false;
        }
        if (!groundEligible)
        {
            m_MovementLabGroundSampleKnown = false;
            m_MovementLabGroundTime = 0;
            m_MovementLabGroundDistance = 0;
            return;
        }
        vector groundPosition = GetPosition();
        if (!m_MovementLabGroundSampleKnown || m_MovementLabGroundSampleLevel != m_MovementLabSprintLevel)
        {
            m_MovementLabGroundX = groundPosition[0];
            m_MovementLabGroundZ = groundPosition[2];
            m_MovementLabGroundSampleLevel = m_MovementLabSprintLevel;
            m_MovementLabGroundSampleKnown = true;
            m_MovementLabGroundTime = 0;
            m_MovementLabGroundDistance = 0;
            return;
        }
        float groundDx = groundPosition[0] - m_MovementLabGroundX;
        float groundDz = groundPosition[2] - m_MovementLabGroundZ;
        float groundDistance = Math.Sqrt(groundDx * groundDx + groundDz * groundDz);
        m_MovementLabGroundX = groundPosition[0];
        m_MovementLabGroundZ = groundPosition[2];
        m_MovementLabGroundTime = m_MovementLabGroundTime + dt;
        m_MovementLabGroundDistance = m_MovementLabGroundDistance + groundDistance;
        if (m_MovementLabGroundTime >= 0.5)
        {
            float groundRate = m_MovementLabGroundDistance / m_MovementLabGroundTime;
            Print("[MovementLab Ground Speed] Sprint level=" + m_MovementLabSprintLevel + ", measured m/s=" + groundRate);
            m_MovementLabGroundTime = 0;
            m_MovementLabGroundDistance = 0;
        }
    }

    // Offline experiment: adjust physical horizontal displacement, not gait index.
    override void OnPhysMove(float dt, vector transform[4])
    {
        super.OnPhysMove(dt, transform);
        MovementLabRecordSprintTravel(dt);
        if (!MovementLabCanUseModes(dt, GetCurrentCommandID()))
            return;
        if (!m_MovementLabScrollSprint || m_MovementLabSprintLevel != 3)
            return;
        if (dt <= 0 || dt > 0.1)
            return;
        if (GetParent() || PhysicsIsFalling(false))
            return;
        if (GetCommand_Move().GetCurrentMovementSpeed() < 2.90)
            return;
        if (m_MovementLabBrakeActive)
            return;
        bool travelMoving = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05;
        if (GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05)
            travelMoving = true;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            travelMoving = true;
        if (!travelMoving)
            return;
        vector travelOrigin = GetPosition();
        vector travelDelta = transform[3] - travelOrigin;
        travelDelta[1] = 0;
        float travelDistance = travelDelta.Length();
        if (travelDistance <= 0.00001 || travelDistance > 2)
            return;
        IEntity travelHit;
        vector travelHitPosition;
        vector travelHitNormal;
        float travelFree = CollisionMoveTest(travelDelta * 1.20, vector.Zero, 1.0, null, travelHit, travelHitPosition, travelHitNormal);
        travelFree = Math.Clamp(travelFree, 0, 1);
        // Retain already validated native displacement if extra travel is blocked.
        float travelScale = Math.Max(1.0, 1.20 * travelFree);
        vector travelFinal = transform[3];
        travelFinal[0] = travelOrigin[0] + travelDelta[0] * travelScale;
        travelFinal[2] = travelOrigin[2] + travelDelta[2] * travelScale;
        transform[3] = travelFinal;
        m_MovementLabTravelProbeTime = m_MovementLabTravelProbeTime + dt;
        m_MovementLabTravelProbeBase = m_MovementLabTravelProbeBase + travelDistance;
        m_MovementLabTravelProbeApplied = m_MovementLabTravelProbeApplied + travelDistance * travelScale;
        if (m_MovementLabTravelProbeTime >= 0.5)
        {
            float travelBaseRate = m_MovementLabTravelProbeBase / m_MovementLabTravelProbeTime;
            float travelAppliedRate = m_MovementLabTravelProbeApplied / m_MovementLabTravelProbeTime;
            Print("[MovementLab Travel120] Native proposal m/s=" + travelBaseRate + ", adjusted proposal m/s=" + travelAppliedRate);
            m_MovementLabTravelProbeTime = 0;
            m_MovementLabTravelProbeBase = 0;
            m_MovementLabTravelProbeApplied = 0;
        }
    }

    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        MovementLabUpdateStandingWalkWheel(pDt, pCurrentCommandID);
        MovementLabUpdateCrouchWheel(pDt, pCurrentCommandID);
        MovementLabCommandStart(pDt, pCurrentCommandID);
        MovementLabUpdateStrafeSlow(pDt, pCurrentCommandID);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
