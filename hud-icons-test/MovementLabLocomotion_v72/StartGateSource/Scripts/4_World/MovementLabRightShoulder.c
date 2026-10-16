// Keep the third-person camera origin on the character's right shoulder.
// Camera look orientation and native boom collision distance remain native.
modded class PlayerBase
{
    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        if (MovementLabStartGate.Enabled && !GetGame().IsMultiplayer() && GetGame().GetPlayer() == this && GetInputController())
            GetInputController().Override3rdIsRightShoulder(HumanInputControllerOverrideType.ONE_FRAME, true);
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
    }
}

modded class DayZPlayerCamera3rdPerson
{
    protected vector MovementLabHeadingVectorToBody(vector value, float relativeYaw)
    {
        float sine = Math.Sin(relativeYaw * Math.DEG2RAD);
        float cosine = Math.Cos(relativeYaw * Math.DEG2RAD);
        return Vector(value[0] * cosine + value[2] * sine, value[1], value[2] * cosine - value[0] * sine);
    }

    protected vector MovementLabFixedShoulderPivot(vector baseMS, vector offsetLS, float shoulder, float distance, vector lookBody)
    {
        vector anchor = baseMS + offsetLS;
        anchor[0] = anchor[0] + shoulder;
        anchor[2] = anchor[2] - distance;
        // Native collision evaluation still backs the camera off along its look
        // vector by 'distance'. Counter that orbit in the pivot, so the resulting
        // camera origin stays fixed behind the body's right shoulder.
        return anchor + lookBody * distance;
    }

    protected void MovementLabAnchorRightShoulder(out DayZPlayerCameraResult result)
    {
        PlayerBase player = PlayerBase.Cast(m_pPlayer);
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || !player || GetGame().GetPlayer() != player || !player.IsAlive() || !player.GetCommand_Move())
            return;
        // Remove the native look-local offset from the current result to retain
        // its bone anchor and native stance-height adjustments.
        vector nativeLS = m_CameraOffsetLS;
        float currentShoulder = m_fCameraLRShoulder * m_fShoulderWidth;
        float leanShift = m_MovementState.m_fLeaning * m_fLeanDistance;
        if (m_bShoulderInLS)
            nativeLS[0] = nativeLS[0] + currentShoulder + leanShift;
        vector transformedLS = result.m_CameraTM[0] * nativeLS[0] + result.m_CameraTM[1] * nativeLS[1] + result.m_CameraTM[2] * nativeLS[2];
        vector baseMS = result.m_CameraTM[3] - transformedLS;
        if (!m_bShoulderInLS)
            baseMS[0] = baseMS[0] - currentShoulder - leanShift;
        float headingYaw = -m_pInput.GetHeadingAngle() * Math.RAD2DEG;
        float bodyYaw = player.GetOrientation()[0];
        vector lookBody = MovementLabHeadingVectorToBody(result.m_CameraTM[2], headingYaw - bodyYaw);
        float rightShoulder = m_fShoulderWidth + leanShift;
        result.m_CameraTM[3] = MovementLabFixedShoulderPivot(baseMS, m_CameraOffsetLS, rightShoulder, result.m_fDistance, lookBody);
        result.m_fPositionModelSpace = 1.0;
    }

    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        MovementLabAnchorRightShoulder(pOutResult);
    }
}

// The prone camera implements its own OnUpdate without calling the upright
// version. Keep its smoothed bone anchor, then apply the same positioning rule.
modded class DayZPlayerCamera3rdPersonProneBase
{
    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        MovementLabAnchorRightShoulder(pOutResult);
    }
}
