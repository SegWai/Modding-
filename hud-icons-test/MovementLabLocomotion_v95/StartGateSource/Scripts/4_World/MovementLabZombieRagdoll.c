// Experimental: render the infected mesh ON the native Human ragdoll actor.
// v94's manual bone-copy path is intentionally removed.
modded class PlayerBase
{
    protected bool m_MovementLabZombiePhysicsDriver;
    protected bool m_MovementLabZombieMeshRevealed;

    void MovementLabZombieDriverVisibility(bool reveal)
    {
        m_MovementLabZombieMeshRevealed = reveal;
        if (reveal)
        {
            SetInvisible(false);
            SetCameraMask(-1);
            SetFlags(EntityFlags.VISIBLE, false);
        }
        else
        {
            SetInvisible(true);
            SetCameraMask(0);
            ClearFlags(EntityFlags.VISIBLE, true);
        }
    }

    void MovementLabMakeZombiePhysicsDriver()
    {
        m_MovementLabZombiePhysicsDriver = true;
        MovementLabZombieDriverVisibility(false);
        SetHealth("", "Health", 0);
        DisableSimulation(false);
        PhysicsSetRagdoll(true);
        MovementLabZombieDriverVisibility(false);
    }

    override int GetHideIconMask()
    {
        if (m_MovementLabZombiePhysicsDriver)
            return EInventoryIconVisibility.HIDE_VICINITY;
        return super.GetHideIconMask();
    }

    override bool HandleDeath(int pCurrentCommandID)
    {
        if (m_MovementLabZombiePhysicsDriver)
        {
            // Reassert render state after the native death/creation transition.
            MovementLabZombieDriverVisibility(m_MovementLabZombieMeshRevealed);
            return true;
        }
        return super.HandleDeath(pCurrentCommandID);
    }
}

class MovementLabZombieRagdoll
{
    protected PlayerBase m_Driver;
    protected ZombieBase m_Visual;
    protected vobject m_ZombieModel;
    protected int m_OriginalLayer;
    protected bool m_VisualSuspended;
    protected int m_ActivationDeadline;
    protected vector m_InitialVelocity;

    bool Start(ZombieBase corpse, vector velocityAtDeath)
    {
        if (!corpse || corpse.IsAlive() || GetGame().IsMultiplayer())
            return false;
        m_Visual = corpse;
        m_ZombieModel = corpse.GetVObject();
        if (!m_ZombieModel)
            return false;
        Object created = GetGame().CreatePlayer(null, "SurvivorM_Denis", corpse.GetPosition(), 0, "NONE");
        m_Driver = PlayerBase.Cast(created);
        if (!m_Driver)
        {
            if (created)
                GetGame().ObjectDelete(created);
            return false;
        }
        m_Driver.MovementLabZombieDriverVisibility(false);
        m_Driver.SetOrientation(corpse.GetOrientation());
        // SetObject adds a resource reference; the infected mesh stays resident
        // while this actor uses it. Its real Human physics rig stays on the actor.
        m_Driver.SetObject(m_ZombieModel, "");
        m_Driver.MovementLabZombieDriverVisibility(false);
        if (m_Driver.GetVObject() != m_ZombieModel)
        {
            Print("[MovementLab Zombie Ragdoll v95] Mesh swap rejected; original corpse retained.");
            Stop();
            return false;
        }
        TStringArray selections = corpse.GetHiddenSelections();
        for (int i = 0; i < selections.Count(); i++)
        {
            string texture = corpse.GetObjectTexture(i);
            string material = corpse.GetObjectMaterial(i);
            if (texture != "")
                m_Driver.SetObjectTexture(i, texture);
            if (material != "")
                m_Driver.SetObjectMaterial(i, material);
        }
        // No attempt to write a frozen infected skeleton's bones.
        m_Driver.MovementLabMakeZombiePhysicsDriver();
        m_ActivationDeadline = GetGame().GetTime() + 500;
        m_InitialVelocity = velocityAtDeath;
        return true;
    }

    void Update()
    {
        if (!m_Driver || !m_Visual)
            return;
        // Never reveal the default survivor if native code replaces its mesh.
        if (m_Driver.GetVObject() != m_ZombieModel)
        {
            Print("[MovementLab Zombie Ragdoll v95] Mesh changed away from infected; stopping proxy.");
            Stop();
            return;
        }
        if (!m_VisualSuspended)
        {
            m_Driver.MovementLabZombieDriverVisibility(false);
            if (!m_Driver.PhysicsIsRagdoll())
            {
                if (GetGame().GetTime() >= m_ActivationDeadline)
                {
                    Print("[MovementLab Zombie Ragdoll v95] Mesh-swap ragdoll failed to activate; original corpse retained.");
                    Stop();
                }
                return;
            }
            m_OriginalLayer = dBodyGetInteractionLayer(m_Visual);
            m_Visual.SetCameraMask(0);
            m_Visual.SetInvisible(true);
            m_Visual.ClearFlags(EntityFlags.VISIBLE, true);
            m_Visual.DisableSimulation(true);
            dBodySetInteractionLayer(m_Visual, 0);
            m_VisualSuspended = true;
            if (m_InitialVelocity.Length() > 0.01)
                dBodyApplyImpulse(m_Driver, m_InitialVelocity * 80.0);
            Print("[MovementLab Zombie Ragdoll v95] Infected mesh on actual ragdoll; original corpse hidden. Native mesh/rig deformation needs visual verification.");
        }
        // Camera masks/visible flags are explicit, unlike v94 SetInvisible alone.
        m_Visual.SetCameraMask(0);
        m_Visual.SetInvisible(true);
        m_Visual.ClearFlags(EntityFlags.VISIBLE, true);
        m_Driver.MovementLabZombieDriverVisibility(true);
    }

    void Stop()
    {
        // Delete/hide the replacement BEFORE restoring the original render state.
        if (m_Driver)
        {
            m_Driver.MovementLabZombieDriverVisibility(false);
            GetGame().ObjectDelete(m_Driver);
        }
        m_Driver = null;
        if (m_Visual && m_VisualSuspended)
        {
            dBodySetInteractionLayer(m_Visual, m_OriginalLayer);
            m_Visual.DisableSimulation(false);
            m_Visual.SetInvisible(false);
            m_Visual.SetFlags(EntityFlags.VISIBLE, true);
            m_Visual.SetCameraMask(-1);
        }
        m_VisualSuspended = false;
        m_Visual = null;
        m_ZombieModel = null;
    }
}
