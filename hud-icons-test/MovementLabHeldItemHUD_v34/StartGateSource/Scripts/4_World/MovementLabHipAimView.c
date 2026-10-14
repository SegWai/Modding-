// Native first-person camera restored. This observer never changes the
// returned transform, view angles, heading, weapon pose, or input state.
modded class DayZPlayerCamera1stPerson
{
    protected int m_MovementLabHipDiagnosticTime = -1000;

    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != m_pPlayer)
            return;
        PlayerBase hipDiagnosticPlayer = PlayerBase.Cast(m_pPlayer);
        if (!hipDiagnosticPlayer || !hipDiagnosticPlayer.IsAlive() || hipDiagnosticPlayer.IsUnconscious() || !hipDiagnosticPlayer.IsRaised())
            return;
        if (hipDiagnosticPlayer.IsInIronsights() || hipDiagnosticPlayer.IsInOptics() || !m_CommandWeapons || !m_pInput)
            return;
        if (!hipDiagnosticPlayer.GetItemInHands() || !hipDiagnosticPlayer.GetItemInHands().IsWeapon())
            return;
        int hipDiagnosticNow = GetGame().GetTime();
        if (hipDiagnosticNow - m_MovementLabHipDiagnosticTime < 500)
            return;
        m_MovementLabHipDiagnosticTime = hipDiagnosticNow;
        vector hipDiagnosticPosition;
        vector hipDiagnosticDirection;
        vector hipDiagnosticRotation;
        hipDiagnosticPlayer.GetCurrentCameraTransform(hipDiagnosticPosition, hipDiagnosticDirection, hipDiagnosticRotation);
        Print("[MovementLab Hip Native] Body=" + hipDiagnosticPlayer.GetOrientation());
        Print("[MovementLab Hip Native] InputHeading=" + m_pInput.GetHeadingAngle() + ", freeLook=" + m_pInput.CameraIsFreeLook() + ", tracking=" + m_pInput.CameraIsTracking());
        Print("[MovementLab Hip Native] BaseLR=" + m_CommandWeapons.GetBaseAimingAngleLR() + ", baseUD=" + m_CommandWeapons.GetBaseAimingAngleUD());
        Print("[MovementLab Hip Native] CameraYaw=" + m_CurrentCameraYaw + ", pitch=" + m_CurrentCameraPitch + ", headingWeight=" + pOutResult.m_fUseHeading + ", boneMode=" + pOutResult.m_iDirectBoneMode);
        Print("[MovementLab Hip Native] ActualCameraRotation=" + hipDiagnosticRotation + ", direction=" + hipDiagnosticDirection);
    }
}
