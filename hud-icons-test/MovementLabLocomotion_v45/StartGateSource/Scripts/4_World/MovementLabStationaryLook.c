// v45: explicitly route stationary mouse input through native free-look.
// The body turn is requested through HeadingModel, not live type-config edits.
modded class PlayerBase
{
    protected bool m_MovementLabLookActive;
    protected bool m_MovementLabLookInitialized;
    protected bool m_MovementLabLookTurning;
    protected float m_MovementLabLookWorld;
    protected float m_MovementLabLookStepTarget;
    protected float m_MovementLabLookCameraYaw;
    protected float m_MovementLabLookNativeDown;
    protected float m_MovementLabLookNativeUp;
    protected float m_MovementLabLookNativeLeft;
    protected float m_MovementLabLookNativeRight;
    protected int m_MovementLabLookReportTime;
    protected float m_MovementLabLookTurnStarted;

    static float MovementLabWrapLook(float angle)
    {
        while (angle > Math.PI)
            angle = angle - Math.PI2;
        while (angle < -Math.PI)
            angle = angle + Math.PI2;
        return angle;
    }
    bool MovementLabStationaryLookActive()
    {
        return m_MovementLabLookActive && m_MovementLabLookInitialized;
    }
    float MovementLabStationaryCameraYaw()
    {
        return m_MovementLabLookCameraYaw;
    }
    protected string MovementLabStationaryLookBlock(int command)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this)
            return "disabled or not local offline player";
        if (!IsAlive() || IsUnconscious() || IsRestrained() || IsEmotePlaying())
            return "character unavailable";
        if (IsRaised() || IsInIronsights() || IsInOptics() || GetInputController().IsWeaponRaised())
            return "aiming";
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
            return "not move command";
        if (GetCommand_Move().IsChangingStance() || GetCommand_Move().IsOnBack() || GetCommand_Move().IsInRoll())
            return "stance transition or prone on back";
        float inputSpeed;
        vector inputDirection;
        GetInputController().GetMovement(inputSpeed, inputDirection);
        if (inputSpeed > 0.01 || GetCommand_Move().GetCurrentMovementSpeed() > 0.05)
            return "moving";
        if (GetInputController().CameraIsTracking())
            return "head tracking";
        if (GetActionManager() && GetActionManager().GetRunningAction())
            return "performing action";
        if (GetWeaponManager() && GetWeaponManager().IsRunning())
            return "weapon action";
        if (!GetGame().GetInput().HasGameFocus() || GetGame().GetUIManager().GetMenu() || GetGame().GetMission().IsPaused())
            return "menu or no game focus";
        return "";
    }
    protected void MovementLabStopStationaryLook()
    {
        if (!m_MovementLabLookActive)
            return;
        GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.DISABLED, false);
        SetLookLimits(m_MovementLabLookNativeDown, m_MovementLabLookNativeUp, m_MovementLabLookNativeLeft, m_MovementLabLookNativeRight);
        m_MovementLabLookActive = false;
        m_MovementLabLookTurning = false;
    }
    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        if (GetInputController() && GetGame().GetPlayer() == this)
        {
            string blocked = MovementLabStationaryLookBlock(pCurrentCommandID);
            if (blocked == "")
            {
                if (!m_MovementLabLookActive)
                {
                    GetLookLimits(m_MovementLabLookNativeDown, m_MovementLabLookNativeUp, m_MovementLabLookNativeLeft, m_MovementLabLookNativeRight);
                    SetLookLimits(m_MovementLabLookNativeDown, m_MovementLabLookNativeUp, -90, 90);
                    m_MovementLabLookInitialized = false;
                    m_MovementLabLookActive = true;
                    Print("[MovementLab stationary look v45] ACTIVE: automatic free-look; head limit 90; turn threshold 140.");
                }
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.ONE_FRAME, true);
            }
            else
            {
                if (m_MovementLabLookActive)
                    Print("[MovementLab stationary look v45] Released: " + blocked);
                MovementLabStopStationaryLook();
                if (MovementLabStartGate.Enabled && GetGame().GetTime() - m_MovementLabLookReportTime >= 3000)
                {
                    m_MovementLabLookReportTime = GetGame().GetTime();
                    Print("[MovementLab stationary look v45] Inactive: " + blocked);
                }
            }
        }
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
    override bool HeadingModel(float pDt, SDayZPlayerHeadingModel pModel)
    {
        if (!m_MovementLabLookActive)
        {
            bool handoff = m_MovementLabLookInitialized;
            if (handoff)
            {
                pModel.m_fHeadingAngle = m_MovementLabLookWorld;
                m_MovementLabLookInitialized = false;
            }
            bool nativeChanged = super.HeadingModel(pDt, pModel);
            return handoff || nativeChanged;
        }
        if (!m_MovementLabLookInitialized)
        {
            m_MovementLabLookWorld = pModel.m_fHeadingAngle;
            m_MovementLabLookInitialized = true;
        }
        else if (pDt > 0 && pDt <= 0.25)
        {
            vector mouseDelta = GetInputController().GetAimDelta(pDt);
            m_MovementLabLookWorld = MovementLabWrapLook(m_MovementLabLookWorld + mouseDelta[0]);
        }
        float bodyAngle = pModel.m_fOrientationAngle;
        float difference = MovementLabWrapLook(m_MovementLabLookWorld - bodyAngle);
        if (!m_MovementLabLookTurning && Math.AbsFloat(difference) > 140 * Math.DEG2RAD)
        {
            float direction = 1;
            if (difference < 0)
                direction = -1;
            // 0.1 degree above native's strict 45-degree activation threshold.
            m_MovementLabLookStepTarget = bodyAngle + direction * 45.1 * Math.DEG2RAD;
            m_MovementLabLookTurning = true;
            m_MovementLabLookTurnStarted = GetGame().GetTime();
            Print("[MovementLab stationary look v45] TURN requested; camera/body degrees=" + difference * Math.RAD2DEG);
        }
        if (m_MovementLabLookTurning && Math.AbsFloat(MovementLabWrapLook(m_MovementLabLookStepTarget - bodyAngle)) < 1 * Math.DEG2RAD)
        {
            m_MovementLabLookTurning = false;
            Print("[MovementLab stationary look v45] TURN completed.");
        }
        pModel.m_fHeadingAngle = bodyAngle;
        if (m_MovementLabLookTurning)
            pModel.m_fHeadingAngle = bodyAngle + MovementLabWrapLook(m_MovementLabLookStepTarget - bodyAngle);
        m_MovementLabLookCameraYaw = MovementLabWrapLook(m_MovementLabLookWorld - pModel.m_fHeadingAngle) * Math.RAD2DEG;
        if (GetGame().GetTime() - m_MovementLabLookReportTime >= 1500)
        {
            m_MovementLabLookReportTime = GetGame().GetTime();
            Print("[MovementLab stationary look v45] Active; camera/body=" + difference * Math.RAD2DEG + "; native free-look=" + GetInputController().CameraIsFreeLook() + "; turning=" + m_MovementLabLookTurning);
        }
        m_fLastHeadingDiff = 0;
        return true;
    }
}

modded class DayZPlayerCameraBase
{
    protected bool m_MovementLabCameraWasStationary;
    override float UpdateLRAngleUnlocked(out float pAngle, out float pAngleAdd, float pMin, float pMax, float pDt)
    {
        PlayerBase player = PlayerBase.Cast(m_pPlayer);
        if (player && player.MovementLabStationaryLookActive())
        {
            pAngle = 0;
            pAngleAdd = player.MovementLabStationaryCameraYaw();
            m_MovementLabCameraWasStationary = true;
            return pAngleAdd;
        }
        if (m_MovementLabCameraWasStationary)
        {
            pAngle = 0;
            pAngleAdd = 0;
            m_MovementLabCameraWasStationary = false;
        }
        return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, pMin, pMax, pDt);
    }
}
