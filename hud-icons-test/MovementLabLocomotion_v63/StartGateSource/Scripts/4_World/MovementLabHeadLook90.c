// Built from v42. Native stationary free-look; camera shares player look limits.
// No heading override, automatic body turn, custom camera matrix or yaw accumulator.
modded class PlayerBase
{
    protected bool m_MovementLabHead90Active;
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
            Print("[MovementLab upper body v63] Native combat ownership=" + blocked);
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
        bool squareIdle = m_MovementLabHead90Active && uprightPose && !combatOwns;
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
            Print("[MovementLab square idle v63] shoulder depth difference=" + depthDifference + "; remaining yaw=" + errorDegrees + "; correction=" + appliedDegrees);
        }
    }

    protected bool m_MovementLabContinuousHeadPose;
    protected float m_MovementLabHeadExtraTarget;
    protected float m_MovementLabHeadExtraCurrent;
    protected float m_MovementLabHeadExtraVelocity[1] = {0};
    protected int m_MovementLabHeadExtraYawVar = -1;

    void MovementLabUpdateHeadExtraYaw(float cameraYaw, float leftLimit, float rightLimit)
    {
        if (!GetAnimInterface())
            return;
        if (m_MovementLabHeadExtraYawVar < 0)
            m_MovementLabHeadExtraYawVar = GetAnimInterface().BindVariableFloat("MovementLabHeadExtraYaw");
        if (m_MovementLabHeadExtraYawVar < 0)
            return;
        float sideRange = rightLimit;
        if (cameraYaw < 0)
            sideRange = -leftLimit;
        float extraYaw = 0;
        if (m_MovementLabHead90Active && sideRange > 0)
            extraYaw = Math.Clamp(cameraYaw / sideRange, -1, 1) * 10 * Math.DEG2RAD;
        m_MovementLabHeadExtraTarget = extraYaw;
    }
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
            m_MovementLabHeadExtraTarget = 0;
            m_MovementLabHeadExtraCurrent = 0;
            m_MovementLabHeadExtraVelocity[0] = 0;
            AnimSetFloat(m_MovementLabStationaryHeadOnlyVar, 0);
            if (m_MovementLabHeadExtraYawVar >= 0)
                AnimSetFloat(m_MovementLabHeadExtraYawVar, 0);
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
        if (!m_MovementLabHead90Active)
            m_MovementLabHeadExtraTarget = 0;
        m_MovementLabHeadExtraCurrent = Math.SmoothCD(m_MovementLabHeadExtraCurrent, m_MovementLabHeadExtraTarget, m_MovementLabHeadExtraVelocity, 0.20, 1.0, blendDt);
        if (m_MovementLabHeadExtraYawVar >= 0)
            AnimSetFloat(m_MovementLabHeadExtraYawVar, m_MovementLabHeadExtraCurrent);
    }

    bool MovementLabHead90Active()
    {
        return m_MovementLabHead90Active;
    }
    protected bool MovementLabCanHead90(int command, bool allowMovement = false)
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
            // Pose continuity includes movement; automatic free-look remains stationary only.
            bool nextContinuousPose = MovementLabCanHead90(pCurrentCommandID, true);
            if (nextContinuousPose != m_MovementLabContinuousHeadPose)
                Print("[MovementLab head90 v63] Continuous movement/idle pose=" + nextContinuousPose);
            m_MovementLabContinuousHeadPose = nextContinuousPose;
            if (MovementLabCanHead90(pCurrentCommandID))
            {
                if (!m_MovementLabHead90Active)
                {
                    m_MovementLabHead90Active = true;
                    Print("[MovementLab head90 v63] ACTIVE: native free-look, camera shares native player head-look endpoints; no body-turn request.");
                }
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.ONE_FRAME, true);
            }
            else if (m_MovementLabHead90Active)
            {
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.DISABLED, false);
                m_MovementLabHead90Active = false;
                Print("[MovementLab head90 v63] RELEASED: native movement/aiming controls.");
            }
        }
        MovementLabUpdateStationaryHeadOnly(pDt);
        MovementLabUpdateSquareIdle(pDt);
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
            float leftLimit = Math.Max(pMin, headLeft) - 10;
            float rightLimit = Math.Min(pMax, headRight) + 10;
            if (leftLimit > rightLimit)
            {
                leftLimit = pMin - 10;
                rightLimit = pMax + 10;
            }
            float limitedYaw = super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, leftLimit, rightLimit, pDt);
            player.MovementLabUpdateHeadExtraYaw(limitedYaw, leftLimit, rightLimit);
            if (GetGame().GetTime() - m_MovementLabHead90MeasureTime >= 500)
            {
                m_MovementLabHead90MeasureTime = GetGame().GetTime();
                vector renderedDirection = GetGame().GetCurrentCameraDirection();
                vector renderedAngles = renderedDirection.VectorToAngles();
                vector bodyAngles = player.GetOrientation();
                float measuredYaw = fixAngle_180_180(renderedAngles[0] - bodyAngles[0]);
                float inputHeading = m_pInput.GetHeadingAngle() * Math.RAD2DEG;
                Print("[MovementLab head90 v63] Camera=" + GetCameraName() + "; shared head limits=" + headLeft + "/" + headRight + "; camera bounds=" + leftLimit + "/" + rightLimit + "; native yaw=" + limitedYaw + "; rendered yaw relative body=" + measuredYaw + "; body world yaw=" + bodyAngles[0] + "; input heading=" + inputHeading);
            }
            return limitedYaw;
        }
        return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, pMin, pMax, pDt);
    }
}
