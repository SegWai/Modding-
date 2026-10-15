// Built from v42. Native stationary free-look; camera shares player look limits.
// No heading override, automatic body turn, custom camera matrix or yaw accumulator.
modded class PlayerBase
{
    protected bool m_MovementLabHead90Active;
    protected int m_MovementLabLeftHeadOnlyVar = -1;

    protected void MovementLabUpdateLeftHeadOnly()
    {
        if (GetGame().GetPlayer() != this || !GetAnimInterface())
            return;
        if (m_MovementLabLeftHeadOnlyVar < 0)
            m_MovementLabLeftHeadOnlyVar = GetAnimInterface().BindVariableFloat("MovementLabLeftHeadOnly");
        if (m_MovementLabLeftHeadOnlyVar < 0)
            return;
        float headOnly = 0;
        if (m_MovementLabHead90Active)
        {
            vector cameraDirection = GetGame().GetCurrentCameraDirection();
            vector cameraAngles = cameraDirection.VectorToAngles();
            vector bodyAngles = GetOrientation();
            float relativeYaw = fixAngle_180_180(cameraAngles[0] - bodyAngles[0]);
            if (relativeYaw < -0.5)
                headOnly = 1;
        }
        AnimSetFloat(m_MovementLabLeftHeadOnlyVar, headOnly);
    }

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
                    Print("[MovementLab head90 v54] ACTIVE: native free-look, camera shares native player head-look endpoints; no body-turn request.");
                }
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.ONE_FRAME, true);
            }
            else if (m_MovementLabHead90Active)
            {
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.DISABLED, false);
                m_MovementLabHead90Active = false;
                Print("[MovementLab head90 v54] RELEASED: native movement/aiming controls.");
            }
        }
        MovementLabUpdateLeftHeadOnly();
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
            // Read the player head-look bounds, rather than imposing a separate
            // camera-only 90-degree cutoff before the native head look is complete.
            float headDown;
            float headUp;
            float headLeft;
            float headRight;
            player.GetLookLimits(headDown, headUp, headLeft, headRight);
            float leftLimit = Math.Max(pMin, headLeft);
            float rightLimit = Math.Min(pMax, headRight);
            if (leftLimit > rightLimit)
            {
                leftLimit = pMin;
                rightLimit = pMax;
            }
            float limitedYaw = super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, leftLimit, rightLimit, pDt);
            if (GetGame().GetTime() - m_MovementLabHead90MeasureTime >= 500)
            {
                m_MovementLabHead90MeasureTime = GetGame().GetTime();
                vector renderedDirection = GetGame().GetCurrentCameraDirection();
                vector renderedAngles = renderedDirection.VectorToAngles();
                vector bodyAngles = player.GetOrientation();
                float measuredYaw = fixAngle_180_180(renderedAngles[0] - bodyAngles[0]);
                float inputHeading = m_pInput.GetHeadingAngle() * Math.RAD2DEG;
                Print("[MovementLab head90 v54] Camera=" + GetCameraName() + "; shared head limits=" + headLeft + "/" + headRight + "; camera bounds=" + leftLimit + "/" + rightLimit + "; native yaw=" + limitedYaw + "; rendered yaw relative body=" + measuredYaw + "; body world yaw=" + bodyAngles[0] + "; input heading=" + inputHeading);
            }
            return limitedYaw;
        }
        return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, pMin, pMax, pDt);
    }
}
