modded class DayZPlayerCameraBase
{
    // Camera LR is added to the engine's aiming heading, not to body yaw.
    // GetHeadingAngle has the opposite sign to world/model yaw (native camera
    // code uses the same sign conversion). Both headings below are world-space.
    protected void MovementLabBodyLookLimits(inout float pMin, inout float pMax)
    {
        if (!m_pPlayer || !m_pInput || m_pPlayer.GetCommand_Vehicle())
            return;
        vector bodyOrientation = m_pPlayer.GetOrientation();
        float aimWorldYaw = -m_pInput.GetHeadingAngle() * Math.RAD2DEG;
        float aimRelativeToBody = fixAngle_180_180(aimWorldYaw - bodyOrientation[0]);
        // Intersect the native range with the remaining body-relative range.
        pMin = Math.Max(pMin, -90.0 - aimRelativeToBody);
        pMax = Math.Min(pMax, 90.0 - aimRelativeToBody);
    }

    override float UpdateLRAngleUnlocked(out float pAngle, out float pAngleAdd, float pMin, float pMax, float pDt)
    {
        MovementLabBodyLookLimits(pMin, pMax);
        return super.UpdateLRAngleUnlocked(pAngle, pAngleAdd, pMin, pMax, pDt);
    }

    override float UpdateLRAngle(float pAngle, float pMin, float pMax, float pDt)
    {
        MovementLabBodyLookLimits(pMin, pMax);
        return super.UpdateLRAngle(pAngle, pMin, pMax, pDt);
    }
}
