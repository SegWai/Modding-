// A fixed slot persists across its own deaths. Missing references are NOT deaths.
class MovementLabInfectedSlot
{
    ZombieBase Body;
    string ClassName;
    vector SpawnPosition;
    int RespawnAt;
    bool DeathConfirmed;
    bool MissingLogged;
}

modded class ZombieBase
{
    protected ref MovementLabInfectedSlot m_MovementLabInfectedSlot;
    protected bool m_MovementLabPhysicsDeathStarted;

    void MovementLabSetRangePhysicsDeath(MovementLabInfectedSlot slot)
    {
        m_MovementLabInfectedSlot = slot;
    }

    override void EEKilled(Object killer)
    {
        super.EEKilled(killer);
        if (m_MovementLabInfectedSlot && !GetGame().IsMultiplayer() && !m_MovementLabInfectedSlot.DeathConfirmed)
        {
            m_MovementLabInfectedSlot.DeathConfirmed = true;
            m_MovementLabInfectedSlot.RespawnAt = GetGame().GetTime() + 5000;
            // This is the infected engine's native physics/impulse death mode,
            // also used for native transport impacts. Not a Human collision toggle.
            m_DeathType = DayZInfectedDeathAnims.ANIM_DEATH_IMPULSE;
            StartCommand_Death(m_DeathType, m_DamageHitDirection);
            m_MovementLabPhysicsDeathStarted = true;
            m_MovementSpeed = -1;
            m_MindState = -1;
            SetSynchDirty();
            Print("[MovementLab Infected Death] " + GetType() + " confirmed killed; physics death started; replacement in five seconds.");
        }
    }

    override bool HandleDeath(int pCurrentCommandID)
    {
        if (m_MovementLabInfectedSlot && !GetGame().IsMultiplayer() && !IsAlive())
        {
            if (!m_MovementLabPhysicsDeathStarted)
            {
                m_DeathType = DayZInfectedDeathAnims.ANIM_DEATH_IMPULSE;
                StartCommand_Death(m_DeathType, m_DamageHitDirection);
                m_MovementLabPhysicsDeathStarted = true;
                m_MovementSpeed = -1;
                m_MindState = -1;
                SetSynchDirty();
            }
            return true;
        }
        return super.HandleDeath(pCurrentCommandID);
    }
}
