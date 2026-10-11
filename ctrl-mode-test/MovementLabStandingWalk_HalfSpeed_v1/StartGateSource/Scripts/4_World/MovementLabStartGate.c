// Loaded before the loose mission. Only its offline mission enables the gate.
class MovementLabStartGate
{
    static bool Enabled;
    static bool HalfWalk;
}

modded class PlayerBase
{
    protected int m_MovementLabHalfWalkVar = -1;
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

    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        if (m_MovementLabHalfWalkVar < 0 && GetAnimInterface())
            m_MovementLabHalfWalkVar = GetAnimInterface().BindVariableFloat("MovementLabHalfWalk");
        if (m_MovementLabHalfWalkVar >= 0)
        {
            float halfWalkSelection = 0;
            if (MovementLabStartGate.Enabled && MovementLabStartGate.HalfWalk)
                halfWalkSelection = 1;
            AnimSetFloat(m_MovementLabHalfWalkVar, halfWalkSelection);
        }
        MovementLabUpdateCrouchWheel(pDt, pCurrentCommandID);
        MovementLabCommandStart(pDt, pCurrentCommandID);
        MovementLabUpdateStrafeSlow(pDt, pCurrentCommandID);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
