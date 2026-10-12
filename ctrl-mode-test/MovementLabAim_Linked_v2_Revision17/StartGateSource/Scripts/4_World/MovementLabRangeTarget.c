modded class PlayerBase
{
    protected bool m_MovementLabRangeTarget;

    void MovementLabSetRangeTarget()
    {
        m_MovementLabRangeTarget = true;
        SetAllowDamage(true);
    }

    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        if (m_MovementLabRangeTarget && IsAlive() && !IsUnconscious() && GetInputController())
        {
            GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 0);
            GetInputController().OverrideMovementAngle(HumanInputControllerOverrideType.ENABLED, 0);
        }
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
