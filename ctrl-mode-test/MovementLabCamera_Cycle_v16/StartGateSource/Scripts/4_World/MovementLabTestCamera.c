class MovementLabCameraSettings
{
    static bool WiderView;
    static int ViewMode; // 0 default third, 1 wider third, 2 first
}

modded class DayZPlayerCamera3rdPerson
{
    protected float m_MovementLabExtraDistance;
    protected float m_MovementLabExtraDistanceVelocity[1];
    protected float m_MovementLabExtraHeight;
    protected float m_MovementLabExtraHeightVelocity[1];

    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer())
            return;
        float extraDistanceTarget = 0;
        float extraHeightTarget = 0;
        if (MovementLabCameraSettings.WiderView)
        {
            if (m_MovementState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT)
            {
                extraDistanceTarget = 0.45;
                extraHeightTarget = 0;
            }
            else if (m_MovementState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH)
                extraDistanceTarget = 0.60;
        }
        m_MovementLabExtraDistance = Math.SmoothCD(m_MovementLabExtraDistance, extraDistanceTarget, m_MovementLabExtraDistanceVelocity, 0.15, 1000, pDt);
        m_MovementLabExtraHeight = Math.SmoothCD(m_MovementLabExtraHeight, extraHeightTarget, m_MovementLabExtraHeightVelocity, 0.15, 1000, pDt);
        pOutResult.m_fDistance = pOutResult.m_fDistance + m_MovementLabExtraDistance;
        pOutResult.m_CameraTM[3][1] = pOutResult.m_CameraTM[3][1] + m_MovementLabExtraHeight;
    }
}

class MovementLabTestBackpack extends AliceBag_Green {}

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
