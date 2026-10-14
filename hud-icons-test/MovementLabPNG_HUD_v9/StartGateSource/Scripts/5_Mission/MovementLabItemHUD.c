// Move only the equipped-item display; keep interaction prompts native.
modded class ItemActionsWidget
{
    override protected void Update()
    {
        super.Update();
        if (!m_Hud || !m_ItemLeft || !MovementLabStartGate.Enabled)
            return;
        Widget staminaAnchor = m_Hud.MovementLabGetStaminaAnchor();
        if (!staminaAnchor)
            return;
        float anchorX;
        float anchorY;
        float anchorW;
        float anchorH;
        staminaAnchor.GetScreenPos(anchorX, anchorY);
        staminaAnchor.GetScreenSize(anchorW, anchorH);
        m_ItemLeft.SetScreenPos(anchorX, anchorY + anchorH + 6);
    }
}
