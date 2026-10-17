// One tracked offline infected. Preserve native AI and death behaviour.
class MovementLabInfectedSlot
{
    ZombieBase Body;
    string ClassName;
    vector SpawnPosition;
    int RespawnAt;
    bool DeathConfirmed;
    bool MissingLogged;
    bool RagdollAttempted;
    vector VelocityAtDeath;
    ref MovementLabZombieRagdoll Ragdoll;
}

modded class ZombieBase
{
    protected ref MovementLabInfectedSlot m_MovementLabInfectedSlot;

    void MovementLabSetRangeSlot(MovementLabInfectedSlot slot)
    {
        m_MovementLabInfectedSlot = slot;
    }

    override void EEKilled(Object killer)
    {
        super.EEKilled(killer);
        if (m_MovementLabInfectedSlot && !GetGame().IsMultiplayer() && !m_MovementLabInfectedSlot.DeathConfirmed)
        {
            m_MovementLabInfectedSlot.VelocityAtDeath = GetVelocity(this);
            m_MovementLabInfectedSlot.DeathConfirmed = true;
            m_MovementLabInfectedSlot.RespawnAt = GetGame().GetTime() + 5000;
            Print("[MovementLab Infected Death] Confirmed kill; replacement in five seconds.");
        }
    }
}
