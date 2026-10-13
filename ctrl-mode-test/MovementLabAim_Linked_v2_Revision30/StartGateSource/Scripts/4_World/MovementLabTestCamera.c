class MovementLabTestBackpack extends AssaultBag_Black {}

modded class DayZPlayerCamera3rdPersonCrouch
{
    protected float m_MovementLabCrouchViewOffset;
    protected float m_MovementLabCrouchViewVelocity[1];

    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer())
            return;
        float viewTarget = 0;
        if (m_MovementState.m_iMovement > 0)
            viewTarget = CONST_CAMERAMOVEMENTHEIGH;
        m_MovementLabCrouchViewOffset = Math.SmoothCD(m_MovementLabCrouchViewOffset, viewTarget, m_MovementLabCrouchViewVelocity, 0.2, 1000, pDt);
        pOutResult.m_CameraTM[3][1] = pOutResult.m_CameraTM[3][1] + m_MovementLabCrouchViewOffset - m_fCameraHeight;
    }
}
