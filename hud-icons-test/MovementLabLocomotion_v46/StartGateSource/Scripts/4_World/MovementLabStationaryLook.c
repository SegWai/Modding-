// v46: render-frame mouse sampling, independent animation head clamp and full-body turn.
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
    protected float m_MovementLabLookHeadingBase;
    protected float m_MovementLabLookTurnBodyStart;
    protected int m_MovementLabLookMouseTime = -1;
    protected bool m_MovementLabLookRecovery;
    protected int m_MovementLabHeadClampVar = -1;
    protected int m_MovementLabHeadYawVar = -1;

    protected void MovementLabSetHeadPose(bool active, float yaw)
    {
        if (!GetAnimInterface())
            return;
        if (m_MovementLabHeadClampVar < 0)
            m_MovementLabHeadClampVar = GetAnimInterface().BindVariableFloat("MovementLabHeadClamp");
        if (m_MovementLabHeadYawVar < 0)
            m_MovementLabHeadYawVar = GetAnimInterface().BindVariableFloat("MovementLabHeadYaw");
        float weight = 0;
        if (active)
            weight = 1;
        if (m_MovementLabHeadClampVar >= 0)
            AnimSetFloat(m_MovementLabHeadClampVar, weight);
        if (m_MovementLabHeadYawVar >= 0)
            AnimSetFloat(m_MovementLabHeadYawVar, Math.Clamp(yaw, -90, 90));
    }

    float MovementLabSampleLookCamera(float dt)
    {
        int now = GetGame().GetTime();
        if (m_MovementLabLookMouseTime != now && dt > 0 && dt <= 0.25)
        {
            m_MovementLabLookMouseTime = now;
            vector mouseDelta = GetInputController().GetAimDelta(dt);
            // Native heading angles are negative to camera/world yaw.
            m_MovementLabLookWorld = MovementLabWrapLook(m_MovementLabLookWorld - mouseDelta[0]);
        }
        m_MovementLabLookCameraYaw = -MovementLabWrapLook(m_MovementLabLookWorld - m_MovementLabLookHeadingBase) * Math.RAD2DEG;
        return m_MovementLabLookCameraYaw;
    }

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
        if (m_MovementLabLookRecovery)
        {
            float recoverySpeed;
            vector recoveryDirection;
            GetInputController().GetMovement(recoverySpeed, recoveryDirection);
            if (recoverySpeed > 0.01 || IsRaised())
                m_MovementLabLookRecovery = false;
            else
                return "turn recovery: move or aim to reset";
        }
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
        GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.ONE_FRAME, false);
        MovementLabSetHeadPose(false, 0);
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
                    m_MovementLabLookMouseTime = -1;
                    m_MovementLabLookActive = true;
                    Print("[MovementLab stationary look v46] ACTIVE: automatic free-look; head limit 90; full-body turn threshold 145.");
                }
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.ONE_FRAME, true);
            }
            else
            {
                if (m_MovementLabLookActive)
                    Print("[MovementLab stationary look v46] Released: " + blocked);
                MovementLabStopStationaryLook();
                if (MovementLabStartGate.Enabled && GetGame().GetTime() - m_MovementLabLookReportTime >= 3000)
                {
                    m_MovementLabLookReportTime = GetGame().GetTime();
                    Print("[MovementLab stationary look v46] Inactive: " + blocked);
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
        float bodyAngle = pModel.m_fOrientationAngle;
        float difference = MovementLabWrapLook(m_MovementLabLookWorld - bodyAngle);
        if (!m_MovementLabLookTurning && Math.AbsFloat(difference) > 145 * Math.DEG2RAD)
        {
            // Capture the actual camera direction at the crossing, not a 45-degree increment.
            m_MovementLabLookStepTarget = m_MovementLabLookWorld;
            m_MovementLabLookTurnBodyStart = bodyAngle;
            m_MovementLabLookTurning = true;
            m_MovementLabLookTurnStarted = GetGame().GetTime();
            Print("[MovementLab stationary look v46] TURN requested; camera/body degrees=" + difference * Math.RAD2DEG);
        }
        if (m_MovementLabLookTurning)
        {
            // Apply a smooth root-heading handoff instead of waiting forever for
            // the native turn controller to settle within its default dead zone.
            float turnProgress = Math.Clamp((GetGame().GetTime() - m_MovementLabLookTurnStarted) / 550.0, 0, 1);
            float turnEase = turnProgress * turnProgress * (3 - 2 * turnProgress);
            float turnArc = MovementLabWrapLook(m_MovementLabLookStepTarget - m_MovementLabLookTurnBodyStart);
            float turnBody = m_MovementLabLookTurnBodyStart + turnArc * turnEase;
            pModel.m_fOrientationAngle = bodyAngle + MovementLabWrapLook(turnBody - bodyAngle);
            bodyAngle = pModel.m_fOrientationAngle;
            difference = MovementLabWrapLook(m_MovementLabLookWorld - bodyAngle);
            if (turnProgress >= 1)
            {
                m_MovementLabLookTurning = false;
                Print("[MovementLab stationary look v46] Full heading handoff completed.");
            }
        }
        if (m_MovementLabLookTurning && GetGame().GetTime() - m_MovementLabLookTurnStarted > 2500)
        {
            Print("[MovementLab stationary look v46] Turn did not complete: releasing to native controls; move or aim to reset.");
            m_MovementLabLookRecovery = true;
            MovementLabStopStationaryLook();
            pModel.m_fHeadingAngle = m_MovementLabLookWorld;
            m_MovementLabLookInitialized = false;
            super.HeadingModel(pDt, pModel);
            return true;
        }
        MovementLabSetHeadPose(true, -difference * Math.RAD2DEG);
        pModel.m_fHeadingAngle = bodyAngle;
        if (m_MovementLabLookTurning)
            pModel.m_fHeadingAngle = bodyAngle + MovementLabWrapLook(m_MovementLabLookStepTarget - bodyAngle);
        m_MovementLabLookHeadingBase = pModel.m_fHeadingAngle;
        m_MovementLabLookCameraYaw = -MovementLabWrapLook(m_MovementLabLookWorld - pModel.m_fHeadingAngle) * Math.RAD2DEG;
        if (GetGame().GetTime() - m_MovementLabLookReportTime >= 1500)
        {
            m_MovementLabLookReportTime = GetGame().GetTime();
            Print("[MovementLab stationary look v46] Active; camera/body=" + difference * Math.RAD2DEG + "; native free-look=" + GetInputController().CameraIsFreeLook() + "; turning=" + m_MovementLabLookTurning + "; head clamp binding=" + m_MovementLabHeadClampVar + "; head yaw binding=" + m_MovementLabHeadYawVar);
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
            pAngleAdd = player.MovementLabSampleLookCamera(pDt);
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
