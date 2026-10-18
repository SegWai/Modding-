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
    bool DeathCrawling;
    bool SourceFrozen;
    bool DeathArmsRaised;
    float DeathGait;

    void SampleMotion(int now)
    {
        if (!Body || !Body.IsAlive() || DeathConfirmed)
            return;
        vector position = Body.GetPosition();
        if (MotionReady)
        {
            int elapsed = now - MotionAt;
            if (elapsed < 80)
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
            vector nativeVelocity = GetVelocity(this);
            vector velocity = "0 0 0";
            string source = "none";
            int age = now - m_MovementLabInfectedSlot.VelocityAt;
            // Animated AI controller velocity can be nonzero yet far smaller
            // than the movement visible in the world. Prefer measured motion.
            if (m_MovementLabInfectedSlot.VelocityAt > 0 && age <= 150)
            {
                velocity = m_MovementLabInfectedSlot.LastVelocity;
                source = "world_motion";
            }
            else if (nativeVelocity.Length() <= 20.0)
            {
                velocity = nativeVelocity;
                source = "native_fallback";
            }
            m_MovementLabInfectedSlot.DeathCrawling = IsCrawling();
            m_MovementLabInfectedSlot.DeathArmsRaised = false;
            m_MovementLabInfectedSlot.DeathGait = Math.Clamp(m_MovementSpeed, 0.0, 3.0);
            if (!m_MovementLabInfectedSlot.DeathCrawling)
            {
                int pelvisIndex = GetBoneIndexByName("Pelvis");
                int leftIndex = GetBoneIndexByName("LeftHand");
                int rightIndex = GetBoneIndexByName("RightHand");
                if (pelvisIndex != -1 && leftIndex != -1 && rightIndex != -1)
                {
                    vector pelvis = GetBonePositionMS(pelvisIndex);
                    vector left = GetBonePositionMS(leftIndex);
                    vector right = GetBonePositionMS(rightIndex);
                    m_MovementLabInfectedSlot.DeathArmsRaised = left[1] > pelvis[1] + 0.12 || right[1] > pelvis[1] + 0.12;
                }
            }
            Print("[MLCORPSE104] stage=source_pose crawling=" + m_MovementLabInfectedSlot.DeathCrawling + " raisedArms=" + m_MovementLabInfectedSlot.DeathArmsRaised + " gait=" + m_MovementLabInfectedSlot.DeathGait);
            m_MovementLabInfectedSlot.DeathVelocity = velocity;
            m_MovementLabInfectedSlot.DeathPosition = GetPosition();
            m_MovementLabInfectedSlot.DeathOrientation = GetOrientation();
            Print("[MLCORPSE104] stage=death_capture velocity=" + velocity + " source=" + source + " worldVelocity=" + m_MovementLabInfectedSlot.LastVelocity + " nativeVelocity=" + nativeVelocity + " sampleAge=" + age);
        }
        super.EEKilled(killer);
        if (m_MovementLabInfectedSlot && !GetGame().IsMultiplayer() && !m_MovementLabInfectedSlot.DeathConfirmed)
        {
            // Preserve the source's evaluated pose while the hidden actor
            // initializes. Do not let native death animation stand it up.
            DisableSimulation(true);
            m_MovementLabInfectedSlot.SourceFrozen = true;
            m_MovementLabInfectedSlot.DeathConfirmed = true;
            m_MovementLabInfectedSlot.RespawnAt = GetGame().GetTime() + 5000;
            Print("[MovementLab Infected Death] Confirmed kill; replacement in five seconds.");
        }
    }
}
