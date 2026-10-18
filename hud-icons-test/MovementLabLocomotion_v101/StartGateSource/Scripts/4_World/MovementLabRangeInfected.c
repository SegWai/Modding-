// One tracked offline infected. Preserve native AI and death behaviour.
class MovementLabInfectedSlot
{
    ZombieBase Body;
    string ClassName;
    vector SpawnPosition;
    int RespawnAt;
    bool DeathConfirmed;
    bool MissingLogged;
    bool CorpseAttempted;
    bool MotionReady;
    int MotionAt;
    int VelocityAt;
    vector MotionPosition;
    vector LastVelocity;
    vector DeathVelocity;
    vector DeathPosition;
    vector DeathOrientation;

    void SampleMotion(int now)
    {
        if (!Body || !Body.IsAlive() || DeathConfirmed)
            return;
        vector position = Body.GetPosition();
        if (MotionReady)
        {
            int elapsed = now - MotionAt;
            if (elapsed < 20)
                return;
            if (elapsed <= 200)
            {
                vector velocity = (position - MotionPosition) * (1000.0 / elapsed);
                if (velocity.Length() <= 20.0)
                {
                    LastVelocity = velocity;
                    VelocityAt = now;
                }
                else
                {
                    LastVelocity = "0 0 0";
                    VelocityAt = 0;
                }
            }
        }
        MotionPosition = position;
        MotionAt = now;
        MotionReady = true;
    }
    ref MovementLabConfiguredCorpse Corpse;
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
        // Capture before the native death handler can clear controller velocity.
        if (m_MovementLabInfectedSlot && !GetGame().IsMultiplayer() && !m_MovementLabInfectedSlot.DeathConfirmed)
        {
            int now = GetGame().GetTime();
            vector velocity = GetVelocity(this);
            if (velocity.Length() < 0.05 || velocity.Length() > 20.0)
            {
                velocity = "0 0 0";
                if (m_MovementLabInfectedSlot.VelocityAt > 0 && now - m_MovementLabInfectedSlot.VelocityAt <= 150)
                    velocity = m_MovementLabInfectedSlot.LastVelocity;
            }
            m_MovementLabInfectedSlot.DeathVelocity = velocity;
            m_MovementLabInfectedSlot.DeathPosition = GetPosition();
            m_MovementLabInfectedSlot.DeathOrientation = GetOrientation();
            Print("[MLCORPSE101] stage=death_capture velocity=" + velocity + " sampleAge=" + (now - m_MovementLabInfectedSlot.VelocityAt));
        }
        super.EEKilled(killer);
        if (m_MovementLabInfectedSlot && !GetGame().IsMultiplayer() && !m_MovementLabInfectedSlot.DeathConfirmed)
        {
            m_MovementLabInfectedSlot.DeathConfirmed = true;
            m_MovementLabInfectedSlot.RespawnAt = GetGame().GetTime() + 5000;
            Print("[MovementLab Infected Death] Confirmed kill; replacement in five seconds.");
        }
    }
}
