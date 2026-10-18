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
    protected int m_CorpseLayer;
    protected int m_CreatedAt;
    protected bool m_Activated;
    protected bool m_OriginalSuspended;
    protected vector m_DeathPosition;
    protected vector m_DeathVelocity;

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

    bool Start(ZombieBase original, vector deathPosition, vector deathOrientation, vector deathVelocity)
    {
        if (!original || original.IsAlive() || GetGame().IsMultiplayer())
            return false;
        m_Original = original;
        m_DeathPosition = deathPosition;
        m_DeathVelocity = deathVelocity;
        Object created = GetGame().CreatePlayer(null, "MovementLabHermitPhysicsCorpse", deathPosition, 0, "NONE");
        m_Corpse = MovementLabHermitPhysicsCorpse.Cast(created);
        if (!m_Corpse)
        {
            if (created)
                GetGame().ObjectDelete(created);
            Print("[MLCORPSE101] stage=failed reason=create_or_script_class");
            return false;
        }
        Visibility(m_Corpse, false);
        m_Corpse.SetOrientation(deathOrientation);
        m_CorpseLayer = dBodyGetInteractionLayer(m_Corpse);
        dBodySetInteractionLayer(m_Corpse, 0);
        m_Corpse.SetAllowDamage(false);
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
        // Let native animation create a valid standing skeleton before death.
        m_CreatedAt = GetGame().GetTime();
        m_Deadline = m_CreatedAt + 1000;
        Print("[MLCORPSE101] stage=warming type=" + m_Corpse.GetType() + " shape=" + m_Corpse.GetShapeName() + " velocity=" + m_DeathVelocity);
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
            Print("[MLCORPSE101] stage=failed reason=native_mesh_mismatch shape=" + shape);
            Stop();
            return;
        }
        if (!m_Activated)
        {
            int now = GetGame().GetTime();
            int headIndex = m_Corpse.GetBoneIndexByName("Head");
            int pelvisIndex = m_Corpse.GetBoneIndexByName("Pelvis");
            vector head;
            vector pelvis;
            if (headIndex != -1 && pelvisIndex != -1)
            {
                head = m_Corpse.GetBonePositionMS(headIndex);
                pelvis = m_Corpse.GetBonePositionMS(pelvisIndex);
            }
            bool ready = headIndex != -1 && pelvisIndex != -1 && head[1] > 0.8 && pelvis[1] > 0.3 && head[1] > pelvis[1] + 0.2;
            if (now <= m_CreatedAt || !ready)
            {
                if (now >= m_Deadline)
                {
                    Print("[MLCORPSE101] stage=failed reason=animated_pose_not_ready head=" + head + " pelvis=" + pelvis);
                    Stop();
                }
                return;
            }
            // Remove overlap before enabling the replacement's articulation.
            m_OldLayer = dBodyGetInteractionLayer(m_Original);
            Visibility(m_Original, false);
            m_Original.DisableSimulation(true);
            dBodySetInteractionLayer(m_Original, 0);
            m_OriginalSuspended = true;
            m_Corpse.SetPosition(m_DeathPosition);
            m_Corpse.SetAllowDamage(true);
            m_Corpse.SetHealth("", "Health", 0);
            m_Corpse.DisableSimulation(false);
            m_Corpse.PhysicsSetRagdoll(true);
            m_Activated = true;
            m_Deadline = now + 500;
            Print("[MLCORPSE101] stage=activated head=" + head + " pelvis=" + pelvis);
        }
        if (!m_Replaced)
        {
            if (!m_Corpse.PhysicsIsRagdoll())
            {
                if (GetGame().GetTime() >= m_Deadline)
                {
                    Print("[MLCORPSE101] stage=failed reason=ragdoll_activation_timeout");
                    Stop();
                }
                return;
            }
            dBodySetInteractionLayer(m_Corpse, m_CorpseLayer);
            // One impulse only, scaled by physical mass: J = m * delta-v.
            // Do not also SetVelocity or repeatedly propel the settled corpse.
            vector initialVelocity = GetVelocity(m_Corpse);
            float mass = dBodyGetMass(m_Corpse);
            if (mass <= 0 || mass > 500)
                mass = 73.9;
            vector impulse = (m_DeathVelocity - initialVelocity) * mass;
            dBodyActive(m_Corpse, ActiveState.ACTIVE);
            dBodyApplyImpulse(m_Corpse, impulse);
            Print("[MLCORPSE101] stage=momentum velocity=" + m_DeathVelocity + " previousVelocity=" + initialVelocity + " mass=" + mass + " impulse=" + impulse);
            m_Replaced = true;
            Visibility(m_Corpse, true);
            Print("[MLCORPSE101] stage=revealed shape=" + shape + " ragdoll=" + m_Corpse.PhysicsIsRagdoll() + " position=" + m_Corpse.GetPosition());
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
        if (m_Original && m_OriginalSuspended)
        {
            m_Original.DisableSimulation(false);
            dBodySetInteractionLayer(m_Original, m_OldLayer);
            Visibility(m_Original, true);
        }
        m_Original = null;
        m_Replaced = false;
        m_OriginalSuspended = false;
        m_Activated = false;
    }
}
