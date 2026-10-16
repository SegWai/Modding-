// Fixed-position third-person pivot experiment, based on v71.
// Capture the native camera offset once; keep it in world axes as the body turns.
modded class DayZPlayerCamera3rdPerson
{
    protected bool m_MovementLabFixedPivotKnown;
    protected vector m_MovementLabFixedWorldOffset;

    protected vector MovementLabRotateOffsetYaw(vector value, float yaw)
    {
        float sine = Math.Sin(yaw * Math.DEG2RAD);
        float cosine = Math.Cos(yaw * Math.DEG2RAD);
        return Vector(value[0] * cosine + value[2] * sine, value[1], value[2] * cosine - value[0] * sine);
    }

    protected vector MovementLabPivotForFixedOrigin(vector worldOffset, vector lookHeading, float headingYaw, float distance)
    {
        // PositionModelSpace=0 means the pivot is expressed in heading space.
        // Native boom distance is applied along lookHeading afterwards.
        vector headingOffset = MovementLabRotateOffsetYaw(worldOffset, -headingYaw);
        return headingOffset + lookHeading * distance;
    }

    protected void MovementLabApplyFixedPivot(out DayZPlayerCameraResult result)
    {
        PlayerBase player = PlayerBase.Cast(m_pPlayer);
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || !player || GetGame().GetPlayer() != player || !player.IsAlive() || !player.GetCommand_Move() || player.IsRaised() || player.IsInIronsights() || player.IsInOptics() || result.m_fUseHeading < 0.99)
        {
            m_MovementLabFixedPivotKnown = false;
            return;
        }
        float headingYaw = -m_pInput.GetHeadingAngle() * Math.RAD2DEG;
        if (!m_MovementLabFixedPivotKnown)
        {
            float positionYaw = headingYaw;
            if (result.m_fPositionModelSpace > 0.5)
                positionYaw = player.GetOrientation()[0];
            vector nativePivotWorld = MovementLabRotateOffsetYaw(result.m_CameraTM[3], positionYaw);
            vector nativeLookWorld = MovementLabRotateOffsetYaw(result.m_CameraTM[2], headingYaw);
            m_MovementLabFixedWorldOffset = nativePivotWorld - nativeLookWorld * result.m_fDistance;
            m_MovementLabFixedPivotKnown = true;
        }
        // Follow the character's translation, preserving the captured offset in
        // world axes. Looking or turning the body cannot rotate this offset.
        result.m_CameraTM[3] = MovementLabPivotForFixedOrigin(m_MovementLabFixedWorldOffset, result.m_CameraTM[2], headingYaw, result.m_fDistance);
        result.m_fPositionModelSpace = 0.0;
    }

    override void OnActivate(DayZPlayerCamera pPrevCamera, DayZPlayerCameraResult pPrevCameraResult)
    {
        super.OnActivate(pPrevCamera, pPrevCameraResult);
        m_MovementLabFixedPivotKnown = false;
    }

    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        // Crouch must finish its existing height correction before anchoring.
        // Prone supplies its own OnUpdate path.
        if (!DayZPlayerCamera3rdPersonCrouch.Cast(this) && !DayZPlayerCamera3rdPersonProneBase.Cast(this))
            MovementLabApplyFixedPivot(pOutResult);
    }
}

modded class DayZPlayerCamera3rdPersonProneBase
{
    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        MovementLabApplyFixedPivot(pOutResult);
    }
}
