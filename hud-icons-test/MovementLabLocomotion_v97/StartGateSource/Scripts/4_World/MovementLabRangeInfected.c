// One tracked offline infected. Preserve native AI and death behaviour.
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

    void MovementLabSetRangeSlot(MovementLabInfectedSlot slot)
    {
        m_MovementLabInfectedSlot = slot;
        MovementLabPhysicsProbe.Observe(this, "infected_spawn");
    }

    override void EEKilled(Object killer)
    {
        super.EEKilled(killer);
        if (m_MovementLabInfectedSlot && !GetGame().IsMultiplayer() && !m_MovementLabInfectedSlot.DeathConfirmed)
        {
            m_MovementLabInfectedSlot.DeathConfirmed = true;
            m_MovementLabInfectedSlot.RespawnAt = GetGame().GetTime() + 5000;
            MovementLabPhysicsProbe.Observe(this, "infected_death");
            MovementLabBeginBoneWriteProbe();
            Print("[MovementLab Infected Death] Confirmed kill; replacement in five seconds.");
        }
    }
}
