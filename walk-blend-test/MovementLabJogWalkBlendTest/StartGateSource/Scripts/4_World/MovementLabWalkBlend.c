// Only the matching standalone offline mission enables this experiment.
class MovementLabStartGate
{
    static bool Enabled;
}

modded class PlayerBase
{
    protected bool m_MovementLabBlendOwnsSpeed;
    protected bool m_MovementLabWasWalk;
    protected float m_MovementLabBlendTime;
    protected float m_MovementLabBlendStart;
    protected int m_MovementLabBlendKeys;

    void MovementLabCancelWalkBlend()
    {
        if (m_MovementLabBlendOwnsSpeed && GetInputController())
            GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
        m_MovementLabBlendOwnsSpeed = false;
        m_MovementLabBlendTime = 0;
    }

    protected bool MovementLabCanBlend(float dt, int command)
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
        if (GetGame().GetUIManager().GetMenu() || GetGame().GetMission().IsPaused())
            return false;
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        return state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
    }

    protected void MovementLabUpdateWalkBlend(float dt, int command)
    {
        bool walk = GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05;
        if (GetUApi().GetInputByID(UAWalkRunForced).LocalValue() > 0.05)
            walk = true;
        bool walkEdge = walk && !m_MovementLabWasWalk;
        m_MovementLabWasWalk = walk;
        if (!MovementLabCanBlend(dt, command))
        {
            MovementLabCancelWalkBlend();
            return;
        }
        int keys = 0;
        if (GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05)
            keys = keys + 1;
        if (GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05)
            keys = keys + 2;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05)
            keys = keys + 4;
        if (GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            keys = keys + 8;
        bool turbo = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
        if (!walk || turbo || keys == 0)
        {
            MovementLabCancelWalkBlend();
            return;
        }
        if (m_MovementLabBlendOwnsSpeed && keys != m_MovementLabBlendKeys)
        {
            MovementLabCancelWalkBlend();
            return;
        }
        if (walkEdge && !m_MovementLabBlendOwnsSpeed)
        {
            float achieved = GetCommand_Move().GetCurrentMovementSpeed();
            // Only achieved jogging. No sprint braking or walk startup added.
            if (achieved > 1.1 && achieved <= 2.05)
            {
                m_MovementLabBlendStart = achieved;
                m_MovementLabBlendTime = 0;
                m_MovementLabBlendKeys = keys;
                m_MovementLabBlendOwnsSpeed = true;
            }
        }
        if (!m_MovementLabBlendOwnsSpeed)
            return;
        m_MovementLabBlendTime = m_MovementLabBlendTime + Math.Max(dt, 0);
        float fraction = Math.Clamp(m_MovementLabBlendTime / 0.45, 0, 1);
        if (fraction >= 1)
        {
            MovementLabCancelWalkBlend();
            return;
        }
        // Gait units, not m/s. Continuous with zero slope at both ends:
        // the early walk blend retains momentum, easing into native walk.
        float eased = fraction * fraction * (3.0 - 2.0 * fraction);
        float speed = m_MovementLabBlendStart + (1.0 - m_MovementLabBlendStart) * eased;
        GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ONE_FRAME, speed);
    }

    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        MovementLabUpdateWalkBlend(pDt, pCurrentCommandID);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
