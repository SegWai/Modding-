// Opt-in only for the offline range target; never alter the selected player.
modded class PlayerBase
{
    protected bool m_MovementLabRangeTarget;
    protected bool m_MovementLabRangeRagdollStarted;

    void MovementLabSetRangeTarget()
    {
        m_MovementLabRangeTarget = true;
    }

    override bool HandleDeath(int pCurrentCommandID)
    {
        if (m_MovementLabRangeTarget && !GetGame().IsMultiplayer() && !IsAlive())
        {
            if (!m_MovementLabRangeRagdollStarted)
            {
                m_MovementLabRangeRagdollStarted = true;
                PhysicsSetRagdoll(true);
                Print("[MovementLab Range NPC] Native physics ragdoll enabled on death.");
            }
            return true;
        }
        return super.HandleDeath(pCurrentCommandID);
    }
}
