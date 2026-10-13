// Reuse the player's existing look-zoom action only while ADS is active.
// One press switches iron sights <-> attached scope; holding cannot repeat.
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
}
