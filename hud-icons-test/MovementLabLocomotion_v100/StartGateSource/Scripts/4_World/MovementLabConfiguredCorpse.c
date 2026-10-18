// Experimental corpse replacement: actual Human actor configured with the
// infected P3D before native creation. No hidden Human driver or bone writes.
class MovementLabHermitPhysicsCorpse : SurvivorBase
{
    override bool HandleDeath(int pCurrentCommandID)
    {
        if (!IsAlive() && !GetGame().IsMultiplayer())
            return true;
        return super.HandleDeath(pCurrentCommandID);
    }

    override int GetHideIconMask()
    {
        return EInventoryIconVisibility.HIDE_VICINITY;
    }
}

class MovementLabConfiguredCorpse
{
    protected MovementLabHermitPhysicsCorpse m_Corpse;
    protected ZombieBase m_Original;
    protected bool m_Replaced;
    protected int m_Deadline;
    protected int m_OldLayer;

    protected void Visibility(EntityAI body, bool visible)
    {
        if (!body)
            return;
        if (visible)
        {
            body.SetInvisible(false);
            body.SetFlags(EntityFlags.VISIBLE, true);
            body.SetCameraMask(-1);
        }
        else
        {
            body.SetCameraMask(0);
            body.SetInvisible(true);
            body.ClearFlags(EntityFlags.VISIBLE, true);
        }
    }

    bool Start(ZombieBase original)
    {
        if (!original || original.IsAlive() || GetGame().IsMultiplayer())
            return false;
        m_Original = original;
        Object created = GetGame().CreatePlayer(null, "MovementLabHermitPhysicsCorpse", original.GetPosition(), 0, "NONE");
        m_Corpse = MovementLabHermitPhysicsCorpse.Cast(created);
        if (!m_Corpse)
        {
            if (created)
                GetGame().ObjectDelete(created);
            Print("[MLCORPSE100] stage=failed reason=create_or_script_class");
            return false;
        }
        Visibility(m_Corpse, false);
        m_Corpse.SetOrientation(original.GetOrientation());
        // Selections/textures belong to the actual configured infected mesh.
        TStringArray selections = original.GetHiddenSelections();
        for (int i = 0; i < selections.Count(); i++)
        {
            string texture = original.GetObjectTexture(i);
            string material = original.GetObjectMaterial(i);
            if (texture != "")
                m_Corpse.SetObjectTexture(i, texture);
            if (material != "")
                m_Corpse.SetObjectMaterial(i, material);
        }
        m_Corpse.SetHealth("", "Health", 0);
        m_Corpse.DisableSimulation(false);
        m_Corpse.PhysicsSetRagdoll(true);
        m_Deadline = GetGame().GetTime() + 500;
        Print("[MLCORPSE100] stage=created type=" + m_Corpse.GetType() + " shape=" + m_Corpse.GetShapeName() + " ragdoll=" + m_Corpse.PhysicsIsRagdoll());
        return true;
    }

    void Update()
    {
        if (!m_Corpse || !m_Original)
            return;
        string shape = m_Corpse.GetShapeName();
        shape.ToLower();
        if (shape.IndexOf("hermit_above0") < 0)
        {
            Print("[MLCORPSE100] stage=failed reason=native_mesh_mismatch shape=" + shape);
            Stop();
            return;
        }
        if (!m_Replaced)
        {
            if (!m_Corpse.PhysicsIsRagdoll())
            {
                if (GetGame().GetTime() >= m_Deadline)
                {
                    Print("[MLCORPSE100] stage=failed reason=ragdoll_activation_timeout");
                    Stop();
                }
                return;
            }
            // Hide the original first; never show two overlapping corpses.
            m_OldLayer = dBodyGetInteractionLayer(m_Original);
            Visibility(m_Original, false);
            m_Original.DisableSimulation(true);
            dBodySetInteractionLayer(m_Original, 0);
            m_Replaced = true;
            Visibility(m_Corpse, true);
            Print("[MLCORPSE100] stage=revealed shape=" + shape + " ragdoll=" + m_Corpse.PhysicsIsRagdoll() + " position=" + m_Corpse.GetPosition());
        }
    }

    void Stop()
    {
        // Remove the replacement before restoring the original on a failure.
        if (m_Corpse)
        {
            Visibility(m_Corpse, false);
            GetGame().ObjectDelete(m_Corpse);
        }
        m_Corpse = null;
        if (m_Original && m_Replaced)
        {
            m_Original.DisableSimulation(false);
            dBodySetInteractionLayer(m_Original, m_OldLayer);
            Visibility(m_Original, true);
        }
        m_Original = null;
        m_Replaced = false;
    }
}
