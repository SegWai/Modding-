// Revision40: native breathing/hold-breath sway restored. ADS mouse-driven
// sight misalignment alone is removed; no aiming-model override.
class MovementLabWeaponSway
{
    static bool ShouldSuppress(PlayerBase player)
    {
        if (!MovementLabStartGate.Enabled || !GetGame() || GetGame().IsMultiplayer())
            return false;
        if (!player || GetGame().GetPlayer() != player || !player.IsAlive() || player.IsUnconscious() || !player.IsRaised())
            return false;
        EntityAI held = player.GetItemInHands();
        return held && held.IsWeapon();
    }
}

modded class DayZPlayerCameraIronsights
{
override void 		OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
	{
        if (!MovementLabWeaponSway.ShouldSuppress(PlayerBase.Cast(m_pPlayer)))
        {
            super.OnUpdate(pDt, pOutResult);
            return;
        }

		//! update angles from input 
		float min;
		DayZPlayerImplement player = DayZPlayerImplement.Cast(g_Game.GetPlayer());
		if (player && player.IsPlayerInStance(DayZPlayerConstants.STANCEMASK_RAISEDPRONE))
			min = CONST_UD_MIN_BACK;
		else
			min = CONST_UD_MIN;

		m_CurrentCameraYaw		= UpdateLRAngleUnlocked(m_fLeftRightAngle, m_fLeftRightAngleAdd, CONST_LR_MIN, CONST_LR_MAX, pDt);
		m_CurrentCameraPitch	= UpdateUDAngleUnlocked(m_fUpDownAngle, m_fUpDownAngleAdd, min, CONST_UD_MAX, pDt);

		// get model space transform matrix of the gun's eye vector 
		vector matTM[4];
		HumanItemAccessor hia = m_pPlayer.GetItemAccessor();
		if(GetCurrentSightEntity())
			hia.WeaponGetCameraPointBoneRelative(GetCurrentSightEntity(), m_OpticsCamPos, m_OpticsCamDir, m_iBoneIndex, matTM);
		
		// aim change based on character movement
		vector aimChangeYPR;
		float aimChangeX = m_pInput.GetAimDelta(pDt)[0] * Math.RAD2DEG;
		float aimChangeY = m_pInput.GetAimDelta(pDt)[1] * Math.RAD2DEG;
        // Remove only input-driven sight misalignment. Keep native walking
        // bob, breathing, horizontal noise, recoil and hold-breath behavior.
        aimChangeX = 0;
        aimChangeY = 0;


		HumanCommandMove hcm = m_pPlayer.GetCommand_Move();
		if (hcm)
		{
			float speed = hcm.GetCurrentMovementSpeed();
			
			if( speed > 0 )
				m_movementTimeAcc += pDt;
			else
				m_movementTimeAcc = 0;
			
			aimChangeX += m_movementAmplitudeX * speed * Math.Sin(Math.PI2 * m_movementFrequencyX * m_movementTimeAcc);
			aimChangeY += m_movementAmplitudeY * speed * Math.Sin(Math.PI2 * m_movementFrequencyY * m_movementTimeAcc);
		}

		aimChangeYPR[0] = Math.SmoothCD(aimChangeYPR[0], -(m_dynamicsStrength * aimChangeY), m_velocityYaw, m_dynamicsSmoothTime, 1000, pDt);
		aimChangeYPR[1] = Math.SmoothCD(aimChangeYPR[1], -(m_dynamicsStrength * aimChangeX), m_velocityPitch, m_dynamicsSmoothTime, 1000, pDt);
		aimChangeYPR[2] = 0;

		vector dynamics[4];
		Math3D.YawPitchRollMatrix(aimChangeYPR, dynamics);
		dynamics[3] = vector.Zero;
		
		// aiming model offsets
		vector aimingMatTM[4];
		hia.WeaponGetAimingModelDirTm(aimingMatTM);
		
		// final offset matrix
		Math3D.MatrixMultiply4(dynamics, aimingMatTM, dynamics);
		Math3D.MatrixMultiply4(dynamics, matTM, pOutResult.m_CameraTM);
			
		AdjustCameraParameters(pDt, pOutResult);
		UpdateBatteryOptics(GetCurrentSightEntity());
		UpdateCameraNV(PlayerBase.Cast(m_pPlayer));

		if(m_CameraShake)
		{
			float x,y;
			m_CameraShake.Update(pDt, x, y);
			DayZPlayerImplement.Cast(m_pPlayer).GetAimingModel().SetCamShakeValues(x, y);
		}
	}
}
