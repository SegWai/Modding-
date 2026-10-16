// Native camera LR helpers use degrees. Clamp their own accumulator, not the
// final camera transform, so excess mouse input cannot build up behind the limit.
modded class DayZPlayerCameraBase
{
    override float UpdateLRAngleUnlocked(out float pAngle, out float pAngleAdd, float pMin, float pMax, float pDt)
    {
        return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, Math.Max(pMin, -90.0), Math.Min(pMax, 90.0), pDt);
    }

    override float UpdateLRAngle(float pAngle, float pMin, float pMax, float pDt)
    {
        return super.UpdateLRAngle(pAngle, Math.Max(pMin, -90.0), Math.Min(pMax, 90.0), pDt);
    }
}
