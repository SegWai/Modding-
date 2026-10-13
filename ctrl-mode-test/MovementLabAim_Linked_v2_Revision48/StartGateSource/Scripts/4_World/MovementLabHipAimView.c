// Experimental first-person hip-aim alignment. Follow only native base aim
// angles (which explicitly exclude sway/recoil offsets), not the gun transform.
// This keeps ordinary breathing/recoil visible and leaves ADS/freelook alone.
modded class DayZPlayerCamera1stPerson
{
    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != m_pPlayer)
            return;
        PlayerBase hipViewPlayer = PlayerBase.Cast(m_pPlayer);
        if (!hipViewPlayer || !hipViewPlayer.IsAlive() || hipViewPlayer.IsUnconscious() || !hipViewPlayer.IsRaised())
            return;
        if (hipViewPlayer.IsInIronsights() || hipViewPlayer.IsInOptics() || !m_CommandWeapons || !m_pInput)
            return;
        if (m_pInput.CameraIsFreeLook() || m_pInput.CameraIsTracking())
            return;
        if (!hipViewPlayer.GetItemInHands() || !hipViewPlayer.GetItemInHands().IsWeapon())
            return;
        if (hipViewPlayer.IsLiftWeapon() || hipViewPlayer.IsWeaponObstructionBlockingADS())
            return;
        if (!hipViewPlayer.GetWeaponManager() || hipViewPlayer.GetWeaponManager().IsRunning())
            return;
        // Base LR is relative to the body, not to the input/aim heading.
        // Match native weapon world-direction construction: body yaw + base LR.
        // Disable engine heading addition so this yaw is applied only once.
        float hipViewYawShake = m_fLeftRightAngle + m_fLeftRightAngleAdd - m_CurrentCameraYaw;
        float hipViewPitchShake = m_fUpDownAngle + m_fUpDownAngleAdd - m_CurrentCameraPitch;
        m_CurrentCameraYaw = hipViewPlayer.GetOrientation()[0] + m_CommandWeapons.GetBaseAimingAngleLR() + hipViewYawShake;
        pOutResult.m_fUseHeading = 0;
        m_CurrentCameraPitch = m_CommandWeapons.GetBaseAimingAngleUD() + hipViewPitchShake;
        Math3D.YawPitchRollMatrix(GetCurrentOrientation(), pOutResult.m_CameraTM);
        // Preserve native camera position, bone binding, FOV and near plane.
        pOutResult.m_CameraTM[3] = m_OffsetLS;
    }
}
