// Hide native held-item readout groups after native BuildCursor refreshes them.
// Keep interaction/action prompts and custom held-item card intact.
modded class ItemActionsWidget
{
    override protected void Update()
    {
        super.Update();
        if (!m_Hud || !m_Root || !MovementLabStartGate.Enabled || !m_Hud.MovementLabHeldPanelReady())
            return;
        if (m_ItemLeft)
            m_ItemLeft.Show(false);
        Widget nativeHeldItem = m_Root.FindAnyWidget("ia_item");
        if (nativeHeldItem)
            nativeHeldItem.Show(false);
        Widget nativeWeaponDetails = m_Root.FindAnyWidget("ia_item_subdesc");
        if (nativeWeaponDetails)
            nativeWeaponDetails.Show(false);
    }
}
