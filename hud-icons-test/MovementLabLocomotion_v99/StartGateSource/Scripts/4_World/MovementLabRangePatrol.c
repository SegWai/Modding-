// Offline male range target only: native lateral jogging between +/-1m points.
modded class PlayerBase
{
    protected bool m_MovementLabRangePatrolEnabled;
    protected bool m_MovementLabRangePatrolOwnsInput;
    protected vector m_MovementLabRangePatrolCenter;
    protected vector m_MovementLabRangePatrolRight;
    protected float m_MovementLabRangePatrolSign = -1.0;

    void MovementLabStartRangePatrol()
    {
        m_MovementLabRangePatrolCenter = GetPosition();
        vector facing = GetDirection();
        facing[1] = 0;
        if (facing.Length() < 0.001)
            facing = "0 0 1";
        facing.Normalize();
        m_MovementLabRangePatrolRight = Vector(facing[2], 0, -facing[0]);
        m_MovementLabRangePatrolSign = -1.0;
        m_MovementLabRangePatrolEnabled = true;
    }

    void MovementLabUpdateRangePatrol()
    {
        HumanInputController input = GetInputController();
        if (!input)
            return;
        if (!m_MovementLabRangePatrolEnabled || !MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() == this || !IsAlive() || IsUnconscious() || !GetCommand_Move())
        {
            if (m_MovementLabRangePatrolOwnsInput)
            {
                input.OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
                input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
                m_MovementLabRangePatrolOwnsInput = false;
            }
            return;
        }
        vector offset = GetPosition() - m_MovementLabRangePatrolCenter;
        float lateral = offset[0] * m_MovementLabRangePatrolRight[0] + offset[2] * m_MovementLabRangePatrolRight[2];
        if (m_MovementLabRangePatrolSign < 0 && lateral <= -1.0)
            m_MovementLabRangePatrolSign = 1.0;
        else if (m_MovementLabRangePatrolSign > 0 && lateral >= 1.0)
            m_MovementLabRangePatrolSign = -1.0;
        // Gait 2 is native jogging; angle is in degrees, relative to facing.
        // Native filters blend each reversal; no position teleports are used.
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 2.0);
        input.OverrideMovementAngle(HumanInputControllerOverrideType.ENABLED, 90.0 * m_MovementLabRangePatrolSign);
        m_MovementLabRangePatrolOwnsInput = true;
    }
}
