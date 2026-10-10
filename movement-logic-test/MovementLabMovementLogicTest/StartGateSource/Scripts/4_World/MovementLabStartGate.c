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
        MovementLabCommandStart(pDt, pCurrentCommandID);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
