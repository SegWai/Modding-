// V16 requests the native brace once and permits continuous reversal motion.
// This controls directional pose/blending and motion, not clip playback rate.
class MovementLabReversalSettings
{
    static bool Enabled = true;
    static float RecoverySeconds = 0.62;
}

class MovementLabReversalCurve
{
    static float Ease(float value)
    {
        float t = Math.Clamp(value, 0, 1);
        return t * t * (3.0 - 2.0 * t);
    }

    static float OldWeight(float time)
    {
        if (time < 0.10)
            return 0.48 - 0.38 * Ease(time / 0.10);
        return 0.10 * (1.0 - Ease((time - 0.10) / 0.08));
    }

    static float NewWeight(float time)
    {
        if (time < 0.10)
            return 0;
        if (time < 0.18)
            return 0.10 * Ease((time - 0.10) / 0.08);
        return 0.10 + 0.90 * Ease((time - 0.18) / 0.44);
    }
}

class MovementLabNativeBraceTable
{
    int Slide;
    int Speed;
    int Direction;

    void MovementLabNativeBraceTable(Human player)
    {
        HumanAnimInterface anim = player.GetAnimInterface();
        Slide = anim.BindCommand("CMD_SlidingPose");
        Speed = anim.BindVariableFloat("MovementSpeed");
        Direction = anim.BindVariableFloat("MovementDirection");
    }

    bool Valid()
    {
        return Slide >= 0 && Speed >= 0 && Direction >= 0;
    }
}

class MovementLabMovingReversalCommand : HumanCommandScript
{
    protected PlayerBase m_Player;
    protected ref MovementLabNativeBraceTable m_Table;
    protected float m_OldAngle;
    protected float m_TargetAngle;
    protected float m_OldForward;
    protected float m_OldSide;
    protected float m_NewForward;
    protected float m_NewSide;
    protected float m_BaseSpeed;
    protected float m_Time;
    protected float m_Duration;
    protected vector m_Origin;
    protected bool m_Abort;
    protected float m_NoInputTime;

    void MovementLabMovingReversalCommand(PlayerBase player, MovementLabNativeBraceTable table, float angle, float forward, float side)
    {
        m_Player = player;
        m_Table = table;
        m_OldAngle = angle;
        m_TargetAngle = Math.Atan2(side, forward) * Math.RAD2DEG;
        m_OldForward = Math.Cos(angle * Math.DEG2RAD);
        m_OldSide = Math.Sin(angle * Math.DEG2RAD);
        float length = Math.Sqrt(forward * forward + side * side);
        m_NewForward = forward / Math.Max(length, 0.01);
        m_NewSide = side / Math.Max(length, 0.01);
        m_Duration = MovementLabReversalSettings.RecoverySeconds;
    }

    override void OnActivate()
    {
        m_Origin = m_Player.GetPosition();
        vector velocity = vector.Zero;
        m_Player.PhysicsGetVelocity(velocity);
        m_BaseSpeed = Math.Sqrt(velocity[0] * velocity[0] + velocity[2] * velocity[2]);
        // Physics velocity may be zero for native root-driven locomotion.
        if (m_BaseSpeed < 0.5)
            m_BaseSpeed = 2.8;
        m_BaseSpeed = Math.Clamp(m_BaseSpeed, 1.5, 3.2);
        PreAnim_SetFloat(m_Table.Speed, 2.0);
        PreAnim_SetFloat(m_Table.Direction, m_OldAngle);
        // One request lets the 0.18s state and 0.3s outgoing blend progress.
        // Reissuing every tick was the v13 stationary-pose experiment.
        PreAnim_CallCommand(m_Table.Slide, 0, 0);
        Print("[MovementLab v16] Moving reversal START oldAngle=" + m_OldAngle + ", newAngle=" + m_TargetAngle + ", baseMps=" + m_BaseSpeed + ", recovery=" + m_Duration);
    }

    override void PreAnimUpdate(float pDt)
    {
        bool movingInput = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05;
        if (movingInput)
            m_NoInputTime = 0;
        else
            m_NoInputTime = m_NoInputTime + Math.Max(pDt, 0);
        // Short key-release gaps during alternating taps do not restart the brace.
        if (m_NoInputTime >= 0.10 || !MovementLabStartGate.Enabled || !MovementLabReversalSettings.Enabled || !m_Player.IsAlive() || m_Player.IsUnconscious() || m_Player.IsRaised() || m_Player.IsEmotePlaying() || m_Player.GetEntityInHands() || GetGame().GetUIManager().GetMenu() || (GetGame().GetMission() && GetGame().GetMission().IsPaused()) || pDt > 0.25 || m_Player.PhysicsIsFalling(true))
        {
            m_Abort = true;
            SetFlagFinished(true);
            return;
        }
        // Do not sweep through the directional pose atlas: that can sample
        // unrelated forward/back braces during an A/D reversal. Keep the
        // incoming brace direction until its native 0.18s gate is reached,
        // then let the graph blend to the target locomotion direction.
        float angle = m_OldAngle;
        if (m_Time + Math.Max(pDt, 0) >= 0.18)
            angle = m_TargetAngle;
        PreAnim_SetFloat(m_Table.Speed, 2.0);
        PreAnim_SetFloat(m_Table.Direction, angle);
        m_Time = m_Time + Math.Max(pDt, 0);
    }

    override void PrePhysUpdate(float pDt)
    {
        if (m_Abort)
            return;
        vector translation = vector.Zero;
        PrePhys_GetTranslation(translation);
        // Blend old/new velocity vectors without rotating motion through
        // forward on A/D reversals. No scheduled stationary dwell.
        float oldWeight = MovementLabReversalCurve.OldWeight(m_Time);
        float newWeight = MovementLabReversalCurve.NewWeight(m_Time);
        translation[0] = (m_OldSide * oldWeight + m_NewSide * newWeight) * m_BaseSpeed * pDt;
        translation[2] = (m_OldForward * oldWeight + m_NewForward * newWeight) * m_BaseSpeed * pDt;
        // Preserve vertical animation translation, gravity and engine collision.
        PrePhys_SetTranslation(translation);
    }

    override bool PostPhysUpdate(float pDt)
    {
        // Neither horizontal translation nor root rotation is locked.
        return !m_Abort && m_Time < m_Duration;
    }

    override void OnDeactivate()
    {
        vector delta = m_Player.GetPosition() - m_Origin;
        float horizontal = Math.Sqrt(delta[0] * delta[0] + delta[2] * delta[2]);
        m_Player.MovementLabReversalEnded(m_NewForward, m_NewSide, m_TargetAngle, m_Abort);
        Print("[MovementLab v16] Moving reversal END elapsed=" + m_Time + ", horizontalMeters=" + horizontal + ", aborted=" + m_Abort);
    }

    override int GetCurrentStance()
    {
        return DayZPlayerConstants.STANCEIDX_ERECT;
    }

    override int GetCurrentMovement()
    {
        return DayZPlayerConstants.MOVEMENT_RUN;
    }
}
