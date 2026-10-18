// Experimental corpse replacement: actual Human actor configured with the
// infected P3D before native creation. No hidden Human driver or bone writes.
class MovementLabHermitPhysicsCorpse : SurvivorBase
{
    protected bool m_MovementLabCorpsePublished;
    // Scheduled code only queues values. Native animation writes must run
    // inside this actor's CommandHandler (DayZPlayer API contract).
    protected ref array<int> m_CapturedControlIDs = new array<int>();
    protected ref array<float> m_CapturedControlValues = new array<float>();
    protected int m_CapturedRevision;
    protected int m_CapturedAppliedRevision;
    protected int m_CapturedCommandTicks;

    void QueueCapturedPoseFloat(int variable, float value)
    {
        int index = m_CapturedControlIDs.Find(variable);
        if (index < 0)
        {
            m_CapturedControlIDs.Insert(variable);
            m_CapturedControlValues.Insert(value);
        }
        else
            m_CapturedControlValues[index] = value;
        m_CapturedRevision++;
    }

    int CapturedPoseAppliedRevision()
    {
        return m_CapturedAppliedRevision;
    }

    int CapturedPoseRevision()
    {
        return m_CapturedRevision;
    }

    int CapturedPoseCommandTicks()
    {
        return m_CapturedCommandTicks;
    }

    override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
    {
        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
        for (int i = 0; i < m_CapturedControlIDs.Count(); i++)
            AnimSetFloat(m_CapturedControlIDs[i], m_CapturedControlValues[i]);
        if (m_CapturedAppliedRevision != m_CapturedRevision)
            Print("[MLPOSE107] stage=command_flush revision=" + m_CapturedRevision + " controls=" + m_CapturedControlIDs.Count());
        m_CapturedAppliedRevision = m_CapturedRevision;
        m_CapturedCommandTicks++;
    }


    void MovementLabHermitPhysicsCorpse()
    {
        MovementLabSetCorpseVisible(false);
    }

    void MovementLabSetCorpseVisible(bool visible)
    {
        m_MovementLabCorpsePublished = visible;
        if (visible)
        {
            SetInvisible(false);
            SetFlags(EntityFlags.VISIBLE, true);
            SetCameraMask(-1);
        }
        else
        {
            SetCameraMask(0);
            SetInvisible(true);
            ClearFlags(EntityFlags.VISIBLE, true);
        }
    }

    override void EOnPostFrame(IEntity other, int extra)
    {
        super.EOnPostFrame(other, extra);
        if (!m_MovementLabCorpsePublished)
            MovementLabSetCorpseVisible(false);
    }

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
    protected ref MovementLabCapturedPoseBridge m_PoseBridge;
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
    protected bool m_DeathCrawling;
    protected bool m_DeathPelvisValid;
    protected vector m_DeathPelvisWorld;
    protected bool m_DeathArmsRaised;
    protected float m_DeathGait;
    protected vector m_SeedLeftHand;
    protected vector m_SeedRightHand;
    protected int m_ProneStableAt = -1;
    protected vector m_ProneStableHead;
    protected vector m_ProneStablePelvis;
    protected int m_RevealedAt;
    protected int m_TraceStage;
    protected vector m_RevealPelvis;

    protected void Visibility(EntityAI body, bool visible)
    {
        if (!body)
            return;
        MovementLabHermitPhysicsCorpse configured = MovementLabHermitPhysicsCorpse.Cast(body);
        if (configured)
        {
            configured.MovementLabSetCorpseVisible(visible);
            return;
        }
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

    bool Start(ZombieBase original, vector deathPosition, vector deathOrientation, vector deathVelocity, bool crawling, bool raisedArms, float gait, bool sourceFrozen, vector deathPelvisWorld, bool deathPelvisValid, MovementLabCapturedPose capturedPose)
    {
        if (!original || original.IsAlive() || GetGame().IsMultiplayer())
            return false;
        m_Original = original;
        m_OldLayer = dBodyGetInteractionLayer(original);
        m_OriginalSuspended = sourceFrozen;
        m_DeathPosition = deathPosition;
        m_DeathVelocity = deathVelocity;
        m_DeathCrawling = crawling;
        m_DeathPelvisWorld = deathPelvisWorld;
        m_DeathPelvisValid = deathPelvisValid;
        m_DeathArmsRaised = raisedArms && !crawling;
        m_DeathGait = gait;
        Object created = GetGame().CreatePlayer(null, "MovementLabHermitPhysicsCorpse", deathPosition, 0, "NONE");
        m_Corpse = MovementLabHermitPhysicsCorpse.Cast(created);
        if (!m_Corpse)
        {
            if (created)
                GetGame().ObjectDelete(created);
            Print("[MLCORPSE107] stage=failed reason=create_or_script_class");
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
        m_CreatedAt = GetGame().GetTime();
        m_Deadline = m_CreatedAt + 350;
        m_PoseBridge = new MovementLabCapturedPoseBridge();
        if (!m_PoseBridge.Begin(m_Corpse, capturedPose))
        {
            Print("[MLCORPSE107] stage=failed reason=pose_bridge_initialization");
            return false;
        }
        Print("[MLCORPSE107] stage=warming type=" + m_Corpse.GetType() + " shape=" + m_Corpse.GetShapeName() + " velocity=" + m_DeathVelocity);
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
            Print("[MLCORPSE107] stage=failed reason=native_mesh_mismatch shape=" + shape);
            Stop();
            return;
        }
        if (!m_Activated)
        {
            int now = GetGame().GetTime();
            if (!m_PoseBridge.Step())
            {
                if (now >= m_Deadline)
                {
                    m_PoseBridge.ReportFailure();
                    Print("[MLCORPSE107] stage=failed reason=captured_pose_not_matched_after_350ms");
                    Stop();
                }
                return;
            }
            int pelvisIndex = m_Corpse.GetBoneIndexByName("Pelvis");
            vector pelvis = m_Corpse.GetBonePositionMS(pelvisIndex);
            // Remove overlap before enabling the replacement's articulation.
            m_OldLayer = dBodyGetInteractionLayer(m_Original);
            Visibility(m_Original, false);
            m_Original.DisableSimulation(true);
            dBodySetInteractionLayer(m_Original, 0);
            m_OriginalSuspended = true;
            vector activationPosition = m_DeathPosition;
            if (m_DeathCrawling && m_DeathPelvisValid)
            {
                vector pelvisOffsetWorld = m_Corpse.ModelToWorld(pelvis) - m_Corpse.GetPosition();
                activationPosition = m_DeathPelvisWorld - pelvisOffsetWorld;
                Print("[MLCORPSE107] stage=align_prone targetPelvis=" + m_DeathPelvisWorld + " root=" + activationPosition);
            }
            m_Corpse.SetPosition(activationPosition);
            m_Corpse.SetAllowDamage(true);
            Print("[MLCORPSE107] stage=pose_seed matched_capture=true crawling=" + m_DeathCrawling);
            m_Corpse.SetHealth("", "Health", 0);
            m_Corpse.DisableSimulation(false);
            m_Corpse.PhysicsSetRagdoll(true);
            m_PoseBridge.ReportPhysicsSeed();
            m_Activated = true;
            m_Deadline = now + 500;
            Print("[MLCORPSE107] stage=activated pelvis=" + pelvis + " crawling=" + m_DeathCrawling + " matched_capture=true");
        }
        if (!m_Replaced)
        {
            if (!m_Corpse.PhysicsIsRagdoll())
            {
                if (GetGame().GetTime() >= m_Deadline)
                {
                    Print("[MLCORPSE107] stage=failed reason=ragdoll_activation_timeout");
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
            vector deltaVelocity = m_DeathVelocity - initialVelocity;
            // Transfer ground travel; don't cancel the new body's gravity.
            deltaVelocity[1] = 0;
            vector impulse = deltaVelocity * mass;
            dBodyActive(m_Corpse, ActiveState.ACTIVE);
            dBodyApplyImpulse(m_Corpse, impulse);
            Print("[MLCORPSE107] stage=momentum velocity=" + m_DeathVelocity + " previousVelocity=" + initialVelocity + " mass=" + mass + " impulse=" + impulse);
            m_Replaced = true;
            Visibility(m_Corpse, true);
            m_RevealedAt = GetGame().GetTime();
            m_RevealPelvis = m_Corpse.GetBonePositionWS(m_Corpse.GetBoneIndexByName("Pelvis"));
            Print("[MLCORPSE107] stage=revealed shape=" + shape + " ragdoll=" + m_Corpse.PhysicsIsRagdoll() + " position=" + m_Corpse.GetPosition());
        }
        int sinceReveal = GetGame().GetTime() - m_RevealedAt;
        if (m_Replaced && ((m_TraceStage == 0 && sinceReveal >= 100) || (m_TraceStage == 1 && sinceReveal >= 300)))
        {
            vector pelvisWorld = m_Corpse.GetBonePositionWS(m_Corpse.GetBoneIndexByName("Pelvis"));
            vector travel = pelvisWorld - m_RevealPelvis;
            Print("[MLCORPSE107] stage=followthrough elapsed=" + sinceReveal + " pelvisTravel=" + travel + " rootVelocity=" + GetVelocity(m_Corpse));
            m_TraceStage++;
        }
    }

    void Stop()
    {
        // Remove the replacement before restoring the original on a failure.
        if (m_Corpse)
        {
            Visibility(m_Corpse, false);
            if (m_PoseBridge)
                m_PoseBridge.Stop();
            GetGame().ObjectDelete(m_Corpse);
        }
        m_Corpse = null;
        m_PoseBridge = null;
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
