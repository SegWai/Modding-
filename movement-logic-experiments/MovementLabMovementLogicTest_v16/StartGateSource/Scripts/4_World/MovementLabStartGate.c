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

    protected void MovementLabCommandStart(float dt, int command)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious() || IsRaised() || IsEmotePlaying() || command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move() || GetGame().GetUIManager().GetMenu() || dt > 0.25)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = false;
            return;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        if (state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = false;
            return;
        }
        bool movingInput = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05;
        HumanInputController input = GetInputController();
        if (!input)
        {
            MovementLabCancelStart();
            return;
        }
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
            Print("[MovementLab v10] Walking start applied before the base command handler.");
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
        // Finish the committed handoff before accepting another reversal.
        if (MovementLabResumeMovingReversal(pDt, pCurrentCommandID))
        {
            super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
            return;
        }
        if (MovementLabTryMovingReversal(pDt, pCurrentCommandID, pCurrentCommandFinished))
            return;
        MovementLabCommandStart(pDt, pCurrentCommandID);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
    protected ref MovementLabNativeBraceTable m_MovementLabNativeBraceTable;
    protected bool m_MovementLabReversalResume;
    protected bool m_MovementLabReversalOwnsHandoff;
    protected float m_MovementLabReversalHandoffTime;
    protected float m_MovementLabReversalNoInputTime;
    protected float m_MovementLabReversalForward;
    protected float m_MovementLabReversalSide;
    protected float m_MovementLabReversalAngle;

    void MovementLabReversalEnded(float forward, float side, float angle, bool aborted)
    {
        m_MovementLabReversalResume = !aborted;
        m_MovementLabReversalHandoffTime = 0;
        m_MovementLabReversalNoInputTime = 0;
        // Track the completed direction, not whichever key was last spammed.
        m_MovementLabReversalForward = forward;
        m_MovementLabReversalSide = side;
        m_MovementLabReversalAngle = angle;
    }

    protected void MovementLabCancelReversalHandoff()
    {
        if (m_MovementLabReversalOwnsHandoff && GetInputController())
        {
            GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
            GetInputController().OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
        }
        m_MovementLabReversalOwnsHandoff = false;
        m_MovementLabReversalResume = false;
        m_MovementLabReversalHandoffTime = 0;
    }

    protected bool MovementLabResumeMovingReversal(float dt, int command)
    {
        if (!m_MovementLabReversalResume)
            return false;
        if (!MovementLabStartGate.Enabled || !MovementLabReversalSettings.Enabled || !IsAlive() || IsUnconscious() || IsRaised() || IsEmotePlaying() || GetEntityInHands() || GetGame().GetUIManager().GetMenu() || (GetGame().GetMission() && GetGame().GetMission().IsPaused()) || dt > 0.25)
        {
            MovementLabCancelReversalHandoff();
            return false;
        }
        // Finished script commands go through the base handler to start MOVE.
        if (command == DayZPlayerConstants.COMMANDID_SCRIPT)
            return false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
        {
            MovementLabCancelReversalHandoff();
            return false;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        HumanInputController input = GetInputController();
        float forward = GetUApi().GetInputByID(UAMoveForward).LocalValue() - GetUApi().GetInputByID(UAMoveBack).LocalValue();
        float side = GetUApi().GetInputByID(UAMoveRight).LocalValue() - GetUApi().GetInputByID(UAMoveLeft).LocalValue();
        bool movingInput = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05;
        if (movingInput)
            m_MovementLabReversalNoInputTime = 0;
        else
            m_MovementLabReversalNoInputTime = m_MovementLabReversalNoInputTime + Math.Max(dt, 0);
        if (!input || m_MovementLabReversalNoInputTime >= 0.10 || state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT || input.IsWalkToggled() || GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05 || GetUApi().GetInputByID(UAWalkRunForced).LocalValue() > 0.05)
        {
            MovementLabCancelReversalHandoff();
            return false;
        }
        MovementLabCancelStart();
        m_MovementLabWasInput = true;
        if (m_MovementLabReversalHandoffTime >= 0.14)
        {
            MovementLabCancelReversalHandoff();
            return false;
        }
        // Keep the completed direction fixed through the native outgoing blend.
        // New presses are read after this handoff, never injected mid-blend.
        // Otherwise its initial angle/gait can briefly revert to forward/idle.
        float angle = m_MovementLabReversalAngle;
        input.OverrideMovementAngle(HumanInputControllerOverrideType.ENABLED, angle);
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 2.0);
        m_MovementLabReversalOwnsHandoff = true;
        m_MovementLabReversalHandoffTime = m_MovementLabReversalHandoffTime + Math.Max(dt, 0);
        return true;
    }

    // The normal base lifecycle still processes death, falling and finished
    // commands. It must not replace our active script command with native move.
    override bool ModCommandHandlerInside(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        if (super.ModCommandHandlerInside(pDt, pCurrentCommandID, pCurrentCommandFinished))
            return true;
        return pCurrentCommandID == DayZPlayerConstants.COMMANDID_SCRIPT && MovementLabMovingReversalCommand.Cast(GetCommand_Script()) != null;
    }

    bool MovementLabTryMovingReversal(float dt, int command, bool finished)
    {
        if (command == DayZPlayerConstants.COMMANDID_SCRIPT && MovementLabMovingReversalCommand.Cast(GetCommand_Script()))
            return false;
        if (!MovementLabStartGate.Enabled || !MovementLabReversalSettings.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious() || IsRaised() || IsEmotePlaying() || GetEntityInHands() || command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move() || finished || GetGame().GetUIManager().GetMenu() || (GetGame().GetMission() && GetGame().GetMission().IsPaused()) || dt > 0.25)
        {
            m_MovementLabReversalForward = 0;
            m_MovementLabReversalSide = 0;
            return false;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        HumanInputController input = GetInputController();
        if (!input || state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT || input.IsWalkToggled() || GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05 || GetUApi().GetInputByID(UAWalkRunForced).LocalValue() > 0.05)
        {
            m_MovementLabReversalForward = 0;
            m_MovementLabReversalSide = 0;
            return false;
        }
        float forward = GetUApi().GetInputByID(UAMoveForward).LocalValue() - GetUApi().GetInputByID(UAMoveBack).LocalValue();
        float side = GetUApi().GetInputByID(UAMoveRight).LocalValue() - GetUApi().GetInputByID(UAMoveLeft).LocalValue();
        // Opposite key presses win detection even if the old key is still held.
        if (GetUApi().GetInputByID(UAMoveRight).LocalPress())
            side = 1;
        else if (GetUApi().GetInputByID(UAMoveLeft).LocalPress())
            side = -1;
        if (GetUApi().GetInputByID(UAMoveForward).LocalPress())
            forward = 1;
        else if (GetUApi().GetInputByID(UAMoveBack).LocalPress())
            forward = -1;
        float gait = GetCommand_Move().GetCurrentMovementSpeed();
        float dot = forward * m_MovementLabReversalForward + side * m_MovementLabReversalSide;
        float lengths = Math.Sqrt((forward * forward + side * side) * (m_MovementLabReversalForward * m_MovementLabReversalForward + m_MovementLabReversalSide * m_MovementLabReversalSide));
        if (!m_MovementLabReversalResume && gait >= 1.75 && lengths > 0.1 && dot / lengths < -0.65)
        {
            if (!m_MovementLabNativeBraceTable)
                m_MovementLabNativeBraceTable = new MovementLabNativeBraceTable(this);
            if (m_MovementLabNativeBraceTable.Valid())
            {
                MovementLabCancelStart();
                // A scripted command owns translation; clear any old brake input.
                input.OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
                input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
                Print("[MovementLab v16] Reversal triggered oldAngle=" + m_MovementLabReversalAngle + ", forward=" + forward + ", side=" + side + ", gait=" + gait);
                StartCommand_Script(new MovementLabMovingReversalCommand(this, m_MovementLabNativeBraceTable, m_MovementLabReversalAngle, forward, side));
                return true;
            }
            Print("[MovementLab v16] Native pose binding unavailable; v11 movement retained.");
        }
        if (Math.AbsFloat(forward) > 0.05 || Math.AbsFloat(side) > 0.05)
        {
            m_MovementLabReversalForward = forward;
            m_MovementLabReversalSide = side;
            m_MovementLabReversalAngle = GetCommand_Move().GetCurrentMovementAngle();
            // Cardinal intent disambiguates native blends near zero degrees.
            if (Math.AbsFloat(forward) <= 0.05)
            {
                if (side < 0)
                    m_MovementLabReversalAngle = -90;
                else
                    m_MovementLabReversalAngle = 90;
            }
            else if (Math.AbsFloat(side) <= 0.05)
            {
                if (forward < 0)
                    m_MovementLabReversalAngle = 180;
                else
                    m_MovementLabReversalAngle = 0;
            }
        }
        else if (gait <= 0.1)
        {
            m_MovementLabReversalForward = 0;
            m_MovementLabReversalSide = 0;
        }
        return false;
    }
}
