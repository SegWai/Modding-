// Loaded before the loose mission. Only its offline mission enables the gate.
class MovementLabStartGate
{
    static bool Enabled;
    static bool NativeAimComparison;
}

modded class PlayerBase
{
    protected int m_MovementLabAimReportTime = -1000;
    protected float m_MovementLabAimReportProfile = -1;
    protected int m_MovementLabAimSlowLevel = 2;
    protected int m_MovementLabAimFastLevel = 2;
    protected bool m_MovementLabAimSlowMode = true;
    protected bool m_MovementLabAimShiftSuppressed;
    protected bool m_MovementLabAimBaseSlow = true;
    protected bool m_MovementLabAimShiftDown;
    protected bool m_MovementLabAimCtrlDown;
    protected float m_MovementLabAimFastPoseProfile = 2;
    protected int m_MovementLabAimFastActiveVar = -1;
    protected int m_MovementLabAimFastProfileVar = -1;
    protected int m_MovementLabAimCrouchLevel = 4;
    protected int m_MovementLabAimLastStance = -1;
    protected bool m_MovementLabAimOwnsSpeed;
    protected int m_MovementLabSprintCheckReport = -1000;
    protected float m_MovementLabFullSprintTime;
    protected int m_MovementLabRecentSprintUntil = -1;
    protected float m_MovementLabAimSprintHandoff;
    protected float m_MovementLabAimSprintTime;
    protected bool m_MovementLabAimSessionActive;
    protected bool m_MovementLabAimSessionStanding;
    protected float m_MovementLabAimPoseProfile = 3;
    protected int m_MovementLabAimActiveVar = -1;
    protected int m_MovementLabAimProfileVar = -1;
    protected int m_MovementLabWheelSampleTime = -1;
    protected int m_MovementLabWheelPending;
    protected int m_MovementLabWheelSampleStance = -1;
    protected bool m_MovementLabPoseInitialised;
    protected bool m_MovementLabPoseBindReported;
    protected float m_MovementLabWalkJogPose;
    protected float m_MovementLabJogSprintPose;
    protected float m_MovementLabWalkingPoseLevel = 1;
    protected float m_MovementLabJogRatePose;
    protected float m_MovementLabCrouchPoseLevel = 3;
    protected float m_MovementLabLateralPose = 0.5;
    protected float m_MovementLabLateralActive;
    protected int m_MovementLabAllSmoothActiveVar = -1;
    protected int m_MovementLabWalkJogPoseVar = -1;
    protected int m_MovementLabJogSprintPoseVar = -1;
    protected int m_MovementLabWalkingPoseLevelVar = -1;
    protected int m_MovementLabJogRatePoseVar = -1;
    protected int m_MovementLabCrouchPoseLevelVar = -1;
    protected int m_MovementLabLateralPoseVar = -1;
    protected int m_MovementLabLateralActiveVar = -1;
    protected int m_MovementLabWalkLevelVar = -1;
    protected int m_MovementLabWalkLevel = 1;
    protected int m_MovementLabJogLevel = 2;
    protected bool m_MovementLabScrollSprint;
    protected int m_MovementLabSprintLevel = 2;
    protected bool m_MovementLabWalkBindReported;
    protected int m_MovementLabWalkReportedLevel;
    protected bool m_MovementLabWalkWheelWasCrouching;
    protected bool m_MovementLabStartOwnsSpeed;
    protected bool m_MovementLabIdleArmed;
    protected bool m_MovementLabStarting;
    protected bool m_MovementLabWasInput;
    protected bool m_MovementLabBrakeActive;
    protected float m_MovementLabStartTime;
    protected float m_MovementLabStartSpeed;
    protected bool m_MovementLabWalkMode;
    protected bool m_MovementLabAimSprintExit;
    protected bool m_MovementLabShiftModeDown;
    protected int m_MovementLabShiftClickTime = -1000;
    protected bool m_MovementLabCtrlDown;
    protected float m_MovementLabLastWantedGait = 2.0;
    protected bool m_MovementLabModeDecreasePending;
    protected bool m_MovementLabWasCrouching;
    protected bool m_MovementLabFastCrouch;
    protected bool m_MovementLabCrouchShiftConsumed;

    protected int m_MovementLabSlowLastSide;
    protected float m_MovementLabSlowGap;
    protected float m_MovementLabSlowHeld;
    protected bool m_MovementLabStrafeSlow;

    protected bool m_MovementLabWheelWasCrouching;
    protected bool m_MovementLabWheelStandingSprint;
    protected int m_MovementLabHiddenCrouchVar = -1;
    protected bool m_MovementLabStandingJog1;
    protected int m_MovementLabJogCrouchTarget = 4;
    protected bool m_MovementLabStandingJog2;
    protected bool m_MovementLabJogCrouchFade;
    protected bool m_MovementLabJogCrouchIgnoreShift;
    protected float m_MovementLabJogCrouchTime;
    protected float m_MovementLabJogCrouchGait = 3;
    protected int m_MovementLabCrouchLevel = 4;
    protected int m_MovementLabCrouchLevelVar = -1;
    protected bool m_MovementLabCrouchBindReported;
    protected int m_MovementLabCrouchExitActiveVar = -1;
    protected int m_MovementLabCrouchExitWeightVar = -1;
    protected bool m_MovementLabCrouchExitWasFast;
    protected bool m_MovementLabCrouchExitActive;
    protected float m_MovementLabCrouchExitTime;
    protected float m_MovementLabCrouchExitStart;

    protected void MovementLabLeaveAimForSprint()
    {
        m_MovementLabAimSprintExit = true;
        GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
        GetInputController().OverrideRaise(HumanInputControllerOverrideType.ENABLED, false);
        GetInputController().ResetADS();
        MovementLabCancelAltADS();
        if (GetCommand_Move())
            GetCommand_Move().ForceStance(DayZPlayerConstants.STANCEIDX_ERECT);
        m_MovementLabAimSessionActive = false;
        m_MovementLabAimOwnsSpeed = false;
        m_MovementLabAimSprintTime = 0;
        m_MovementLabWalkMode = false;
        m_MovementLabJogLevel = 3;
        m_MovementLabScrollSprint = true;
        m_MovementLabSprintLevel = 2;
        m_MovementLabModeDecreasePending = false;
        m_MovementLabCrouchShiftConsumed = false;
    }

    protected void MovementLabCaptureStandingModeKeys(bool allowed, int stance)
    {
        bool modeShift = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
        bool modeCtrl = GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05;
        bool modeShiftPress = modeShift && !m_MovementLabShiftModeDown;
        bool modeCtrlPress = modeCtrl && !m_MovementLabCtrlDown;
        m_MovementLabShiftModeDown = modeShift;
        if (m_MovementLabAimSprintExit && !IsRaised() && stance == DayZPlayerConstants.STANCEIDX_ERECT && GetUApi().GetInputByID(UATempRaiseWeapon).LocalValue() <= 0.05)
        {
            GetInputController().OverrideRaise(HumanInputControllerOverrideType.DISABLED, false);
            m_MovementLabAimSprintExit = false;
        }
        if (allowed && IsRaised() && GetInputController())
        {
            if (modeShiftPress)
            {
                if (GetGame().GetTime() - m_MovementLabShiftClickTime <= 250)
                    MovementLabLeaveAimForSprint();
                m_MovementLabShiftClickTime = GetGame().GetTime();
            }
            return;
        }
        if (!allowed || stance != DayZPlayerConstants.STANCEIDX_ERECT)
        {
            m_MovementLabShiftClickTime = -1000;
            return;
        }
        m_MovementLabCtrlDown = modeCtrl;
        if (modeCtrlPress)
        {
            m_MovementLabWalkMode = true;
            m_MovementLabWalkLevel = 1;
            m_MovementLabScrollSprint = false;
            m_MovementLabSprintLevel = 2;
            m_MovementLabShiftClickTime = -1000;
        }
        else if (modeShiftPress)
        {
            bool modeDoubleShift = GetGame().GetTime() - m_MovementLabShiftClickTime <= 250;
            if (m_MovementLabScrollSprint)
                m_MovementLabScrollSprint = false;
            else if (modeDoubleShift)
                m_MovementLabScrollSprint = true;
            else
                m_MovementLabScrollSprint = false;
            m_MovementLabWalkMode = false;
            m_MovementLabJogLevel = 3;
            m_MovementLabSprintLevel = 2;
            m_MovementLabShiftClickTime = GetGame().GetTime();
        }
    }

    void MovementLabCaptureWheelTarget()
    {
        int wheelSampleTime = GetGame().GetTime();
        if (wheelSampleTime == m_MovementLabWheelSampleTime)
            return;
        m_MovementLabWheelSampleTime = wheelSampleTime;
        bool wheelCaptureAllowed = MovementLabStartGate.Enabled && !GetGame().IsMultiplayer();
        if (!GetGame().GetInput().HasGameFocus())
            wheelCaptureAllowed = false;
        if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
            wheelCaptureAllowed = false;
        if (GetGame().GetUIManager().GetMenu())
            wheelCaptureAllowed = false;
        if (GetGame().GetMission())
        {
            if (GetGame().GetMission().IsPaused())
                wheelCaptureAllowed = false;
        }
        HumanMovementState wheelCaptureState = new HumanMovementState();
        GetMovementState(wheelCaptureState);
        MovementLabCaptureStandingModeKeys(wheelCaptureAllowed, wheelCaptureState.m_iStanceIdx);
        if (m_MovementLabWheelSampleStance != wheelCaptureState.m_iStanceIdx)
            m_MovementLabWheelPending = 0;
        m_MovementLabWheelSampleStance = wheelCaptureState.m_iStanceIdx;
        if (!wheelCaptureAllowed)
        {
            m_MovementLabWheelPending = 0;
            return;
        }
        // Action edges are read once by Mission.OnUpdate; raw state can persist
        // across callbacks and must never be counted as another wheel event.
        int wheelUnits = 0;
        if (GetUApi().GetInputByID(UAPrevAction).LocalPress())
            wheelUnits = 1;
        else if (GetUApi().GetInputByID(UANextAction).LocalPress())
            wheelUnits = -1;
        m_MovementLabWheelPending = Math.Clamp(m_MovementLabWheelPending + wheelUnits, -32, 32);
        if (wheelUnits != 0)
        {
            Print("[MovementLab Wheel Target] Action steps=" + wheelUnits);
        }
    }

    protected int MovementLabStandingTargetIndex()
    {
        if (m_MovementLabScrollSprint)
            return 5;
        if (m_MovementLabWalkMode)
            return Math.Clamp(m_MovementLabWalkLevel - 1, 0, 2);
        if (m_MovementLabJogLevel >= 3)
            return 4;
        return 3;
    }

    protected void MovementLabStepStandingTarget(int direction)
    {
        if (m_MovementLabScrollSprint)
            m_MovementLabSprintLevel = Math.Clamp(m_MovementLabSprintLevel + direction, 1, 2);
        else if (m_MovementLabWalkMode)
            m_MovementLabWalkLevel = Math.Clamp(m_MovementLabWalkLevel + direction, 1, 3);
        else
            m_MovementLabJogLevel = Math.Clamp(m_MovementLabJogLevel + direction, 1, 4);
        // Process each notch against selected mode, never reached animation state.
        MovementLabApplyStandingWheelBoundaries();
    }

    protected void MovementLabApplyStandingWheelBoundaries()
    {
        if (m_MovementLabWalkMode && m_MovementLabWalkLevel >= 3)
        {
            // Walking level3 is a mode boundary: native jogging, not a faster walk.
            m_MovementLabWalkLevel = 2;
            m_MovementLabJogLevel = 2;
            m_MovementLabWalkMode = false;
            Print("[MovementLab Linked Wheel] Walk level3 boundary -> jog80%");
        }
        else if (m_MovementLabScrollSprint && m_MovementLabSprintLevel <= 1)
        {
            m_MovementLabScrollSprint = false;
            m_MovementLabSprintLevel = 2;
            m_MovementLabJogLevel = 3;
            m_MovementLabWalkMode = false;
            Print("[MovementLab Linked Wheel] Sprint99% -> jog100%");
        }
        else if (!m_MovementLabWalkMode && !m_MovementLabScrollSprint && m_MovementLabJogLevel <= 1)
        {
            m_MovementLabJogLevel = 2;
            m_MovementLabWalkLevel = 1;
            m_MovementLabWalkMode = true;
            Print("[MovementLab Linked Wheel] Jog79% -> walk73%");
        }
        else if (!m_MovementLabWalkMode && !m_MovementLabScrollSprint)
        {
            if (m_MovementLabJogLevel >= 4)
            {
                m_MovementLabJogLevel = 3;
                m_MovementLabSprintLevel = 2;
                m_MovementLabScrollSprint = true;
                Print("[MovementLab Linked Wheel] Jog101% -> sprint100%");
            }
        }
    }

    protected void MovementLabUpdateStandingWalkWheel(float dt, int command)
    {
        if (m_MovementLabWalkLevelVar < 0 && GetAnimInterface())
            m_MovementLabWalkLevelVar = GetAnimInterface().BindVariableFloat("MovementLabWalkLevel");
        if (!m_MovementLabWalkBindReported)
        {
            Print("[MovementLab Walk Wheel v3] Graph variable binding=" + m_MovementLabWalkLevelVar);
            m_MovementLabWalkBindReported = true;
        }
        HumanMovementState walkWheelState = new HumanMovementState();
        GetMovementState(walkWheelState);
        bool walkWheelCrouching = walkWheelState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH;
        bool walkWheelErect = walkWheelState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
        bool walkWheelReset = m_MovementLabWalkWheelWasCrouching && walkWheelErect;
        if (walkWheelReset)
        {
            m_MovementLabWalkLevel = 1;
            Print("[MovementLab Walk Wheel] Crouch exit: walking level1 80%");
        }
        m_MovementLabWalkWheelWasCrouching = walkWheelCrouching;
        bool walkWheelAllowed = MovementLabCanUseModes(dt, command);
        // One wheel reader owns both standing modes, preventing a boundary
        // crossing from processing the same notch again in the destination mode.
        if (walkWheelAllowed && !walkWheelReset)
        {
            {
                if (m_MovementLabWheelPending != 0)
                {
                    int wheelStandingSteps = Math.AbsInt(m_MovementLabWheelPending);
                    int wheelStandingDirection = 1;
                    if (m_MovementLabWheelPending < 0)
                        wheelStandingDirection = -1;
                    for (int wheelStandingStep = 0; wheelStandingStep < wheelStandingSteps; wheelStandingStep++)
                        MovementLabStepStandingTarget(wheelStandingDirection);
                    Print("[MovementLab Wheel Target] Standing target=" + MovementLabStandingTargetIndex());
                    m_MovementLabWheelPending = 0;
                }
            }
            MovementLabApplyStandingWheelBoundaries();
        }
        if (m_MovementLabWalkLevelVar >= 0)
        {
            // Selector2 is native; erect levels use reversed encoding3/2/1.
            float walkWheelSelected = 2;
            if (MovementLabStartGate.Enabled && !GetGame().IsMultiplayer())
            {
                walkWheelSelected = 4 - m_MovementLabWalkLevel;
                if (m_MovementLabJogLevel == 2)
                    walkWheelSelected = walkWheelSelected + 3;
            }
            AnimSetFloat(m_MovementLabWalkLevelVar, walkWheelSelected);
            if (m_MovementLabWalkReportedLevel != m_MovementLabWalkLevel)
            {
                Print("[MovementLab Walk Wheel v3] Level=" + m_MovementLabWalkLevel + ", graph=" + walkWheelSelected);
                m_MovementLabWalkReportedLevel = m_MovementLabWalkLevel;
            }
        }
    }

    protected void MovementLabUpdateCrouchWheel(float dt, int command)
    {
        if (m_MovementLabCrouchLevelVar < 0 && GetAnimInterface())
            m_MovementLabCrouchLevelVar = GetAnimInterface().BindVariableFloat("MovementLabCrouchLevel");
        if (!m_MovementLabCrouchBindReported)
        {
            Print("[MovementLab Wheel] Graph variable binding=" + m_MovementLabCrouchLevelVar);
            m_MovementLabCrouchBindReported = true;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        bool wheelCrouching = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH;
        if (!wheelCrouching)
        {
            m_MovementLabJogCrouchFade = false;
            m_MovementLabStandingJog1 = !IsRaised() && !m_MovementLabWalkMode && !m_MovementLabScrollSprint && m_MovementLabJogLevel == 2;
            m_MovementLabStandingJog2 = !IsRaised() && !m_MovementLabWalkMode && !m_MovementLabScrollSprint && m_MovementLabJogLevel >= 3;
            if (state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT || !GetCommand_Move())
            {
                m_MovementLabStandingJog2 = false;
                m_MovementLabStandingJog1 = false;
            }
            else if (GetCommand_Move().GetCurrentMovementSpeed() < 1.7)
            {
                m_MovementLabStandingJog2 = false;
                m_MovementLabStandingJog1 = false;
            }
            // Do not mistake the first upright sample of fast crouch for
            // full standing sprint. Transition commands retain prior evidence.
            if (m_MovementLabWheelWasCrouching || state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT)
                m_MovementLabWheelStandingSprint = false;
            else if (command == DayZPlayerConstants.COMMANDID_MOVE && GetCommand_Move())
                m_MovementLabWheelStandingSprint = GetCommand_Move().GetCurrentMovementSpeed() >= 2.90;
        }
        else if (!m_MovementLabWheelWasCrouching)
        {
            m_MovementLabCrouchLevel = 4;
            bool crouchEntryMoving = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05;
            if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
                crouchEntryMoving = true;
            if (!crouchEntryMoving)
            {
                m_MovementLabStandingJog1 = false;
                m_MovementLabStandingJog2 = false;
                m_MovementLabWheelStandingSprint = false;
            }
            if (m_MovementLabWheelStandingSprint || m_MovementLabStandingJog2 || m_MovementLabStandingJog1)
            {
                m_MovementLabJogCrouchTarget = 4;
                m_MovementLabCrouchLevel = 7;
                if (!m_MovementLabWheelStandingSprint && m_MovementLabStandingJog1)
                {
                    m_MovementLabJogCrouchTarget = 4;
                    m_MovementLabCrouchLevel = 8;
                }
                m_MovementLabCrouchPoseLevel = 5;
                m_MovementLabJogCrouchFade = true;
                m_MovementLabJogCrouchTime = 0;
                m_MovementLabJogCrouchGait = 3;
                m_MovementLabJogCrouchIgnoreShift = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
                Print("[MovementLab Momentum Fade] Hidden entry=" + m_MovementLabCrouchLevel + ", target=" + m_MovementLabJogCrouchTarget + ", duration1.5s");
            }
            Print("[MovementLab Crouch Entry] Default level=" + m_MovementLabCrouchLevel);
            if (!m_MovementLabJogCrouchFade)
            {
                MessageStatus("Crouch speed level " + m_MovementLabCrouchLevel + "/5");
            }
        }
        if (m_MovementLabJogCrouchFade)
        {
            m_MovementLabWheelPending = 0;
            if (GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05)
                m_MovementLabJogCrouchIgnoreShift = true;
            if (m_MovementLabJogCrouchTime > 0)
                m_MovementLabCrouchLevel = m_MovementLabJogCrouchTarget;
        }
        if (GetUApi().GetInputByID(UATurbo).LocalValue() <= 0.05)
            m_MovementLabJogCrouchIgnoreShift = false;
        m_MovementLabWheelWasCrouching = wheelCrouching;
        if (MovementLabCrouchAllowed(dt, command) && state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH)
        {
            if (m_MovementLabWheelPending != 0)
            {
                m_MovementLabCrouchLevel = Math.Clamp(m_MovementLabCrouchLevel + m_MovementLabWheelPending, 1, 5);
                m_MovementLabWheelPending = 0;
                Print("[MovementLab Wheel Target] Crouch target=" + m_MovementLabCrouchLevel);
            }
        }
        if (m_MovementLabCrouchLevelVar >= 0)
        {
            float selected = m_MovementLabCrouchLevel;
            if (m_MovementLabJogCrouchFade)
                selected = m_MovementLabJogCrouchTarget;
            if (selected >= 4)
                selected = selected + 1;
            if (GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05 && !m_MovementLabJogCrouchIgnoreShift && !m_MovementLabJogCrouchFade)
                selected = 6;
            AnimSetFloat(m_MovementLabCrouchLevelVar, selected);
        }
    }

    protected bool MovementLabUpdateJogCrouchFade(float dt, int command)
    {
        if (!m_MovementLabJogCrouchFade)
            return false;
        HumanMovementState fadeState = new HumanMovementState();
        GetMovementState(fadeState);
        bool fadeMoving = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            fadeMoving = true;
        if (!MovementLabCrouchAllowed(dt, command) || fadeState.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_CROUCH || !fadeMoving)
        {
            m_MovementLabJogCrouchFade = false;
            m_MovementLabCrouchLevel = m_MovementLabJogCrouchTarget;
            m_MovementLabCrouchExitActive = false;
            m_MovementLabCrouchExitWasFast = false;
            return false;
        }
        float fadeFraction = Math.Clamp(m_MovementLabJogCrouchTime / 1.5, 0, 1);
        float fadeBlend = fadeFraction * fadeFraction;
        fadeBlend = fadeBlend * (3 - 2 * fadeFraction);
        float fadeWeight = 1 - fadeBlend;
        m_MovementLabJogCrouchGait = 1 + 2 * fadeWeight;
        m_MovementLabCrouchExitActive = false;
        m_MovementLabCrouchExitWasFast = false;
        m_MovementLabJogCrouchTime = m_MovementLabJogCrouchTime + dt;
        if (m_MovementLabJogCrouchTime >= 1.5)
        {
            m_MovementLabJogCrouchFade = false;
            m_MovementLabCrouchLevel = m_MovementLabJogCrouchTarget;
            m_MovementLabJogCrouchGait = 1;
            fadeWeight = 0;
        }
        if (m_MovementLabCrouchExitActiveVar >= 0)
            AnimSetFloat(m_MovementLabCrouchExitActiveVar, 1);
        if (m_MovementLabCrouchExitWeightVar >= 0)
            AnimSetFloat(m_MovementLabCrouchExitWeightVar, fadeWeight);
        return true;
    }

    protected void MovementLabUpdateCrouchPoseExit(float dt, int command)
    {
        if (GetAnimInterface())
        {
            if (m_MovementLabHiddenCrouchVar < 0)
                m_MovementLabHiddenCrouchVar = GetAnimInterface().BindVariableFloat("MovementLabHiddenCrouch95");
            if (m_MovementLabHiddenCrouchVar >= 0)
            {
                float hiddenCrouchActive = 0;
                if (m_MovementLabJogCrouchFade)
                    hiddenCrouchActive = 1;
                AnimSetFloat(m_MovementLabHiddenCrouchVar, hiddenCrouchActive);
            }
            if (m_MovementLabCrouchExitActiveVar < 0)
                m_MovementLabCrouchExitActiveVar = GetAnimInterface().BindVariableFloat("MovementLabCrouchExitActive");
            if (m_MovementLabCrouchExitWeightVar < 0)
                m_MovementLabCrouchExitWeightVar = GetAnimInterface().BindVariableFloat("MovementLabCrouchExitWeight");
        }
        if (MovementLabUpdateJogCrouchFade(dt, command))
            return;
        HumanMovementState poseExitState = new HumanMovementState();
        GetMovementState(poseExitState);
        bool poseExitAllowed = MovementLabCrouchAllowed(dt, command);
        if (poseExitState.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_CROUCH)
            poseExitAllowed = false;
        bool poseExitMoving = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05;
        if (GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05)
            poseExitMoving = true;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            poseExitMoving = true;
        bool poseExitFast = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05 && !m_MovementLabJogCrouchIgnoreShift;
        if (m_MovementLabCrouchLevel == 5)
            poseExitFast = true;
        if (!poseExitAllowed || !poseExitMoving)
        {
            m_MovementLabCrouchExitActive = false;
            m_MovementLabCrouchExitWasFast = false;
        }
        else
        {
            if (poseExitFast || m_MovementLabCrouchLevel >= 5)
                m_MovementLabCrouchExitActive = false;
            if (!poseExitFast && m_MovementLabCrouchLevel <= 4)
            {
                if (m_MovementLabCrouchExitWasFast && GetCommand_Move().GetCurrentMovementSpeed() > 2.05)
                {
                    m_MovementLabCrouchExitStart = Math.Clamp(GetCommand_Move().GetCurrentMovementSpeed() - 2.0, 0, 1);
                    m_MovementLabCrouchExitTime = 0;
                    m_MovementLabCrouchExitActive = true;
                    Print("[MovementLab Pose Exit] Fast ->87 pose blend started");
                }
            }
            m_MovementLabCrouchExitWasFast = poseExitFast;
        }
        float poseExitWeight = 0;
        float poseExitActiveValue = 0;
        if (m_MovementLabCrouchExitActive)
        {
            float poseExitFraction = Math.Clamp(m_MovementLabCrouchExitTime / 0.55, 0, 1);
            poseExitFraction = poseExitFraction * poseExitFraction * (3.0 - 2.0 * poseExitFraction);
            poseExitWeight = m_MovementLabCrouchExitStart * (1.0 - poseExitFraction);
            poseExitActiveValue = 1;
            if (m_MovementLabCrouchExitTime >= 0.55)
            {
                m_MovementLabCrouchExitActive = false;
                poseExitActiveValue = 0;
                Print("[MovementLab Pose Exit] Pose blend complete");
            }
            m_MovementLabCrouchExitTime = m_MovementLabCrouchExitTime + dt;
        }
        if (m_MovementLabCrouchExitActiveVar >= 0)
            AnimSetFloat(m_MovementLabCrouchExitActiveVar, poseExitActiveValue);
        if (m_MovementLabCrouchExitWeightVar >= 0)
            AnimSetFloat(m_MovementLabCrouchExitWeightVar, poseExitWeight);
    }

    protected void MovementLabUpdateAllPoseSmoothing(float dt, int command)
    {
        bool poseAllowed = MovementLabStartGate.Enabled && !GetGame().IsMultiplayer();
        if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
            poseAllowed = false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
            poseAllowed = false;
        if (dt <= 0 || dt > 0.25)
            poseAllowed = false;
        if (GetGame().GetUIManager().GetMenu())
            poseAllowed = false;
        if (GetGame().GetMission())
        {
            if (GetGame().GetMission().IsPaused())
                poseAllowed = false;
        }
        float poseGait = 0;
        float poseAngle = 0;
        if (GetCommand_Move())
        {
            poseGait = GetCommand_Move().GetCurrentMovementSpeed();
            poseAngle = GetCommand_Move().GetCurrentMovementAngle();
        }
        float poseWalkJogTarget = Math.Clamp(poseGait - 1.0, 0, 1);
        // Ease the pose weight endpoints only for the slow-jog return to walking.
        // Gait requests, physical momentum budget and profile speeds are unchanged.
        if (m_MovementLabWalkMode && m_MovementLabJogLevel == 2)
            poseWalkJogTarget = poseWalkJogTarget * poseWalkJogTarget * (3.0 - 2.0 * poseWalkJogTarget);
        float poseJogSprintTarget = Math.Clamp(poseGait - 2.0, 0, 1);
        float poseWalkingTarget = m_MovementLabWalkLevel;
        float poseJogRateTarget = 1;
        if (m_MovementLabJogLevel == 2)
            poseJogRateTarget = 0;
        float poseCrouchTarget = Math.Clamp(m_MovementLabCrouchLevel, 1, 5);
        if (m_MovementLabCrouchLevel >= 4)
            poseCrouchTarget = 5;
        if (m_MovementLabCrouchExitActive)
            poseCrouchTarget = 5;
        float poseSideTarget = Math.Clamp((poseAngle + 90.0) / 180.0, 0, 1);
        float poseSideActiveTarget = 0;
        if (Math.AbsFloat(poseAngle) >= 65 && Math.AbsFloat(poseAngle) <= 115)
            poseSideActiveTarget = 1;
        if (!poseAllowed || !m_MovementLabPoseInitialised)
        {
            m_MovementLabWalkJogPose = poseWalkJogTarget;
            m_MovementLabJogSprintPose = poseJogSprintTarget;
            m_MovementLabWalkingPoseLevel = poseWalkingTarget;
            m_MovementLabJogRatePose = poseJogRateTarget;
            m_MovementLabCrouchPoseLevel = poseCrouchTarget;
            m_MovementLabLateralPose = poseSideTarget;
            m_MovementLabLateralActive = 0;
            m_MovementLabPoseInitialised = poseAllowed;
        }
        else
        {
            float poseStep = Math.Clamp(dt / 0.16, 0, 1);
            float poseProfileStep = Math.Clamp(dt / 0.20, 0, 1);
            float walkPoseNext = m_MovementLabWalkJogPose + (poseWalkJogTarget - m_MovementLabWalkJogPose) * poseStep;
            // Bound the visible pose handoff even if native achieved gait drops sharply.
            // Only walking returns: no changes to acceleration, speed requests or wheel input.
            if (m_MovementLabWalkMode && walkPoseNext < m_MovementLabWalkJogPose)
            {
                float walkPoseMinimum = m_MovementLabWalkJogPose - Math.Max(dt, 0) / 0.45;
                walkPoseNext = Math.Max(walkPoseNext, walkPoseMinimum);
            }
            m_MovementLabWalkJogPose = Math.Clamp(walkPoseNext, 0, 1);
            m_MovementLabJogSprintPose = m_MovementLabJogSprintPose + (poseJogSprintTarget - m_MovementLabJogSprintPose) * poseStep;
            m_MovementLabWalkingPoseLevel = m_MovementLabWalkingPoseLevel + (poseWalkingTarget - m_MovementLabWalkingPoseLevel) * poseProfileStep;
            m_MovementLabJogRatePose = m_MovementLabJogRatePose + (poseJogRateTarget - m_MovementLabJogRatePose) * poseProfileStep;
            m_MovementLabCrouchPoseLevel = m_MovementLabCrouchPoseLevel + (poseCrouchTarget - m_MovementLabCrouchPoseLevel) * poseProfileStep;
            m_MovementLabLateralPose = m_MovementLabLateralPose + (poseSideTarget - m_MovementLabLateralPose) * poseStep;
            m_MovementLabLateralActive = m_MovementLabLateralActive + (poseSideActiveTarget - m_MovementLabLateralActive) * poseStep;
        }
        float poseActive = 0;
        if (poseAllowed)
            poseActive = 1;
        if (m_MovementLabAllSmoothActiveVar < 0 && GetAnimInterface())
            m_MovementLabAllSmoothActiveVar = GetAnimInterface().BindVariableFloat("MovementLabAllSmoothActive");
        if (m_MovementLabWalkJogPoseVar < 0 && GetAnimInterface())
            m_MovementLabWalkJogPoseVar = GetAnimInterface().BindVariableFloat("MovementLabWalkJogPose");
        if (m_MovementLabJogSprintPoseVar < 0 && GetAnimInterface())
            m_MovementLabJogSprintPoseVar = GetAnimInterface().BindVariableFloat("MovementLabJogSprintPose");
        if (m_MovementLabWalkingPoseLevelVar < 0 && GetAnimInterface())
            m_MovementLabWalkingPoseLevelVar = GetAnimInterface().BindVariableFloat("MovementLabWalkingPoseLevel");
        if (m_MovementLabJogRatePoseVar < 0 && GetAnimInterface())
            m_MovementLabJogRatePoseVar = GetAnimInterface().BindVariableFloat("MovementLabJogRatePose");
        if (m_MovementLabCrouchPoseLevelVar < 0 && GetAnimInterface())
            m_MovementLabCrouchPoseLevelVar = GetAnimInterface().BindVariableFloat("MovementLabCrouchPoseLevel");
        if (m_MovementLabLateralPoseVar < 0 && GetAnimInterface())
            m_MovementLabLateralPoseVar = GetAnimInterface().BindVariableFloat("MovementLabLateralPose");
        if (m_MovementLabLateralActiveVar < 0 && GetAnimInterface())
            m_MovementLabLateralActiveVar = GetAnimInterface().BindVariableFloat("MovementLabLateralActive");
        if (!m_MovementLabPoseBindReported)
        {
            Print("[MovementLab All Poses] Active binding=" + m_MovementLabAllSmoothActiveVar);
            Print("[MovementLab All Poses] Walk/jog binding=" + m_MovementLabWalkJogPoseVar);
            Print("[MovementLab All Poses] Jog/sprint binding=" + m_MovementLabJogSprintPoseVar);
            m_MovementLabPoseBindReported = true;
        }
        if (m_MovementLabAllSmoothActiveVar >= 0)
            AnimSetFloat(m_MovementLabAllSmoothActiveVar, poseActive);
        if (m_MovementLabWalkJogPoseVar >= 0)
            AnimSetFloat(m_MovementLabWalkJogPoseVar, m_MovementLabWalkJogPose);
        if (m_MovementLabJogSprintPoseVar >= 0)
            AnimSetFloat(m_MovementLabJogSprintPoseVar, m_MovementLabJogSprintPose);
        if (m_MovementLabWalkingPoseLevelVar >= 0)
            AnimSetFloat(m_MovementLabWalkingPoseLevelVar, m_MovementLabWalkingPoseLevel);
        if (m_MovementLabJogRatePoseVar >= 0)
            AnimSetFloat(m_MovementLabJogRatePoseVar, m_MovementLabJogRatePose);
        if (m_MovementLabCrouchPoseLevelVar >= 0)
            AnimSetFloat(m_MovementLabCrouchPoseLevelVar, m_MovementLabCrouchPoseLevel);
        if (m_MovementLabLateralPoseVar >= 0)
            AnimSetFloat(m_MovementLabLateralPoseVar, m_MovementLabLateralPose);
        if (m_MovementLabLateralActiveVar >= 0)
            AnimSetFloat(m_MovementLabLateralActiveVar, m_MovementLabLateralActive);
    }

    void MovementLabCancelStart()
    {
        if (m_MovementLabStartOwnsSpeed && GetInputController())
            GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
        m_MovementLabStartOwnsSpeed = false;
        m_MovementLabIdleArmed = false;
        m_MovementLabStarting = false;
        m_MovementLabStartTime = 0;
    }

    void MovementLabSetBrakingActive(bool active)
    {
        if (active)
        {
            MovementLabCancelStart();
            m_MovementLabModeDecreasePending = false;
        }
        m_MovementLabBrakeActive = active;
    }

    // Called before both command and mission movement processing. The
    // standing v4 path is untouched unless a crouch exit must select its mode.
    bool MovementLabUpdateCrouchRules(float dt, int command)
    {
        if (m_MovementLabAimSprintExit)
        {
            m_MovementLabWasCrouching = false;
            m_MovementLabFastCrouch = false;
            return false;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        bool crouching = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH;
        if (!crouching && !m_MovementLabWasCrouching)
            return false;
        if (!MovementLabCrouchAllowed(dt, command))
        {
            m_MovementLabWasCrouching = false;
            m_MovementLabFastCrouch = false;
            m_MovementLabCrouchShiftConsumed = false;
            return false;
        }
        bool moving = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            moving = true;
        bool shift = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05 && !m_MovementLabJogCrouchIgnoreShift;
        if (crouching && m_MovementLabCrouchLevel == 5)
            shift = true;
        if (crouching)
        {
            m_MovementLabScrollSprint = false;
            m_MovementLabSprintLevel = 2;
            MovementLabCancelStart();
            m_MovementLabModeDecreasePending = false;
            m_MovementLabWasInput = false;
            m_MovementLabWasCrouching = true;
            // Current crouch state, not an "ever used Shift" latch.
            if (moving && m_MovementLabJogCrouchFade)
            {
                m_MovementLabFastCrouch = true;
                m_MovementLabStartOwnsSpeed = true;
                GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, m_MovementLabJogCrouchGait);
                return true;
            }
            m_MovementLabFastCrouch = shift && moving;
            m_MovementLabCrouchShiftConsumed = false;
            m_MovementLabLastWantedGait = MovementLabWantedGait();
            if (moving && !shift)
            {
                // Slow crouch uses the saved wheel level. Held Shift is
                // explicitly fast below, independent of native input filtering.
                m_MovementLabStartOwnsSpeed = true;
                GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 1.0);
            }
            if (moving && shift)
            {
                m_MovementLabStartOwnsSpeed = true;
                GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 3.0);
            }
            return true;
        }
        if (state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT)
        {
            if (m_MovementLabFastCrouch)
            {
                m_MovementLabWalkMode = false;
                // The SAME Shift hold used for crouch must not become an
                // upright sprint. Release it before requesting sprint again.
                m_MovementLabCrouchShiftConsumed = shift;
            }
            // Slow crouch preserves m_MovementLabWalkMode (rule 4).
            m_MovementLabLastWantedGait = MovementLabWantedGait();
            m_MovementLabModeDecreasePending = false;
            m_MovementLabWasInput = moving;
        }
        m_MovementLabWasCrouching = false;
        m_MovementLabFastCrouch = false;
        return false;
    }

    protected bool MovementLabCrouchAllowed(float dt, int command)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer())
            return false;
        if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
            return false;
        if (IsRaised() || IsEmotePlaying())
            return false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
            return false;
        if (!GetInputController() || dt > 0.25)
            return false;
        if (GetGame().GetUIManager().GetMenu())
            return false;
        if (GetGame().GetMission())
        {
            if (GetGame().GetMission().IsPaused())
                return false;
        }
        return true;
    }

    bool MovementLabIsStarting()
    {
        return m_MovementLabStarting;
    }

    float MovementLabGetStartSpeed()
    {
        return m_MovementLabStartSpeed;
    }

    bool MovementLabIsScrollSprinting()
    {
        return m_MovementLabScrollSprint;
    }

    bool MovementLabIsModeDecreasePending()
    {
        return m_MovementLabModeDecreasePending;
    }

    float MovementLabBaseGait()
    {
        if (m_MovementLabWalkMode)
            return 1.0;
        return 2.0;
    }

    float MovementLabWantedGait()
    {
        if (m_MovementLabScrollSprint)
            return 3.0;
        return MovementLabBaseGait();
    }

    protected bool MovementLabCanUseModes(float dt, int command)
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer())
            return false;
        if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
            return false;
        if (IsRaised() || IsEmotePlaying())
            return false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move())
            return false;
        if (!GetInputController() || dt > 0.25)
            return false;
        if (GetGame().GetUIManager().GetMenu())
            return false;
        if (GetGame().GetMission())
        {
            if (GetGame().GetMission().IsPaused())
                return false;
        }
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        return state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
    }

    protected void MovementLabCommandStart(float dt, int command)
    {
        bool ctrl = GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05;
        bool press = ctrl && !m_MovementLabCtrlDown;
        m_MovementLabCtrlDown = ctrl;
        if (MovementLabUpdateCrouchRules(dt, command))
            return;
        if (!MovementLabCanUseModes(dt, command))
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = false;
            m_MovementLabModeDecreasePending = false;
            m_MovementLabLastWantedGait = MovementLabWantedGait();
            return;
        }
        float wanted = MovementLabWantedGait();
        float previousWanted = m_MovementLabLastWantedGait;
        m_MovementLabLastWantedGait = wanted;
        if (wanted < previousWanted)
            m_MovementLabModeDecreasePending = true;
        bool movingInput = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05;
        HumanInputController input = GetInputController();
        // Retain v11's single braking owner in the mission.
        if (m_MovementLabBrakeActive)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = movingInput;
            return;
        }
        float achieved = GetCommand_Move().GetCurrentMovementSpeed();
        if (!movingInput)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = false;
            m_MovementLabModeDecreasePending = false;
            if (achieved <= 0.1)
            {
                m_MovementLabIdleArmed = true;
                m_MovementLabStartOwnsSpeed = true;
                input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 0);
            }
            return;
        }
        if (m_MovementLabModeDecreasePending && wanted < achieved - 0.05)
        {
            // Hold current gait until the mission starts its timed slowdown.
            // Never emit one walking frame ahead of the brake controller.
            MovementLabCancelStart();
            m_MovementLabWasInput = true;
            m_MovementLabStartOwnsSpeed = true;
            input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, achieved);
            return;
        }
        m_MovementLabModeDecreasePending = false;
        if (wanted == 1.0)
        {
            MovementLabCancelStart();
            m_MovementLabWasInput = true;
            m_MovementLabStartOwnsSpeed = true;
            input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 1.0);
            return;
        }
        if (!m_MovementLabStarting)
        {
            if (m_MovementLabIdleArmed || (!m_MovementLabWasInput && achieved <= 0.1))
            {
                m_MovementLabStarting = true;
                m_MovementLabIdleArmed = false;
                m_MovementLabStartTime = 0;
            }
            else if (previousWanted == 1.0 && wanted > 1.0 && achieved < 1.75)
            {
                // Only a real walk-to-jog/sprint MODE change starts this blend.
                // Native turn/backward gait dips must not restart it each cycle.
                m_MovementLabStarting = true;
                m_MovementLabStartTime = 0.10;
            }
        }
        m_MovementLabWasInput = true;
        if (m_MovementLabStarting && m_MovementLabStartTime < 0.35)
        {
            float blend = Math.Clamp((m_MovementLabStartTime - 0.10) / 0.18, 0, 1);
            blend = blend * blend * (3.0 - 2.0 * blend);
            m_MovementLabStartSpeed = 1.0 + blend;
            m_MovementLabStartOwnsSpeed = true;
            input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, m_MovementLabStartSpeed);
            m_MovementLabStartTime = m_MovementLabStartTime + Math.Max(dt, 0);
            return;
        }
        if (m_MovementLabStarting)
            MovementLabCancelStart();
        // Persistent mode ownership replaces Ctrl-hold with Ctrl-toggle.
        m_MovementLabStartOwnsSpeed = true;
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, wanted);
    }

    protected void MovementLabUpdateStrafeSlow(float dt, int command)
    {
        if (!MovementLabCanUseModes(dt, command) || MovementLabWantedGait() < 2.0)
        {
            m_MovementLabSlowLastSide = 0;
            m_MovementLabStrafeSlow = false;
            m_MovementLabSlowHeld = 0;
            m_MovementLabSlowGap = 0;
            return;
        }
        bool left = GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05;
        bool right = GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05;
        bool longitudinal = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05;
        float step = Math.Max(dt, 0);
        int side = 0;
        if (left && !right)
            side = -1;
        else if (right && !left)
            side = 1;
        if (longitudinal)
        {
            m_MovementLabStrafeSlow = false;
            m_MovementLabSlowLastSide = 0;
            return;
        }
        if (side == 0)
        {
            m_MovementLabSlowHeld = 0;
            m_MovementLabSlowGap = m_MovementLabSlowGap + step;
            if (!left && !right)
                m_MovementLabStrafeSlow = false;
            if (m_MovementLabSlowGap > 0.18)
                m_MovementLabSlowLastSide = 0;
            if (left && right && m_MovementLabStrafeSlow && !m_MovementLabBrakeActive)
                GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 0.15);
            return;
        }
        bool reversed = m_MovementLabSlowLastSide != 0 && side != m_MovementLabSlowLastSide;
        if (reversed)
        {
            m_MovementLabStrafeSlow = true;
            m_MovementLabSlowHeld = 0;
        }
        else
            m_MovementLabSlowHeld = m_MovementLabSlowHeld + step;
        m_MovementLabSlowLastSide = side;
        m_MovementLabSlowGap = 0;
        if (!m_MovementLabStrafeSlow || m_MovementLabBrakeActive)
            return;
        MovementLabApplyStrafeSlow();
    }

    void MovementLabApplyStrafeSlow()
    {
        if (!m_MovementLabStrafeSlow || m_MovementLabBrakeActive)
            return;
        // Near-stop movement, never a frozen pose or angle override.
        // A fresh reversal resets ONLY stable-hold age, keeping speed low.
        float blend = Math.Clamp((m_MovementLabSlowHeld - 0.30) / 0.08, 0, 1);
        blend = blend * blend * (3.0 - 2.0 * blend);
        m_MovementLabStartOwnsSpeed = true;
        float gait = 0.15 + (MovementLabWantedGait() - 0.15) * blend;
        GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, gait);
        if (blend >= 1)
            m_MovementLabStrafeSlow = false;
    }

    void MovementLabApplyAimWalkingSpeed()
    {
        if (!m_MovementLabAimOwnsSpeed || !GetInputController())
            return;
        bool aimMoving = GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05 || GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            aimMoving = true;
        float aimGait = 0;
        if (aimMoving)
        {
            aimGait = 1;
            bool speedCrouching = m_MovementLabAimLastStance == DayZPlayerConstants.STANCEIDX_CROUCH || m_MovementLabAimLastStance == DayZPlayerConstants.STANCEIDX_RAISEDCROUCH;
            if (!speedCrouching && !m_MovementLabAimSlowMode)
                aimGait = 2;
        }
        GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, aimGait);
    }

    protected void MovementLabStepLinkedAim(int direction)
    {
        if (m_MovementLabAimSlowMode)
            m_MovementLabAimSlowLevel = Math.Clamp(m_MovementLabAimSlowLevel + direction, 1, 3);
        else
            m_MovementLabAimFastLevel = Math.Clamp(m_MovementLabAimFastLevel + direction, 1, 3);
    }

    protected bool MovementLabUpdateAimWalking(float dt, int command)
    {
        if (m_MovementLabAimActiveVar < 0 && GetAnimInterface())
            m_MovementLabAimActiveVar = GetAnimInterface().BindVariableFloat("MovementLabAimWalkActive");
        if (m_MovementLabAimProfileVar < 0 && GetAnimInterface())
            m_MovementLabAimProfileVar = GetAnimInterface().BindVariableFloat("MovementLabAimWalkProfile");
        if (m_MovementLabAimFastActiveVar < 0 && GetAnimInterface())
            m_MovementLabAimFastActiveVar = GetAnimInterface().BindVariableFloat("MovementLabAimFastActive");
        if (m_MovementLabAimFastProfileVar < 0 && GetAnimInterface())
            m_MovementLabAimFastProfileVar = GetAnimInterface().BindVariableFloat("MovementLabAimFastProfile");
        HumanMovementState aimState = new HumanMovementState();
        GetMovementState(aimState);
        // Qualify only sustained achieved full sprint, never a selected sprint target.
        if (!IsRaised())
        {
            bool aimFullSprint = MovementLabStartGate.Enabled && !GetGame().IsMultiplayer();
            if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious() || IsEmotePlaying())
                aimFullSprint = false;
            if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move() || dt <= 0 || dt > 0.25)
                aimFullSprint = false;
            if (aimState.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT && aimState.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_RAISEDERECT)
                aimFullSprint = false;
            if (GetGame().GetUIManager().GetMenu() || GetGame().GetMission().IsPaused())
                aimFullSprint = false;
            if (aimFullSprint && GetCommand_Move().GetCurrentMovementSpeed() >= 2.7)
            {
                m_MovementLabFullSprintTime = Math.Min(1.01, m_MovementLabFullSprintTime + dt);
                if (m_MovementLabFullSprintTime >= 0.35)
                    m_MovementLabRecentSprintUntil = GetGame().GetTime() + 1000;
            }
            else
            {
                m_MovementLabFullSprintTime = 0;
                m_MovementLabRecentSprintUntil = -1;
            }
        }
        else
            m_MovementLabFullSprintTime = 0;
        if (!IsRaised() && GetCommand_Move() && GetGame().GetPlayer() == this && GetGame().GetTime() - m_MovementLabSprintCheckReport >= 500)
        {
            m_MovementLabSprintCheckReport = GetGame().GetTime();
            Print("[MovementLab SprintGate rev17] Achieved=" + GetCommand_Move().GetCurrentMovementSpeed() + ", duration=" + m_MovementLabFullSprintTime + ", qualified until=" + m_MovementLabRecentSprintUntil);
        }
        if (IsRaised())
        {
            if (m_MovementLabJogCrouchFade)
                m_MovementLabCrouchLevel = m_MovementLabJogCrouchTarget;
            m_MovementLabJogCrouchFade = false;
            if (m_MovementLabHiddenCrouchVar >= 0)
                AnimSetFloat(m_MovementLabHiddenCrouchVar, 0);
            if (m_MovementLabCrouchExitActiveVar >= 0)
                AnimSetFloat(m_MovementLabCrouchExitActiveVar, 0);
        }
        bool aimAllowed = MovementLabStartGate.Enabled && !GetGame().IsMultiplayer() && !m_MovementLabAimSprintExit;
        if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious() || !IsRaised() || IsEmotePlaying())
            aimAllowed = false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || !GetCommand_Move() || !GetInputController() || dt > 0.25)
            aimAllowed = false;
        bool aimStandingStance = aimState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || aimState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
        bool aimCrouchStance = aimState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH || aimState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDCROUCH;
        if (!aimStandingStance && !aimCrouchStance)
            aimAllowed = false;
        if (GetGame().GetUIManager().GetMenu())
            aimAllowed = false;
        if (GetGame().GetMission())
        {
            if (GetGame().GetMission().IsPaused())
                aimAllowed = false;
        }
        if (!aimAllowed)
        {
            if (m_MovementLabAimSessionActive && !IsRaised())
            {
                if (m_MovementLabAimSessionStanding)
                {
                    m_MovementLabWalkMode = m_MovementLabAimSlowMode;
                    m_MovementLabWalkLevel = 1;
                    m_MovementLabJogLevel = 2;
                    if (!m_MovementLabAimSlowMode && m_MovementLabAimFastLevel >= 2)
                        m_MovementLabJogLevel = 3;
                    m_MovementLabScrollSprint = false;
                    m_MovementLabSprintLevel = 2;
                    m_MovementLabCrouchShiftConsumed = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
                }
                m_MovementLabAimSprintTime = 0;
                m_MovementLabAimSessionActive = false;
            }
            if (IsRaised() && GetGame().GetTime() - m_MovementLabAimReportTime >= 1000)
            {
                m_MovementLabAimReportTime = GetGame().GetTime();
                Print("[MovementLab AimWalk] Ineligible command=" + command + ", stance=" + aimState.m_iStanceIdx);
            }
            if (m_MovementLabAimOwnsSpeed && GetInputController())
                GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
            m_MovementLabAimOwnsSpeed = false;
            m_MovementLabAimLastStance = -1;
            if (m_MovementLabAimActiveVar >= 0)
                AnimSetFloat(m_MovementLabAimActiveVar, 0);
            if (m_MovementLabAimFastActiveVar >= 0)
                AnimSetFloat(m_MovementLabAimFastActiveVar, 0);
            return false;
        }
        bool aimCrouching = aimCrouchStance;
        bool aimEntering = !m_MovementLabAimOwnsSpeed || m_MovementLabAimLastStance != aimState.m_iStanceIdx;
        if (aimEntering)
        {
            MovementLabCancelStart();
            if (aimCrouching)
            {
                m_MovementLabAimSprintTime = 0;
                m_MovementLabAimFastLevel = Math.Clamp(m_MovementLabAimFastLevel, 1, 3);
                m_MovementLabAimCrouchLevel = 4;
            }
            else
            {
                if (!m_MovementLabAimSessionActive || !m_MovementLabAimSessionStanding)
                {
                    bool aimFromSprint = m_MovementLabScrollSprint;
                    m_MovementLabAimBaseSlow = m_MovementLabWalkMode && !aimFromSprint;
                    m_MovementLabAimSlowMode = m_MovementLabAimBaseSlow;
                    m_MovementLabAimSlowLevel = Math.Clamp(m_MovementLabWalkLevel + 1, 2, 3);
                    m_MovementLabAimFastLevel = 1;
                    if (m_MovementLabJogLevel >= 3)
                        m_MovementLabAimFastLevel = 2;
                    bool aimProjectileWeapon = GetItemInHands() && GetItemInHands().IsWeapon();
                    bool aimRecentSprint = GetGame().GetTime() <= m_MovementLabRecentSprintUntil;
                    if (aimProjectileWeapon && aimRecentSprint)
                    {
                        m_MovementLabAimBaseSlow = false;
                        m_MovementLabAimSlowMode = false;
                        m_MovementLabAimFastLevel = 4;
                        m_MovementLabAimSprintTime = 1.5;
                        m_MovementLabAimSprintHandoff = 0.25;
                    }
                    m_MovementLabRecentSprintUntil = -1;
                    Print("[MovementLab AimGate rev17] Recent qualified sprint=" + aimRecentSprint + ", projectile weapon=" + aimProjectileWeapon + ", stance=" + aimState.m_iStanceIdx);
                    Print("[MovementLab AimEntry rev17] Jog internal level=" + m_MovementLabJogLevel + ", selected fast aim level=" + m_MovementLabAimFastLevel);
                    m_MovementLabAimShiftDown = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
                    m_MovementLabAimShiftSuppressed = false;
                }
            }
        }
        m_MovementLabAimSessionActive = true;
        m_MovementLabAimSessionStanding = !aimCrouching;
        bool aimCtrl = GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05;
        bool aimCtrlPressed = aimCtrl && !m_MovementLabAimCtrlDown;
        m_MovementLabAimCtrlDown = aimCtrl;
        m_MovementLabCtrlDown = aimCtrl;
        bool aimShiftHeld = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
        bool aimShiftPressed = aimShiftHeld && !m_MovementLabAimShiftDown;
        m_MovementLabAimShiftDown = aimShiftHeld;
        bool aimSprintBlending = !aimCrouching && m_MovementLabAimSprintTime > 0;
        if (!aimCrouching && !aimSprintBlending)
        {
            if (aimCtrlPressed)
            {
                m_MovementLabAimBaseSlow = !m_MovementLabAimSlowMode;
                m_MovementLabAimSlowLevel = 3;
                m_MovementLabAimFastLevel = 3;
            }
            else if (aimShiftPressed && m_MovementLabAimSlowMode)
            {
                m_MovementLabAimBaseSlow = false;
                m_MovementLabAimFastLevel = 3;
            }
            m_MovementLabAimSlowMode = m_MovementLabAimBaseSlow;
        }
        if (m_MovementLabWheelPending != 0)
        {
            if (aimCrouching)
                m_MovementLabAimCrouchLevel = Math.Clamp(m_MovementLabAimCrouchLevel + m_MovementLabWheelPending, 1, 4);
            else if (!MovementLabStartGate.NativeAimComparison && !aimSprintBlending)
            {
                int linkedAimCount = Math.AbsInt(m_MovementLabWheelPending);
                int linkedAimDirection = 1;
                if (m_MovementLabWheelPending < 0)
                    linkedAimDirection = -1;
                for (int linkedAimStep = 0; linkedAimStep < linkedAimCount; linkedAimStep++)
                    MovementLabStepLinkedAim(linkedAimDirection);
            }
            m_MovementLabWheelPending = 0;
        }
        float aimTargetProfile = 5;
        if (m_MovementLabAimSlowMode)
            aimTargetProfile = 2 + m_MovementLabAimSlowLevel;
        if (aimCrouching)
        {
            aimTargetProfile = 5 + m_MovementLabAimCrouchLevel;
            if (m_MovementLabAimCrouchLevel == 4)
                aimTargetProfile = 10;
        }
        float aimFastTargetProfile = m_MovementLabAimFastLevel;
        bool aimNativeComparison = MovementLabStartGate.NativeAimComparison && !aimCrouching;
        bool aimOriginalSlowSource = false;
        bool aimOriginalFastSource = !aimCrouching && !m_MovementLabAimSlowMode && m_MovementLabAimFastLevel == 2 && m_MovementLabAimFastPoseProfile <= 2.001;
        if (aimNativeComparison)
        {
            aimTargetProfile = 5;
            aimFastTargetProfile = 2;
        }
        if (aimSprintBlending)
        {
            float aimSprintProgress = 1 - m_MovementLabAimSprintTime / 1.5;
            float aimSprintEase = aimSprintProgress * aimSprintProgress;
            aimSprintEase = aimSprintEase * (3 - 2 * aimSprintProgress);
            aimFastTargetProfile = 4 - 2 * aimSprintEase;
            // Let the native sprint-to-raised handoff finish before consuming the visible aim blend.
            m_MovementLabAimSprintHandoff = Math.Max(0, m_MovementLabAimSprintHandoff - dt);
            if (GetCommand_Move().GetCurrentMovementSpeed() <= 2.1 || m_MovementLabAimSprintHandoff <= 0)
                m_MovementLabAimSprintTime = Math.Max(0, m_MovementLabAimSprintTime - dt);
            if (m_MovementLabAimSprintTime <= 0.0001)
            {
                m_MovementLabAimSprintTime = 0;
                m_MovementLabAimFastLevel = 2;
                aimFastTargetProfile = 2;
            }
        }
        if (aimEntering)
        {
            m_MovementLabAimPoseProfile = aimTargetProfile;
            m_MovementLabAimFastPoseProfile = aimFastTargetProfile;
        }
        else
        {
            float aimProfileBlend = Math.Clamp(dt / 0.20, 0, 1);
            m_MovementLabAimPoseProfile = m_MovementLabAimPoseProfile + (aimTargetProfile - m_MovementLabAimPoseProfile) * aimProfileBlend;
            m_MovementLabAimFastPoseProfile = m_MovementLabAimFastPoseProfile + (aimFastTargetProfile - m_MovementLabAimFastPoseProfile) * aimProfileBlend;
        }
        if (aimSprintBlending && !aimNativeComparison)
            m_MovementLabAimFastPoseProfile = aimFastTargetProfile;
        m_MovementLabAimLastStance = aimState.m_iStanceIdx;
        m_MovementLabAimOwnsSpeed = true;
        // Native upper-body raised/ADS layers stay outside the six retimed foot sources.
        if (m_MovementLabAllSmoothActiveVar < 0 && GetAnimInterface())
            m_MovementLabAllSmoothActiveVar = GetAnimInterface().BindVariableFloat("MovementLabAllSmoothActive");
        if (m_MovementLabAllSmoothActiveVar >= 0)
            AnimSetFloat(m_MovementLabAllSmoothActiveVar, 0);
        float aimWalkActive = 1;
        if (aimNativeComparison || aimOriginalSlowSource || aimOriginalFastSource)
            aimWalkActive = 0;
        if (m_MovementLabAimActiveVar >= 0)
            AnimSetFloat(m_MovementLabAimActiveVar, aimWalkActive);
        if (m_MovementLabAimProfileVar >= 0)
            AnimSetFloat(m_MovementLabAimProfileVar, m_MovementLabAimPoseProfile);
        float aimFastActive = 1;
        if (aimCrouching || aimNativeComparison || aimOriginalSlowSource || aimOriginalFastSource)
            aimFastActive = 0;
        if (m_MovementLabAimFastActiveVar >= 0)
            AnimSetFloat(m_MovementLabAimFastActiveVar, aimFastActive);
        if (m_MovementLabAimFastProfileVar >= 0)
            AnimSetFloat(m_MovementLabAimFastProfileVar, m_MovementLabAimFastPoseProfile);
        MovementLabApplyAimWalkingSpeed();
        if (aimEntering || aimTargetProfile != m_MovementLabAimReportProfile || GetGame().GetTime() - m_MovementLabAimReportTime >= 500)
        {
            m_MovementLabAimReportTime = GetGame().GetTime();
            m_MovementLabAimReportProfile = aimTargetProfile;
            Print("[MovementLab AimWalk v2] Slow mode=" + m_MovementLabAimSlowMode + ", slow level=" + m_MovementLabAimSlowLevel + ", fast level=" + m_MovementLabAimFastLevel);
            Print("[MovementLab AimMomentum rev17] Remaining=" + m_MovementLabAimSprintTime + ", pose=" + m_MovementLabAimFastPoseProfile + ", native comparison=" + MovementLabStartGate.NativeAimComparison);
            Print("[MovementLab AimWalk v2] Crouch level=" + m_MovementLabAimCrouchLevel);
            Print("[MovementLab AimWalk] Profile=" + m_MovementLabAimPoseProfile + ", active binding=" + m_MovementLabAimActiveVar + ", profile binding=" + m_MovementLabAimProfileVar);
            Print("[MovementLab AimWalk] Achieved gait=" + GetCommand_Move().GetCurrentMovementSpeed() + ", velocity m/s=" + GetVelocity(this).Length());
        }
        return true;
    }

    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        if (MovementLabUpdateAimWalking(pDt, pCurrentCommandID))
        {
            super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
            return;
        }
        MovementLabUpdateStandingWalkWheel(pDt, pCurrentCommandID);
        MovementLabUpdateCrouchWheel(pDt, pCurrentCommandID);
        MovementLabUpdateCrouchPoseExit(pDt, pCurrentCommandID);
        MovementLabUpdateAllPoseSmoothing(pDt, pCurrentCommandID);
        MovementLabCommandStart(pDt, pCurrentCommandID);
        MovementLabUpdateStrafeSlow(pDt, pCurrentCommandID);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
