// Built from v42. Native stationary free-look; camera shares player look limits.
// No heading override, automatic body turn, custom camera matrix or yaw accumulator.
modded class PlayerBase
{
    protected bool m_MovementLabHead90Active;
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
        if (IsRaised() || IsInIronsights() || IsInOptics() || GetInputController().IsWeaponRaised())
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
                Print("[MovementLab head90 v59] Continuous movement/idle pose=" + nextContinuousPose);
            m_MovementLabContinuousHeadPose = nextContinuousPose;
            if (MovementLabCanHead90(pCurrentCommandID))
            {
                if (!m_MovementLabHead90Active)
                {
                    m_MovementLabHead90Active = true;
                    Print("[MovementLab head90 v59] ACTIVE: native free-look, camera shares native player head-look endpoints; no body-turn request.");
                }
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.ONE_FRAME, true);
            }
            else if (m_MovementLabHead90Active)
            {
                GetInputController().OverrideFreeLook(HumanInputControllerOverrideType.DISABLED, false);
                m_MovementLabHead90Active = false;
                Print("[MovementLab head90 v59] RELEASED: native movement/aiming controls.");
            }
        }
        MovementLabUpdateStationaryHeadOnly(pDt);
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
                Print("[MovementLab head90 v59] Camera=" + GetCameraName() + "; shared head limits=" + headLeft + "/" + headRight + "; camera bounds=" + leftLimit + "/" + rightLimit + "; native yaw=" + limitedYaw + "; rendered yaw relative body=" + measuredYaw + "; body world yaw=" + bodyAngles[0] + "; input heading=" + inputHeading);
            }
            return limitedYaw;
        }
        return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, pMin, pMax, pDt);
    }
}
