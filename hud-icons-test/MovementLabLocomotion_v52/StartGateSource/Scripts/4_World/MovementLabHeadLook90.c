// Built from v42. Native stationary free-look with a hard +/-90 yaw limit.
// No heading override, automatic body turn, custom camera matrix or yaw accumulator.
modded class PlayerBase
{
    protected bool m_MovementLabHead90Active;

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
                    m_MovementLabHead90Active = true;
                    Print("[MovementLab head90 v52] ACTIVE: native free-look, camera +/-90, original native player look limits; no body-turn request.");
                }
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.ONE_FRAME, true);
            }
            else if (m_MovementLabHead90Active)
            {
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.DISABLED, false);
                m_MovementLabHead90Active = false;
                Print("[MovementLab head90 v52] RELEASED: native movement/aiming controls.");
            }
        }
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}

modded class DayZPlayerCameraBase
{
    protected int m_MovementLabHead90MeasureTime;
    override float UpdateLRAngleUnlocked(out float pAngle, out float pAngleAdd, float pMin, float pMax, float pDt)
    {
        PlayerBase player = PlayerBase.Cast(m_pPlayer);
        if (player && player.MovementLabHead90Active())
        {
            // Clamp inside the native input path, so excess mouse input is discarded
            // instead of queued beyond the stop. Keep tighter native camera limits.
            float leftLimit = Math.Max(pMin, -90);
            float rightLimit = Math.Min(pMax, 90);
            float limitedYaw = super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, leftLimit, rightLimit, pDt);
            if (GetGame().GetTime() - m_MovementLabHead90MeasureTime >= 500)
            {
                m_MovementLabHead90MeasureTime = GetGame().GetTime();
                vector renderedDirection = GetGame().GetCurrentCameraDirection();
                vector renderedAngles = renderedDirection.VectorToAngles();
                vector bodyAngles = player.GetOrientation();
                float measuredYaw = fixAngle_180_180(renderedAngles[0] - bodyAngles[0]);
                float inputHeading = m_pInput.GetHeadingAngle() * Math.RAD2DEG;
                Print("[MovementLab head90 v52] Camera=" + GetCameraName() + "; native yaw=" + limitedYaw + "; rendered yaw relative body=" + measuredYaw + "; body world yaw=" + bodyAngles[0] + "; input heading=" + inputHeading);
            }
            return limitedYaw;
        }
        return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, pMin, pMax, pDt);
    }
}
