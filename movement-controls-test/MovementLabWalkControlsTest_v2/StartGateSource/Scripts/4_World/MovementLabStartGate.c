// The offline mission enables this profile. Native movement owns animation.
class MovementLabStartGate
{
    static bool Enabled;
}

class MovementLabWalkControls
{
    float Speed;
    float Angle;
    bool Braking;
    bool Moving;
    bool Sprint;
    bool WasShift;
    float Clock;
    float LastTap = -1;
    float Exposure;
    float BrakeTime;
    float BrakeDuration;
    float BrakeStart;
    int LastKeys;
    float StartTime;
    float BlendTime;
    float BlendStart;
    float PreviousTarget;

    float Ease(float value)
    {
        float t = Math.Clamp(value, 0, 1);
        return t * t * (3.0 - 2.0 * t);
    }

    void Reset()
    {
        Speed = 0;
        Angle = 0;
        Braking = false;
        Moving = false;
        Sprint = false;
        WasShift = false;
        LastTap = -1;
        Exposure = 0;
        StartTime = 0;
        PreviousTarget = 0;
    }

    void BeginStop(float achieved)
    {
        // Stop from the achieved gait, never the sprint request alone.
        BrakeStart = Math.Clamp(Math.Min(achieved, Speed), 0, 3);
        BrakeTime = 0;
        BrakeDuration = 0.14;
        if (BrakeStart >= 2.05)
        {
            float amount = Math.Clamp(BrakeStart - 2.0, 0, 1);
            float sustained = Math.Clamp(Exposure / 0.45, 0, 1);
            BrakeDuration = 0.18 + 0.97 * amount * sustained;
            // A barely achieved sprint must not stop faster than a jog.
            float jogBudget = 0.42;
            if (LastKeys == 2)
                jogBudget = 0.18;
            BrakeDuration = Math.Max(jogBudget, BrakeDuration);
        }
        else if (BrakeStart >= 1.75)
        {
            BrakeDuration = 0.42 * Math.Min(BrakeStart / 2.0, 1.0);
            if (LastKeys == 2)
                BrakeDuration = 0.18 * Math.Min(BrakeStart / 2.0, 1.0);
        }
        else if (BrakeStart > 1.05)
            BrakeDuration = 0.25;
        Braking = BrakeStart > 0.05;
    }

    void UpdateStop(float dt)
    {
        BrakeTime = BrakeTime + dt;
        float fraction = Math.Clamp(BrakeTime / BrakeDuration, 0, 1);
        if (fraction >= 1)
        {
            Speed = 0;
            Braking = false;
            return;
        }
        float blend = 2.0 * fraction - fraction * fraction;
        Speed = BrakeStart * (1.0 - blend);
        // V11 near/full-sprint budget: prompt jog, longer jog, short walk.
        if (BrakeStart >= 2.5)
        {
            if (fraction < 0.18)
            {
                float sprintBlend = fraction / 0.18;
                sprintBlend = 2.0 * sprintBlend - sprintBlend * sprintBlend;
                Speed = BrakeStart + (2.0 - BrakeStart) * sprintBlend;
            }
            else if (fraction < 0.62)
                Speed = 2.0;
            else if (fraction < 0.82)
                Speed = 2.0 - Ease((fraction - 0.62) / 0.20);
            else if (fraction < 0.92)
                Speed = 1.0;
            else
            {
                float walkBlend = (fraction - 0.92) / 0.08;
                walkBlend = 2.0 * walkBlend - walkBlend * walkBlend;
                Speed = 1.0 - walkBlend;
            }
        }
        if (LastKeys == 4 || LastKeys == 8)
            Speed = Math.Min(BrakeStart, Math.Max(1.0, Speed));
        if (LastKeys == 2)
            Speed = Math.Min(1.0, BrakeStart);
    }

    void Update(float dt, float forward, float side, int keys, bool shift, bool forcedWalk, float achieved)
    {
        dt = Math.Max(dt, 0);
        Clock = Clock + dt;
        bool movement = Math.AbsFloat(forward) > 0.05 || Math.AbsFloat(side) > 0.05;
        bool press = shift && !WasShift;
        WasShift = shift;
        if (!movement)
        {
            if (Moving)
                BeginStop(achieved);
            Moving = false;
            Sprint = false;
            LastTap = -1;
            Exposure = 0;
            StartTime = 0;
            PreviousTarget = 0;
            if (Braking)
                UpdateStop(dt);
            else
                Speed = 0;
            // Keep the last movement angle throughout stop and idle.
            return;
        }
        if (press)
        {
            if (LastTap >= 0 && Clock - LastTap <= 0.30)
                Sprint = true;
            LastTap = Clock;
        }
        if (forcedWalk)
        {
            Sprint = false;
            LastTap = -1;
        }
        float target = 1.0;
        if (!forcedWalk)
        {
            if (Sprint)
                target = 3.0;
            else if (shift)
                target = 2.0;
        }
        Angle = Math.Atan2(side, forward) * Math.RAD2DEG;
        LastKeys = keys;
        bool started = !Moving;
        bool resuming = started && Braking;
        if (resuming && achieved <= 0.10)
            resuming = false;
        if (started)
        {
            if (resuming)
            {
                // Retarget a moving coast from its current gait, without
                // snapping to a new walking start in the middle of a step.
                Speed = Math.Clamp(Math.Min(Speed, achieved), 0, 3);
                StartTime = 0.35;
            }
            else
            {
                Speed = 1.0;
                StartTime = 0;
            }
            BlendTime = 0;
            BlendStart = Speed;
            PreviousTarget = 0;
        }
        Moving = true;
        Braking = false;
        StartTime = StartTime + dt;
        float stage = target;
        if (target == 3.0)
        {
            // Restore v11's walk/jog lead-in before handing off to sprint.
            // A quick double tap cannot blend directly from gait 1 to gait 3.
            if (Speed < 1.999 || StartTime < 0.35 || achieved < 1.75)
                stage = 2.0;
        }
        else if (target == 1.0 && Speed > 2.001)
            stage = 2.0;
        if (stage != PreviousTarget)
        {
            BlendStart = Speed;
            BlendTime = 0;
            PreviousTarget = stage;
        }
        if (started && !resuming)
        {
            Speed = 1.0;
            BlendStart = Speed;
            BlendTime = 0;
        }
        else if (StartTime <= 0.10 && target > 1.0)
        {
            Speed = 1.0;
            BlendStart = Speed;
            BlendTime = 0;
        }
        else
        {
            BlendTime = BlendTime + dt;
            float duration = 0.18;
            if (stage == 3.0)
                duration = 0.36;
            Speed = BlendStart + (stage - BlendStart) * Ease(BlendTime / duration);
        }
        if (Sprint && achieved > 2.05)
            Exposure = Math.Min(0.45, Exposure + dt);
        else
            Exposure = 0;
    }
}

modded class PlayerBase
{
    protected ref MovementLabWalkControls m_MovementLabControls;
    protected bool m_MovementLabControlsOwnInput;

    bool MovementLabControlsBraking()
    {
        return m_MovementLabControls && m_MovementLabControls.Braking;
    }

    void MovementLabCancelControls()
    {
        if (m_MovementLabControlsOwnInput && GetInputController())
        {
            GetInputController().OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
            GetInputController().OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
        }
        m_MovementLabControlsOwnInput = false;
        if (m_MovementLabControls)
            m_MovementLabControls.Reset();
    }

    protected bool MovementLabCanUseControls(float dt, int command, bool finished)
    {
        // Keep each eligibility expression small for Enforce compilation.
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer())
            return false;
        if (GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
            return false;
        if (IsRaised() || IsEmotePlaying())
            return false;
        if (command != DayZPlayerConstants.COMMANDID_MOVE || finished)
            return false;
        if (!GetCommand_Move() || !GetInputController())
            return false;
        if (dt > 0.25 || PhysicsIsFalling(true))
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

    protected void MovementLabUpdateControls(float dt, int command, bool finished)
    {
        if (!MovementLabCanUseControls(dt, command, finished))
        {
            MovementLabCancelControls();
            return;
        }
        if (!m_MovementLabControls)
            m_MovementLabControls = new MovementLabWalkControls();
        float f = GetUApi().GetInputByID(UAMoveForward).LocalValue();
        float b = GetUApi().GetInputByID(UAMoveBack).LocalValue();
        float l = GetUApi().GetInputByID(UAMoveLeft).LocalValue();
        float r = GetUApi().GetInputByID(UAMoveRight).LocalValue();
        float forward = f - b;
        float side = r - l;
        int keys = 0;
        if (forward > 0.05)
            keys = keys + 1;
        if (forward < -0.05)
            keys = keys + 2;
        if (side < -0.05)
            keys = keys + 4;
        if (side > 0.05)
            keys = keys + 8;
        HumanInputController input = GetInputController();
        bool forcedWalk = input.IsWalkToggled();
        if (GetUApi().GetInputByID(UAWalkRunTemp).LocalValue() > 0.05)
            forcedWalk = true;
        if (GetUApi().GetInputByID(UAWalkRunForced).LocalValue() > 0.05)
            forcedWalk = true;
        bool shift = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
        float achieved = GetCommand_Move().GetCurrentMovementSpeed();
        m_MovementLabControls.Update(dt, forward, side, keys, shift, forcedWalk, achieved);
        // Persistent pre-handler ownership prevents a leaked native jog frame.
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, m_MovementLabControls.Speed);
        if (m_MovementLabControls.Braking)
            input.OverrideMovementAngle(HumanInputControllerOverrideType.ENABLED, m_MovementLabControls.Angle);
        else
            input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
        m_MovementLabControlsOwnInput = true;
    }

    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        MovementLabUpdateControls(pDt, pCurrentCommandID, pCurrentCommandFinished);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}
