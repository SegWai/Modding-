// Keep existing test weight exemption; stamina depletion/recovery is fully native.
modded class StaminaHandler
{
    override void RecalculateStaminaCap()
    {
        if (MovementLabStartGate.Enabled && !GetGame().IsMultiplayer())
        {
            m_StaminaCap = CfgGameplayHandler.GetStaminaMax();
            m_StaminaCapSynced = m_StaminaCap;
            return;
        }
        super.RecalculateStaminaCap();
    }
}

modded class PlayerBase
{
    override bool IsOverloaded()
    {
        if (MovementLabStartGate.Enabled && !GetGame().IsMultiplayer())
            return false;
        return super.IsOverloaded();
    }
}
