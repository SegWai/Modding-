// Offline test only: keep native stamina processing, remove load cap and depletion.
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

    override protected void ProcessStaminaChanges(float deltaT, bool isServerOrSingleplayer)
    {
        if (MovementLabStartGate.Enabled && !GetGame().IsMultiplayer())
        {
            m_StaminaCap = CfgGameplayHandler.GetStaminaMax();
            m_StaminaCapSynced = m_StaminaCap;
            m_Stamina = m_StaminaCap;
            m_StaminaDepletion = 0;
            m_StaminaDelta = 0;
        }
        super.ProcessStaminaChanges(deltaT, isServerOrSingleplayer);
    }

    override void DepleteStaminaEx(EStaminaModifiers modifier, float dT = -1, float coef = 1.0)
    {
        if (MovementLabStartGate.Enabled && !GetGame().IsMultiplayer())
            return;
        super.DepleteStaminaEx(modifier, dT, coef);
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
