// Loaded before the loose mission. Only its offline mission enables the gate.
class MovementLabStartGate
{
    static bool Enabled;
}

modded class PlayerBase
{
    protected bool m_MovementLabStartOwnsSpeed;
    protected bool m_MovementLabIdleArmed;
    protected bool m_MovementLabStarting;
    protected bool m_MovementLabWasInput;
    protected bool m_MovementLabBrakeActive;
    protected float m_MovementLabStartTime;
    protected float m_MovementLabStartSpeed;
    protected bool m_MovementLabReversing;
    protected int m_MovementLabPreviousSide;
    protected int m_MovementLabPreviousKeys;
    protected float m_MovementLabPreviousGait;
    protected float m_MovementLabPreviousAngle;
    protected float m_MovementLabReverseStart;
    protected float m_MovementLabReverseDuration;
    protected float m_MovementLabReverseAngle;
    protected bool m_MovementLabReverseLateral;
    protected float m_MovementLabReverseTime;
    protected float m_MovementLabReverseWait;
    protected float m_MovementLabReverseDwell;
    protected bool m_MovementLabReverseIdleConfirmed;

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
            MovementLabCancelStart();
        m_MovementLabBrakeActive = active;
    }

    bool MovementLabIsStarting()
    {
        return m_MovementLabStarting;
    }

    float MovementLabGetStartSpeed()
    {
        return m_MovementLabStartSpeed;
    }

    bool MovementLabIsReversing()
    {
        return m_MovementLabReversing;
    }

    void MovementLabCancelReversal()
    {
        if (m_MovementLabReversing && GetInputController())
        {
            GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
            GetInputController().OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
        }
        m_MovementLabReversing = false;
        m_MovementLabPreviousSide = 0;
        m_MovementLabPreviousGait = 0;
        m_MovementLabReverseTime = 0;
        m_MovementLabReverseWait = 0;
        m_MovementLabReverseDwell = 0;
        m_MovementLabReverseIdleConfirmed = false;
    }

    protected void MovementLabBeginReversal()
    {
        MovementLabCancelStart();
        m_MovementLabReversing = true;
        m_MovementLabReverseStart = m_MovementLabPreviousGait;
        m_MovementLabReverseAngle = m_MovementLabPreviousAngle;
        m_MovementLabReverseLateral = m_MovementLabPreviousKeys == 4 || m_MovementLabPreviousKeys == 8;
        if (m_MovementLabPreviousKeys == 4)
            m_MovementLabReverseAngle = -90.0;
        else if (m_MovementLabPreviousKeys == 8)
            m_MovementLabReverseAngle = 90.0;
        m_MovementLabReverseDuration = 0.42 * Math.Min(m_MovementLabReverseStart / 2.0, 1.0);
        if (m_MovementLabReverseStart > 2.05)
            m_MovementLabReverseDuration = 0.18 + 0.74 * Math.Clamp(m_MovementLabReverseStart - 2.0, 0, 1);
        m_MovementLabReverseTime = 0;
        m_MovementLabReverseWait = 0;
        m_MovementLabReverseDwell = 0;
        m_MovementLabReverseIdleConfirmed = false;
        Print("[MovementLab v12 experimental] Opposite-side request: brake, settle, then restart.");
    }

    protected bool MovementLabUpdateReversal(HumanInputController input, float dt)
    {
        float gait = 0;
        if (m_MovementLabReverseTime < m_MovementLabReverseDuration)
        {
            float fraction = Math.Clamp(m_MovementLabReverseTime / m_MovementLabReverseDuration, 0, 1);
            if (m_MovementLabReverseStart >= 2.5)
                gait = MovementLabStopEnvelope.Sprint(m_MovementLabReverseStart, fraction);
            else
                gait = m_MovementLabReverseStart * (1.0 - (2.0 * fraction - fraction * fraction));
            if (m_MovementLabReverseLateral)
                gait = Math.Max(1.0, gait);
            m_MovementLabReverseTime = m_MovementLabReverseTime + Math.Max(dt, 0);
        }
        else
        {
            // Confirm achieved idle, then require a brief 0.12s stationary pause.
            // A bounded wait prevents trapping control if native idle is not reached.
            m_MovementLabReverseWait = m_MovementLabReverseWait + Math.Max(dt, 0);
            if (GetCommand_Move().GetCurrentMovementSpeed() <= 0.1)
            {
                if (m_MovementLabReverseIdleConfirmed)
                    m_MovementLabReverseDwell = m_MovementLabReverseDwell + Math.Max(dt, 0);
                else
                    m_MovementLabReverseIdleConfirmed = true;
            }
            else
            {
                m_MovementLabReverseDwell = 0;
                m_MovementLabReverseIdleConfirmed = false;
            }
            if (m_MovementLabReverseDwell >= 0.12 || m_MovementLabReverseWait >= 0.60)
            {
                if (m_MovementLabReverseDwell < 0.12)
                    Print("[MovementLab v12 experimental] Idle wait timed out; returning control.");
                MovementLabCancelReversal();
                m_MovementLabIdleArmed = true;
                m_MovementLabWasInput = false;
                return false;
            }
        }
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, gait);
        input.OverrideMovementAngle(HumanInputControllerOverrideType.ENABLED, m_MovementLabReverseAngle);
        GetCommand_Move().SetRunSprintFilterModifier(0.35);
        return true;
    }

    protected void MovementLabCommandStart(float dt, int command)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious() || IsRaised() || IsEmotePlaying() || command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move() || GetGame().GetUIManager().GetMenu() || dt > 0.25)
        {
            MovementLabCancelStart();
            MovementLabCancelReversal();
            m_MovementLabWasInput = false;
            return;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        if (state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT)
        {
            MovementLabCancelStart();
            MovementLabCancelReversal();
            m_MovementLabWasInput = false;
            return;
        }
        float forward = GetUApi().GetInputByID(UAMoveForward).LocalValue();
        float back = GetUApi().GetInputByID(UAMoveBack).LocalValue();
        float left = GetUApi().GetInputByID(UAMoveLeft).LocalValue();
        float right = GetUApi().GetInputByID(UAMoveRight).LocalValue();
        bool movingInput = Math.AbsFloat(forward - back) > 0.05 || Math.AbsFloat(right - left) > 0.05;
        int movementKeys = 0;
        if (forward > 0.05) movementKeys = movementKeys + 1;
        if (back > 0.05) movementKeys = movementKeys + 2;
        if (left > 0.05) movementKeys = movementKeys + 4;
        if (right > 0.05) movementKeys = movementKeys + 8;
        int side = 0;
        if (right - left > 0.05) side = 1;
        else if (left - right > 0.05) side = -1;
        // Catch the opposite key even while the old key is briefly still held.
        bool leftPress = GetUApi().GetInputByID(UAMoveLeft).LocalPress();
        bool rightPress = GetUApi().GetInputByID(UAMoveRight).LocalPress();
        if (rightPress && !leftPress) side = 1;
        else if (leftPress && !rightPress) side = -1;
        HumanInputController input = GetInputController();
        if (!input)
        {
            MovementLabCancelStart();
            MovementLabCancelReversal();
            return;
        }
        if (m_MovementLabReversing)
        {
            if (MovementLabUpdateReversal(input, dt))
                return;
            // Resume from the latest held keys, not a stale queued direction.
            side = 0;
        }
        bool manualWalk = input.IsWalkToggled() || GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05 || GetUApi().GetInputByID(UAWalkRunForced).LocalValue() > 0.05;
        if (!manualWalk && side != 0 && m_MovementLabPreviousSide != 0 && side != m_MovementLabPreviousSide && m_MovementLabPreviousGait >= 1.75)
        {
            MovementLabBeginReversal();
            MovementLabUpdateReversal(input, dt);
            return;
        }
        float achieved = GetCommand_Move().GetCurrentMovementSpeed();
        if (m_MovementLabStarting)
            achieved = Math.Min(achieved, m_MovementLabStartSpeed);
        m_MovementLabPreviousGait = Math.Clamp(achieved, 0, 3);
        if (movingInput && side != 0)
        {
            m_MovementLabPreviousSide = side;
            m_MovementLabPreviousKeys = movementKeys;
            m_MovementLabPreviousAngle = GetCommand_Move().GetCurrentMovementAngle();
        }
        else if (achieved <= 0.1 || (movingInput && side == 0 && Math.AbsFloat(GetCommand_Move().GetCurrentMovementAngle()) <= 15.0))
            m_MovementLabPreviousSide = 0;
        // The mission owns braking. Do not replace its coast with idle speed 0.
        if (m_MovementLabBrakeActive)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = movingInput;
            return;
        }
        if (!movingInput)
        {
            if (m_MovementLabStarting)
                MovementLabCancelStart();
            MovementLabCancelReversal();
            m_MovementLabWasInput = false;
            // Prime idle BEFORE the next key press. Persistent speed 0 cannot
            // creep forward and cannot leak a jog before the command hook runs.
            if (GetCommand_Move().GetCurrentMovementSpeed() <= 0.1)
            {
                m_MovementLabIdleArmed = true;
                m_MovementLabStartOwnsSpeed = true;
                input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 0);
            }
            return;
        }
        if (input.IsWalkToggled() || GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05 || GetUApi().GetInputByID(UAWalkRunForced).LocalValue() > 0.05)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = true;
            return;
        }
        if (!m_MovementLabStarting && (m_MovementLabIdleArmed || (!m_MovementLabWasInput && GetCommand_Move().GetCurrentMovementSpeed() <= 0.1)))
        {
            m_MovementLabStarting = true;
            m_MovementLabIdleArmed = false;
            m_MovementLabStartTime = 0;
            Print("[MovementLab v12 experimental] Walking start applied before the base command handler.");
        }
        m_MovementLabWasInput = true;
        if (!m_MovementLabStarting)
            return;
        if (m_MovementLabStartTime >= 0.35)
        {
            MovementLabCancelStart();
            return;
        }
        float blend = Math.Clamp((m_MovementLabStartTime - 0.10) / 0.18, 0, 1);
        blend = blend * blend * (3.0 - 2.0 * blend);
        m_MovementLabStartSpeed = 1.0 + blend;
        m_MovementLabStartOwnsSpeed = true;
        // Persistent ownership avoids a ONE_FRAME gap between command ticks.
        // Direction stays native; Shift is handed back after walk -> jog.
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, m_MovementLabStartSpeed);
        m_MovementLabStartTime = m_MovementLabStartTime + Math.Max(dt, 0);
    }

    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        MovementLabCommandStart(pDt, pCurrentCommandID);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
