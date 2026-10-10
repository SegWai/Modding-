// Experimental native graph command + animation/physics separation.
// The engine must verify whether repeated CMD_SlidingPose retains the state.
class MovementLabPoseSettings
{
    static bool Enabled = true;
    static float HoldSeconds = 0.32;
}

class MovementLabPoseTable
{
    int Slide;
    int Speed;
    int Direction;

    void MovementLabPoseTable(Human player)
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

class MovementLabPoseCommand : HumanCommandScript
{
    protected PlayerBase m_Player;
    protected ref MovementLabPoseTable m_Table;
    protected float m_Angle;
    protected float m_Time;
    protected float m_Duration;
    protected vector m_Origin;
    protected bool m_Abort;
    protected int m_Requests;

    void MovementLabPoseCommand(PlayerBase player, MovementLabPoseTable table, float angle)
    {
        m_Player = player;
        m_Table = table;
        m_Angle = angle;
        m_Duration = MovementLabPoseSettings.HoldSeconds;
    }

    override void OnActivate()
    {
        m_Origin = m_Player.GetPosition();
        Print("[MovementLab v13] Native pose hold START angle=" + m_Angle + ", duration=" + m_Duration);
    }

    override void PreAnimUpdate(float pDt)
    {
        if (!MovementLabStartGate.Enabled || !MovementLabPoseSettings.Enabled || !m_Player.IsAlive() || m_Player.IsUnconscious() || m_Player.IsRaised() || m_Player.IsEmotePlaying() || m_Player.GetEntityInHands() || GetGame().GetUIManager().GetMenu() || (GetGame().GetMission() && GetGame().GetMission().IsPaused()) || pDt > 0.25 || m_Player.PhysicsIsFalling(true))
        {
            m_Abort = true;
            SetFlagFinished(true);
            return;
        }
        // Keep the RUN pose branch, even though X/Z translation is suppressed.
        // Setting animation speed=0 would select idle/walk and lose the brace.
        PreAnim_SetFloat(m_Table.Speed, 2.0);
        PreAnim_SetFloat(m_Table.Direction, m_Angle);
        PreAnim_CallCommand(m_Table.Slide, 0, 0);
        m_Requests = m_Requests + 1;
        m_Time = m_Time + Math.Max(pDt, 0);
    }

    override void PrePhysUpdate(float pDt)
    {
        if (m_Abort)
            return;
        vector translation = vector.Zero;
        PrePhys_GetTranslation(translation);
        // Preserve the vertical component; do not teleport or disable gravity.
        translation[0] = 0;
        translation[2] = 0;
        PrePhys_SetTranslation(translation);
    }

    override bool PostPhysUpdate(float pDt)
    {
        PostPhys_LockRotation();
        return !m_Abort && m_Time < m_Duration;
    }

    override void OnDeactivate()
    {
        vector delta = m_Player.GetPosition() - m_Origin;
        float horizontal = Math.Sqrt(delta[0] * delta[0] + delta[2] * delta[2]);
        m_Player.MovementLabPoseEnded();
        Print("[MovementLab v13] Native pose hold END elapsed=" + m_Time + ", horizontalMeters=" + horizontal + ", requests=" + m_Requests + ", aborted=" + m_Abort);
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

