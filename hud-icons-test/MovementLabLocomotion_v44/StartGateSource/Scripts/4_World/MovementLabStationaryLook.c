// Experimental stationary head-look and native turn-in-place handoff.
// Angles in HeadingModel are radians; camera and native turn setting use degrees.
modded class PlayerBase
{
    protected bool m_MovementLabLookActive;
    protected bool m_MovementLabLookTurning;
    protected float m_MovementLabLookWorld;
    protected float m_MovementLabLookStepTarget;
    protected float m_MovementLabLookCameraExtra;
    protected float m_MovementLabLookNativeTurnAngle;
    protected float m_MovementLabLookNativeDown;
    protected float m_MovementLabLookNativeUp;
    protected float m_MovementLabLookNativeLeft;
    protected float m_MovementLabLookNativeRight;
    protected int m_MovementLabLookStance = -1;

    static float MovementLabWrapLook(float angle)
    {
        while (angle > Math.PI)
            angle = angle - Math.PI2;
        while (angle < -Math.PI)
            angle = angle + Math.PI2;
        return angle;
    }
    float MovementLabStationaryCameraExtra()
    {
        return m_MovementLabLookCameraExtra;
    }
    protected bool MovementLabCanStationaryLook(SDayZPlayerHeadingModel model)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this)
            return false;
        if (!IsAlive() || IsUnconscious() || IsRestrained() || IsRaised() || IsInIronsights() || IsInOptics() || IsEmotePlaying())
            return false;
        if (model.m_iCurrentCommandID != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move() || !GetInputController())
            return false;
        if (GetCommand_Move().IsChangingStance() || GetCommand_Move().IsOnBack() || GetCommand_Move().IsInRoll())
            return false;
        if (GetCommand_Move().GetCurrentMovementSpeed() > 0.01)
            return false;
        float inputAngle;
        if (GetCommand_Move().GetCurrentInputAngle(inputAngle))
            return false;
        if (GetInputController().CameraIsFreeLook() || GetInputController().CameraIsTracking())
            return false;
        if (GetActionManager() && GetActionManager().GetRunningAction())
            return false;
        if (GetWeaponManager() && GetWeaponManager().IsRunning())
            return false;
        if (!GetGame().GetInput().HasGameFocus() || GetGame().GetUIManager().GetMenu() || GetGame().GetMission().IsPaused())
            return false;
        return true;
    }
    protected void MovementLabReleaseStationaryLook()
    {
        if (m_MovementLabLookActive)
        {
            GetDayZPlayerType().CommandMoveSettingsW().m_fTurnAngle = m_MovementLabLookNativeTurnAngle;
            SetLookLimits(m_MovementLabLookNativeDown, m_MovementLabLookNativeUp, m_MovementLabLookNativeLeft, m_MovementLabLookNativeRight);
        }
        m_MovementLabLookActive = false;
        m_MovementLabLookTurning = false;
        m_MovementLabLookCameraExtra = 0;
        m_MovementLabLookStance = -1;
    }
    override bool HeadingModel(float pDt, SDayZPlayerHeadingModel pModel)
    {
        if (!MovementLabCanStationaryLook(pModel) || pDt <= 0 || pDt > 0.25)
        {
            // Pass the accumulated world direction back before native movement/aiming takes over.
            bool restoringLook = m_MovementLabLookActive;
            if (restoringLook)
                pModel.m_fHeadingAngle = m_MovementLabLookWorld;
            MovementLabReleaseStationaryLook();
            bool nativeChanged = super.HeadingModel(pDt, pModel);
            return restoringLook || nativeChanged;
        }
        HumanMovementState lookState = new HumanMovementState();
        GetMovementState(lookState);
        if (m_MovementLabLookActive && m_MovementLabLookStance != lookState.m_iStanceIdx)
            MovementLabReleaseStationaryLook();
        SHumanCommandMoveSettings moveSettings = GetDayZPlayerType().CommandMoveSettingsW();
        if (!m_MovementLabLookActive)
        {
            m_MovementLabLookNativeTurnAngle = moveSettings.m_fTurnAngle;
            GetLookLimits(m_MovementLabLookNativeDown, m_MovementLabLookNativeUp, m_MovementLabLookNativeLeft, m_MovementLabLookNativeRight);
            m_MovementLabLookWorld = pModel.m_fHeadingAngle;
            m_MovementLabLookStance = lookState.m_iStanceIdx;
            m_MovementLabLookActive = true;
            SetLookLimits(m_MovementLabLookNativeDown, m_MovementLabLookNativeUp, -90, 90);
        }
        else
        {
            vector lookDelta = GetInputController().GetAimDelta(pDt);
            m_MovementLabLookWorld = MovementLabWrapLook(m_MovementLabLookWorld + lookDelta[0]);
        }
        float bodyAngle = pModel.m_fOrientationAngle;
        float difference = MovementLabWrapLook(m_MovementLabLookWorld - bodyAngle);
        if (!m_MovementLabLookTurning && Math.AbsFloat(difference) > 140 * Math.DEG2RAD)
        {
            float stepDirection = 1;
            if (difference < 0)
                stepDirection = -1;
            m_MovementLabLookStepTarget = bodyAngle + stepDirection * 45 * Math.DEG2RAD;
            m_MovementLabLookTurning = true;
            Print("[MovementLab stationary look v43] 140-degree threshold: requesting native 45-degree turn, stance=" + lookState.m_iStanceIdx);
        }
        if (m_MovementLabLookTurning)
        {
            float remaining = MovementLabWrapLook(m_MovementLabLookStepTarget - bodyAngle);
            if (Math.AbsFloat(remaining) < 2 * Math.DEG2RAD)
                m_MovementLabLookTurning = false;
        }
        if (m_MovementLabLookTurning)
        {
            // Native turning owns the feet/root; do not teleport or SetOrientation.
            moveSettings.m_fTurnAngle = 44;
            pModel.m_fHeadingAngle = bodyAngle + MovementLabWrapLook(m_MovementLabLookStepTarget - bodyAngle);
        }
        else
        {
            // Separate the camera's extra yaw from the head's 90-degree limit.
            moveSettings.m_fTurnAngle = 140;
            pModel.m_fHeadingAngle = bodyAngle + Math.Clamp(difference, -Math.PI_HALF, Math.PI_HALF);
        }
        m_MovementLabLookCameraExtra = MovementLabWrapLook(m_MovementLabLookWorld - pModel.m_fHeadingAngle) * Math.RAD2DEG;
        m_fLastHeadingDiff = 0;
        return true;
    }
}

modded class DayZPlayerCameraBase
{
    override float UpdateLRAngleUnlocked(out float pAngle, out float pAngleAdd, float pMin, float pMax, float pDt)
    {
        float nativeYaw = super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, pMin, pMax, pDt);
        PlayerBase player = PlayerBase.Cast(m_pPlayer);
        if (player)
            return nativeYaw + player.MovementLabStationaryCameraExtra();
        return nativeYaw;
    }
}
