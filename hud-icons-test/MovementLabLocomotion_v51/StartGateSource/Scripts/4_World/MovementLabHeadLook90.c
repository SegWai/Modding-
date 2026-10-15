// Built from v42. Native stationary free-look with a hard +/-90 yaw limit.
// No heading override, automatic body turn, custom camera matrix or yaw accumulator.
modded class PlayerBase
{
    protected bool m_MovementLabHead90Active;
    protected float m_MovementLabHead90Down;
    protected float m_MovementLabHead90Up;
    protected float m_MovementLabHead90Left;
    protected float m_MovementLabHead90Right;

    bool MovementLabHead90Active()
    {
        return m_MovementLabHead90Active;
    }
    protected bool MovementLabCanHead90(int command)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this)
            return false;
        if (!IsAlive() || IsUnconscious() || IsRestrained() || IsEmotePlaying())
            return false;
        if (IsRaised() || IsInIronsights() || IsInOptics() || GetInputController().IsWeaponRaised())
            return false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
            return false;
        if (GetCommand_Move().IsChangingStance() || GetCommand_Move().IsOnBack() || GetCommand_Move().IsInRoll())
            return false;
        float inputSpeed;
        vector inputDirection;
        GetInputController().GetMovement(inputSpeed, inputDirection);
        if (inputSpeed > 0.01 || GetCommand_Move().GetCurrentMovementSpeed() > 0.05)
            return false;
        if (GetActionManager() && GetActionManager().GetRunningAction())
            return false;
        if (GetWeaponManager() && GetWeaponManager().IsRunning())
            return false;
        if (!GetGame().GetInput().HasGameFocus() || GetGame().GetUIManager().GetMenu() || GetGame().GetMission().IsPaused())
            return false;
        return true;
    }
    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        if (GetInputController() && GetGame().GetPlayer() == this)
        {
            if (MovementLabCanHead90(pCurrentCommandID))
            {
                if (!m_MovementLabHead90Active)
                {
                    GetLookLimits(m_MovementLabHead90Down, m_MovementLabHead90Up, m_MovementLabHead90Left, m_MovementLabHead90Right);
                    SetLookLimits(m_MovementLabHead90Down, m_MovementLabHead90Up, -90, 90);
                    m_MovementLabHead90Active = true;
                    Print("[MovementLab head90 v51] ACTIVE: native free-look, head/camera +/-90; no body-turn request.");
                }
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.ONE_FRAME, true);
            }
            else if (m_MovementLabHead90Active)
            {
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.DISABLED, false);
                SetLookLimits(m_MovementLabHead90Down, m_MovementLabHead90Up, m_MovementLabHead90Left, m_MovementLabHead90Right);
                m_MovementLabHead90Active = false;
                Print("[MovementLab head90 v51] RELEASED: native movement/aiming controls.");
            }
        }
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}

modded class DayZPlayerCameraBase
{
    override float UpdateLRAngleUnlocked(out float pAngle, out float pAngleAdd, float pMin, float pMax, float pDt)
    {
        PlayerBase player = PlayerBase.Cast(m_pPlayer);
        if (player && player.MovementLabHead90Active())
        {
            // Clamp inside the native input path, so excess mouse input is discarded
            // instead of queued beyond the stop. Keep tighter native camera limits.
            float leftLimit = Math.Max(pMin, -90);
            float rightLimit = Math.Min(pMax, 90);
            return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, leftLimit, rightLimit, pDt);
        }
        return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, pMin, pMax, pDt);
    }
}
