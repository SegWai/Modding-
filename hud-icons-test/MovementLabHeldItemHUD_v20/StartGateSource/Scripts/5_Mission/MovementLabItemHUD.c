// Replace only held-item readout; native interaction prompts remain.
modded class ItemActionsWidget
{
    override protected void Update()
    {
        super.Update();
        if (m_Hud && m_ItemLeft && MovementLabStartGate.Enabled && m_Hud.MovementLabHeldPanelReady())
            m_ItemLeft.Show(false);
    }
}
