// Opt-in only for the five offline fixtures. Keep native AI and death execution.
modded class ZombieBase
{
    protected bool m_MovementLabRangePhysicsDeath;

    void MovementLabSetRangePhysicsDeath()
    {
        m_MovementLabRangePhysicsDeath = true;
    }

    override bool HandleDeath(int pCurrentCommandID)
    {
        if (m_MovementLabRangePhysicsDeath && !GetGame().IsMultiplayer() && !IsAlive())
            m_DeathType = DayZInfectedDeathAnims.ANIM_DEATH_IMPULSE;
        return super.HandleDeath(pCurrentCommandID);
    }
}
