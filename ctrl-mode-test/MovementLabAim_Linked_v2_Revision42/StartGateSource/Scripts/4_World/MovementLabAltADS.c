modded class PlayerBase
{
    protected bool m_MovementLabSightZoomDown;

    void MovementLabUpdateZoomSightSwitch()
    {
        if (!GetGame() || GetGame().GetPlayer() != this || !GetUApi())
            return;
        UAInput sightZoomInput = GetUApi().GetInputByID(UAZoomInToggle);
        if (!sightZoomInput)
            return;
        bool sightZoomHeld = sightZoomInput.LocalValue() > 0.05;
        bool sightZoomPressed = sightZoomHeld && !m_MovementLabSightZoomDown;
        m_MovementLabSightZoomDown = sightZoomHeld;
        if (!sightZoomPressed || !MovementLabStartGate.Enabled || GetGame().IsMultiplayer())
            return;
        if (!GetGame().GetInput().HasGameFocus() || GetGame().GetUIManager().GetMenu() || GetGame().GetMission().IsPaused())
            return;
        if (!IsAlive() || IsUnconscious() || !IsRaised() || (!m_CameraIronsight && !m_CameraOptics))
            return;
        Weapon_Base sightZoomWeapon = Weapon_Base.Cast(GetEntityInHands());
        if (!sightZoomWeapon || !sightZoomWeapon.CanEnterIronsights())
            return;
        ItemOptics sightZoomOptic = sightZoomWeapon.GetAttachedOptics();
        if (!sightZoomOptic || sightZoomOptic.IsSightOnly())
            return;
        if (IsLiftWeapon() || IsWeaponObstructionBlockingADS() || !IsWeaponRaiseCompleted() || IsFighting() || GetCommand_Melee2())
            return;
        if (GetDayZPlayerInventory().IsProcessing() || !GetWeaponManager() || GetWeaponManager().IsRunning())
            return;
        if (m_CameraOptics)
        {
            SwitchOptics(sightZoomOptic, false);
            SetIronsights(true);
            sightZoomWeapon.SetWasIronSight(true);
        }
        else
        {
            SetIronsights(false);
            SwitchOptics(sightZoomOptic, true);
            sightZoomWeapon.SetWasIronSight(false);
        }
    }

    protected bool m_MovementLabAltADS;

    void MovementLabCancelAltADS()
    {
        m_MovementLabAltADS = false;
        m_bADS = false;
        ExitSights();
    }

    override int CameraHandler(int pCameraMode)
    {
        MovementLabUpdateZoomSightSwitch();
        if (MovementLabStartGate.Enabled && !GetGame().IsMultiplayer() && GetGame().GetPlayer() == this)
        {
            HumanInputController cameraADSInput = GetInputController();
            if (cameraADSInput && cameraADSInput.WeaponADS())
                cameraADSInput.ResetADS();
        }
        return super.CameraHandler(pCameraMode);
    }

    void MovementLabToggleAltADS()
    {
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this)
            return;
        if (!IsAlive() || IsUnconscious() || !IsRaised() || !GetItemInHands() || !GetItemInHands().IsWeapon())
            return;
        if (!GetGame().GetInput().HasGameFocus() || GetGame().GetUIManager().GetMenu())
            return;
        m_MovementLabAltADS = !m_MovementLabAltADS;
    }

	override void HandleADS()
	{
        if (!MovementLabStartGate.Enabled || GetGame().IsMultiplayer() || GetGame().GetPlayer() != this)
        {
            super.HandleADS();
            return;
        }
        HumanInputController altADSInput = GetInputController();
        if (altADSInput && altADSInput.WeaponADS())
            altADSInput.ResetADS();
        if (!IsRaised() || !IsAlive() || !GetItemInHands() || !GetItemInHands().IsWeapon())
            m_MovementLabAltADS = false;
		if (!IsAlive())
		{
			if (m_CameraIronsight || m_CameraOptics)
			{
				ExitSights();
			}
			return;
		}
		
		bool bADSToggle = false;
		bool exitSights = false;
		HumanInputController hic = GetInputController();
		HumanItemAccessor 	hia = GetItemAccessor();
		HumanCommandWeapons	hcw = GetCommandModifier_Weapons();
		PlayerBase playerPB = PlayerBase.Cast(this);
		GetMovementState(m_MovementState);
		
		if (playerPB.IsRolling())
		{
			exitSights = true;
		}
		
		bool isItemInHandsWeapon = hia.IsItemInHandsWeapon();
		if (m_ResetADS || (!isItemInHandsWeapon && hic.WeaponADS()))
		{
			hic.ResetADS();
			m_ResetADS = false;
		}
		
		if (!m_MovementState.IsRaised() || m_LiftWeapon_player)
		{
			ResetWeaponRaiseProgress();
			exitSights = true;
		}
		else
		{
			bool isWeaponADS = m_MovementLabAltADS;
			if (m_bADS != isWeaponADS)
			{
				m_bADS = isWeaponADS;
				bADSToggle = true;
			}
			
			if (m_bADS && !m_CameraIronsight && !m_CameraOptics)
			{
				//!artificial Auto-ADS delay
				if (!IsWeaponRaiseCompleted())
				{
					bADSToggle = false;
					exitSights = true;
				}
				else
				{
					bADSToggle = true;
				}
			}
		}
	
		if (bADSToggle && !GetCommand_Melee2() && !GetThrowing().IsThrowingModeEnabled())
		{
			if (hia.IsItemInHandsWeapon() && playerPB.GetWeaponManager() && !playerPB.GetWeaponManager().IsRunning())
			{
				Weapon_Base weapon = Weapon_Base.Cast(GetEntityInHands());
				ItemOptics optic = weapon.GetAttachedOptics();
				bool switchToADS = false;
				bool canUseIronsights = weapon.CanEnterIronsights();
				bool canUseOptics = optic != NULL;
				
				if (canUseIronsights || canUseOptics)
					switchToADS = m_bADS;
				
				// go to ironsights - disable ironsights when
				//! if !raised
				//! if sprinting
				if (!m_MovementState.IsRaised() || m_MovementState.m_iMovement == DayZPlayerConstants.MOVEMENTIDX_SPRINT)
				{
					switchToADS = false;
				}
				
				// fixes camera switching during item transitions
				if (IsLiftWeapon() || IsWeaponObstructionBlockingADS() || !IsRaised() || GetDayZPlayerInventory().IsProcessing() || !IsWeaponRaiseCompleted() || IsFighting())
				{
					exitSights = true;
				}
				else if (switchToADS) // enter ironsights or optics
				{
					// filter by usability
					if (weapon.GetWasIronSight() && !canUseIronsights)
					{
						weapon.SetWasIronSight(false);
					}
					else if (!weapon.GetWasIronSight() && !canUseOptics)
					{
						weapon.SetWasIronSight(true);
					}
					
					if (weapon.GetWasIronSight())
					{
						SwitchOptics(optic,false);
						SetIronsights(true);
					}
					else if (!weapon.GetWasIronSight() || (!canUseIronsights && canUseOptics))
					{
						SetIronsights(false);
						SwitchOptics(optic,true);
					}
					else
					{
						exitSights = true;
					}
					
					if (hcw && (m_CameraOptics/* || m_CameraIronsight*/))
					{
						hcw.SetADS(true);
					}
				}
				else
				{
					exitSights = true;
				}
			}
		}
		
		// leave ironsight and/ or optics
		if (exitSights && !IsHandheldOpticsInUse() && (m_CameraIronsight || m_CameraOptics) || GetCommand_Melee2())
		{
			ExitSights();
		}
	}
	
}
