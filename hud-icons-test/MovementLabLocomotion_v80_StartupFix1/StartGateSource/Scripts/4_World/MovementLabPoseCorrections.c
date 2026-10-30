// Pose-only module: square idle shoulders and continuous non-aiming pose blending.
// Native camera, input, head-look limits and root body-turn controls are untouched.
modded class PlayerBase
{
    protected bool m_MovementLabSquareIdleActive;
    protected int m_MovementLabCombatUntil;
    protected bool m_MovementLabCombatGuardLogged;
    protected bool m_MovementLabIdleYawLearned;
    protected float m_MovementLabLearnedIdleYaw;
    protected int m_MovementLabSquareIdleSince = -1;

    protected bool MovementLabCombatOwnsUpperBody()
    {
        bool combat = IsRaised() || IsInIronsights() || IsInOptics() || IsFighting();
        if (GetInputController())
        {
            if (GetInputController().IsWeaponRaised() || GetInputController().IsMeleeWeaponAttack())
                combat = true;
        }
        // Read intent before native raise/punch animations have advanced a frame.
        if (GetUApi())
        {
            if (GetUApi().GetInputByID(UATempRaiseWeapon).LocalValue() > 0.05 || GetUApi().GetInputByID(UAFire).LocalValue() > 0.05)
                combat = true;
        }
        if (combat)
            m_MovementLabCombatUntil = GetGame().GetTime() + 300;
        bool blocked = combat || GetGame().GetTime() < m_MovementLabCombatUntil;
        if (blocked != m_MovementLabCombatGuardLogged)
        {
            m_MovementLabCombatGuardLogged = blocked;
            Print("[MovementLab upper body v75] Native combat ownership=" + blocked);
        }
        return blocked;
    }

    protected int m_MovementLabShoulderYawVar = -1;
    protected int m_MovementLabLeftShoulderJoint = -1;
    protected int m_MovementLabRightShoulderJoint = -1;
    protected float m_MovementLabShoulderYaw;
    protected float m_MovementLabShoulderYawVelocity[1] = {0};
    protected int m_MovementLabShoulderReportTime;

    protected void MovementLabUpdateSquareIdle(float dt)
    {
        if (GetGame().GetPlayer() != this || !MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || !GetAnimInterface())
            return;
        if (m_MovementLabShoulderYawVar < 0)
            m_MovementLabShoulderYawVar = GetAnimInterface().BindVariableFloat("MovementLabIdleShoulderYaw");
        if (m_MovementLabShoulderYawVar < 0)
            return;
        float targetYaw = 0;
        bool combatOwns = MovementLabCombatOwnsUpperBody();
        float measuredError = 0;
        float depthDifference = 0;
        HumanMovementState shoulderState = new HumanMovementState();
        GetMovementState(shoulderState);
        bool uprightPose = shoulderState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
        bool squareIdle = m_MovementLabSquareIdleActive && uprightPose && !combatOwns;
        // Prime the idle-only correction while moving so the idle pose is ready on stopping.
        // The moving graph does not consume this correction; native gait stays untouched.
        if (uprightPose && m_MovementLabContinuousHeadPose && m_MovementLabIdleYawLearned && !combatOwns)
            targetYaw = m_MovementLabLearnedIdleYaw;
        if (squareIdle)
        {
            if (m_MovementLabSquareIdleSince < 0)
                m_MovementLabSquareIdleSince = GetGame().GetTime();
        }
        else
            m_MovementLabSquareIdleSince = -1;
        // Let the underlying gait finish settling before adapting the neutral offset.
        bool measureIdle = squareIdle && GetGame().GetTime() - m_MovementLabSquareIdleSince >= 350;
        if (measureIdle)
        {
            // Upper-arm origins are the shoulder joints; forearm/hand swing does
            // not enter this measurement. Read model space, independent of world yaw.
            if (m_MovementLabLeftShoulderJoint < 0)
                m_MovementLabLeftShoulderJoint = GetBoneIndexByName("LeftArm");
            if (m_MovementLabRightShoulderJoint < 0)
                m_MovementLabRightShoulderJoint = GetBoneIndexByName("RightArm");
            if (m_MovementLabLeftShoulderJoint >= 0 && m_MovementLabRightShoulderJoint >= 0)
            {
                vector leftJoint = GetBonePositionMS(m_MovementLabLeftShoulderJoint);
                vector rightJoint = GetBonePositionMS(m_MovementLabRightShoulderJoint);
                vector shoulderLine = rightJoint - leftJoint;
                // Measure front/back shoulder yaw in model space; native graph
                // rotation must oppose this measured offset, not reinforce it.
                if (shoulderLine[0] > 0.05 && shoulderLine[0] < 1.0)
                {
                    depthDifference = shoulderLine[2];
                    measuredError = Math.Atan2(shoulderLine[2], shoulderLine[0]);
                    // The measured pose includes last frame's correction.
                    targetYaw = m_MovementLabShoulderYaw - measuredError;
                    targetYaw = Math.Clamp(targetYaw, -15 * Math.DEG2RAD, 15 * Math.DEG2RAD);
                    m_MovementLabLearnedIdleYaw = targetYaw;
                    m_MovementLabIdleYawLearned = true;
                }
            }
        }
        float blendDt = Math.Clamp(dt, 0, 0.05);
        if (combatOwns)
        {
            // Native weapon alignment owns the raised pose.
            m_MovementLabShoulderYaw = 0;
            m_MovementLabShoulderYawVelocity[0] = 0;
        }
        else
        {
            m_MovementLabShoulderYaw = Math.SmoothCD(m_MovementLabShoulderYaw, targetYaw, m_MovementLabShoulderYawVelocity, 0.35, 30 * Math.DEG2RAD, blendDt);
            m_MovementLabShoulderYaw = Math.Clamp(m_MovementLabShoulderYaw, -15 * Math.DEG2RAD, 15 * Math.DEG2RAD);
        }
        AnimSetFloat(m_MovementLabShoulderYawVar, m_MovementLabShoulderYaw);
        if (squareIdle && GetGame().GetTime() - m_MovementLabShoulderReportTime >= 1000)
        {
            m_MovementLabShoulderReportTime = GetGame().GetTime();
            float appliedDegrees = m_MovementLabShoulderYaw * Math.RAD2DEG;
            float errorDegrees = measuredError * Math.RAD2DEG;
            Print("[MovementLab square idle v75] shoulder depth difference=" + depthDifference + "; remaining yaw=" + errorDegrees + "; correction=" + appliedDegrees);
        }
    }

    protected bool m_MovementLabContinuousHeadPose;
    protected int m_MovementLabStationaryHeadOnlyVar = -1;
    protected float m_MovementLabStationaryHeadOnlyWeight;
    protected float m_MovementLabStationaryHeadOnlyVelocity[1] = {0};

    protected void MovementLabUpdateStationaryHeadOnly(float dt)
    {
        if (GetGame().GetPlayer() != this || !GetAnimInterface())
            return;
        if (m_MovementLabStationaryHeadOnlyVar < 0)
            m_MovementLabStationaryHeadOnlyVar = GetAnimInterface().BindVariableFloat("MovementLabStationaryHeadOnly");
        if (m_MovementLabStationaryHeadOnlyVar < 0)
            return;
        // One pose source across non-aiming movement and idle, regardless of yaw.
        // Crossfade only when entering/leaving this mode, never at centre or a side threshold.
        float targetWeight = 0;
        if (m_MovementLabContinuousHeadPose)
            targetWeight = 1;
        float blendDt = Math.Clamp(dt, 0, 0.05);
        if (MovementLabCombatOwnsUpperBody())
        {
            m_MovementLabStationaryHeadOnlyWeight = 0;
            m_MovementLabStationaryHeadOnlyVelocity[0] = 0;
            AnimSetFloat(m_MovementLabStationaryHeadOnlyVar, 0);
            return;
        }
        m_MovementLabStationaryHeadOnlyWeight = Math.SmoothCD(m_MovementLabStationaryHeadOnlyWeight, targetWeight, m_MovementLabStationaryHeadOnlyVelocity, 0.25, 2.0, blendDt);
        m_MovementLabStationaryHeadOnlyWeight = Math.Clamp(m_MovementLabStationaryHeadOnlyWeight, 0, 1);
        if (Math.AbsFloat(m_MovementLabStationaryHeadOnlyWeight - targetWeight) < 0.0001 && Math.AbsFloat(m_MovementLabStationaryHeadOnlyVelocity[0]) < 0.001)
        {
            m_MovementLabStationaryHeadOnlyWeight = targetWeight;
            m_MovementLabStationaryHeadOnlyVelocity[0] = 0;
        }
        AnimSetFloat(m_MovementLabStationaryHeadOnlyVar, m_MovementLabStationaryHeadOnlyWeight);
    }

    protected bool MovementLabCanUsePoseCorrections(int command, bool allowMovement = false)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this)
            return false;
        if (!IsAlive() || IsUnconscious() || IsRestrained() || IsEmotePlaying())
            return false;
        if (MovementLabCombatOwnsUpperBody())
            return false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
            return false;
        if (GetCommand_Move().IsChangingStance() || GetCommand_Move().IsOnBack() || GetCommand_Move().IsInRoll())
            return false;
        float inputSpeed;
        vector inputDirection;
        GetInputController().GetMovement(inputSpeed, inputDirection);
        if (!allowMovement && (inputSpeed > 0.01 || GetCommand_Move().GetCurrentMovementSpeed() > 0.05))
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
            // These flags control animation weights only. No camera/input override.
            m_MovementLabContinuousHeadPose = MovementLabCanUsePoseCorrections(pCurrentCommandID, true);
            m_MovementLabSquareIdleActive = MovementLabCanUsePoseCorrections(pCurrentCommandID);
        }
        MovementLabUpdateStationaryHeadOnly(pDt);
        MovementLabUpdateSquareIdle(pDt);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
