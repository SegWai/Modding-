// Retain the same native MOVE command and its animation clock throughout.
class MovementLabReversalSettings
{
    static bool Enabled = true;
}

class MovementLabNativeReversal
{
    bool Active;
    bool OwnsInput;
    bool HasDirection;
    float Angle;
    float TargetAngle;
    float Time;
    float Gap;
    float StartSpeed;
    float Speed;
    float Forward;
    float Side;
    int Reversals;

    float Ease(float value)
    {
        float t = Math.Clamp(value, 0, 1);
        return t * t * (3.0 - 2.0 * t);
    }

    void Reset()
    {
        Active = false;
        HasDirection = false;
        Gap = 0;
        Time = 0;
    }

    bool Update(float dt, float forward, float side, float gait, bool held)
    {
        dt = Math.Max(dt, 0);
        float length = Math.Sqrt(forward * forward + side * side);
        if (length <= 0.05)
        {
            if (held)
                Gap = 0;
            else
                Gap = Gap + dt;
            // Overlapping opposite keys and very short release gaps are neutral:
            // they never restart or retarget an in-progress native transition.
            if (!Active || Gap >= 0.10)
            {
                Reset();
                return false;
            }
        }
        else
            Gap = 0;

        // End recovery BEFORE testing current input, without releasing the
        // override for an intervening native tick if another reversal is due.
        if (Active && Time >= 0.62)
            Active = false;
        if (!Active)
        {
            if (length <= 0.05)
                return false;
            float wantedForward = forward / length;
            float wantedSide = side / length;
            if (HasDirection && gait >= 1.75 && wantedForward * Forward + wantedSide * Side < -0.65)
            {
                Active = true;
                Time = 0;
                StartSpeed = Math.Clamp(gait, 1.75, 3.0);
                TargetAngle = Math.Atan2(side, forward) * Math.RAD2DEG;
                Forward = wantedForward;
                Side = wantedSide;
                Reversals = Reversals + 1;
            }
            else
            {
                HasDirection = true;
                Forward = wantedForward;
                Side = wantedSide;
                Angle = Math.Atan2(side, forward) * Math.RAD2DEG;
                return false;
            }
        }
        Time = Time + dt;
        if (Time < 0.12)
            Speed = StartSpeed + (1.60 - StartSpeed) * Ease(Time / 0.12);
        else
        {
            // One native direction change, at reduced gait. No intermediate
            // forward-facing atlas samples and no manually requested brace.
            Angle = TargetAngle;
            Speed = 1.60 + 0.40 * Ease((Time - 0.12) / 0.50);
        }
        return true;
    }
}
