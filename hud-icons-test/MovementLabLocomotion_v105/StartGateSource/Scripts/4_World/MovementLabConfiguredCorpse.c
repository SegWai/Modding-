// Experimental corpse replacement: actual Human actor configured with the
// infected P3D before native creation. No hidden Human driver or bone writes.
class MovementLabHermitPhysicsCorpse : SurvivorBase
{
    protected bool m_MovementLabCorpsePublished;

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

    bool MovementLabInPronePose()
    {
        HumanMovementState state = new HumanMovementState();
        GetMovementState(state);
        return state.IsInProne() || state.IsInRaisedProne();
    }

    void MovementLabPrimeDeathPose(bool crawling, bool raisedArms, float gait)
    {
        if (!IsAlive())
            return;
        HumanCommandMove movement = GetCommand_Move();
        if (!movement)
            movement = StartCommand_Move();
        if (movement)
        {
            int stance = DayZPlayerConstants.STANCEIDX_ERECT;
            if (crawling)
                stance = DayZPlayerConstants.STANCEIDX_PRONE;
            else if (raisedArms)
                stance = DayZPlayerConstants.STANCEIDX_RAISEDERECT;
            movement.ForceStance(stance);
        }
        HumanInputController input = GetInputController();
        if (input)
        {
            input.OverrideRaise(HumanInputControllerOverrideType.ENABLED, raisedArms && !crawling);
            input.OverrideMovementAngle(HumanInputControllerOverrideType.ENABLED, 0);
            float poseGait = Math.Clamp(gait, 0.0, 3.0);
            if (crawling)
                poseGait = Math.Min(poseGait, 1.0);
            else if (raisedArms)
                poseGait = Math.Min(poseGait, 2.0);
            input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, poseGait);
        }
    }

    void MovementLabReleaseDeathPoseInput()
    {
        HumanInputController input = GetInputController();
        if (input)
        {
            input.OverrideRaise(HumanInputControllerOverrideType.DISABLED, false);
            input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
            input.OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
        }
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

    bool Start(ZombieBase original, vector deathPosition, vector deathOrientation, vector deathVelocity, bool crawling, bool raisedArms, float gait, bool sourceFrozen, vector deathPelvisWorld, bool deathPelvisValid)
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
            Print("[MLCORPSE105] stage=failed reason=create_or_script_class");
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
        m_Corpse.MovementLabPrimeDeathPose(m_DeathCrawling, m_DeathArmsRaised, m_DeathGait);
        // Wait for the requested native pose, not a default standing skeleton.
        m_CreatedAt = GetGame().GetTime();
        m_Deadline = m_CreatedAt + 1000;
        if (m_DeathCrawling)
            m_Deadline = m_CreatedAt + 2000;
        Print("[MLCORPSE105] stage=warming type=" + m_Corpse.GetType() + " shape=" + m_Corpse.GetShapeName() + " velocity=" + m_DeathVelocity);
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
            Print("[MLCORPSE105] stage=failed reason=native_mesh_mismatch shape=" + shape);
            Stop();
            return;
        }
        if (!m_Activated)
        {
            int now = GetGame().GetTime();
            m_Corpse.MovementLabPrimeDeathPose(m_DeathCrawling, m_DeathArmsRaised, m_DeathGait);
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
            if (m_DeathCrawling)
            {
                // No erect fallback for a crawler: retain its original corpse
                // if the low native pose cannot be established in time.
                // Model-space Y includes animation/root offsets; it is not
                // distance from the ground. Check stance and torso direction.
                vector torso = head - pelvis;
                bool horizontalTorso = torso[1] * torso[1] < torso[0] * torso[0] + torso[2] * torso[2];
                bool lowPose = headIndex != -1 && pelvisIndex != -1 && head.Length() > 0.05 && head.Length() < 3 && pelvis.Length() > 0.05 && pelvis.Length() < 3 && horizontalTorso && m_Corpse.MovementLabInPronePose();
                if (!lowPose)
                    m_ProneStableAt = -1;
                else if (m_ProneStableAt < 0 || vector.Distance(head, m_ProneStableHead) > 0.025 || vector.Distance(pelvis, m_ProneStablePelvis) > 0.025)
                {
                    m_ProneStableAt = now;
                    m_ProneStableHead = head;
                    m_ProneStablePelvis = pelvis;
                }
                ready = lowPose && m_ProneStableAt >= 0 && now - m_ProneStableAt >= 100;
            }
            else if (m_DeathArmsRaised)
            {
                int leftIndex = m_Corpse.GetBoneIndexByName("LeftHand");
                int rightIndex = m_Corpse.GetBoneIndexByName("RightHand");
                if (leftIndex == -1 || rightIndex == -1)
                    ready = false;
                else
                {
                    vector left = m_Corpse.GetBonePositionMS(leftIndex);
                    vector right = m_Corpse.GetBonePositionMS(rightIndex);
                    m_SeedLeftHand = left;
                    m_SeedRightHand = right;
                    ready = ready && (left[1] > pelvis[1] + 0.12 || right[1] > pelvis[1] + 0.12);
                }
            }
            if (now - m_CreatedAt < 100 || !ready)
            {
                if (now >= m_Deadline)
                {
                    Print("[MLCORPSE105] stage=failed reason=animated_pose_not_ready head=" + head + " pelvis=" + pelvis + " nativeProne=" + m_Corpse.MovementLabInPronePose());
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
            vector activationPosition = m_DeathPosition;
            if (m_DeathCrawling && m_DeathPelvisValid)
            {
                vector pelvisOffsetWorld = m_Corpse.ModelToWorld(pelvis) - m_Corpse.GetPosition();
                activationPosition = m_DeathPelvisWorld - pelvisOffsetWorld;
                Print("[MLCORPSE105] stage=align_prone targetPelvis=" + m_DeathPelvisWorld + " root=" + activationPosition);
            }
            m_Corpse.SetPosition(activationPosition);
            m_Corpse.MovementLabReleaseDeathPoseInput();
            m_Corpse.SetAllowDamage(true);
            Print("[MLCORPSE105] stage=pose_seed crawling=" + m_DeathCrawling + " raisedArms=" + m_DeathArmsRaised + " left=" + m_SeedLeftHand + " right=" + m_SeedRightHand);
            m_Corpse.SetHealth("", "Health", 0);
            m_Corpse.DisableSimulation(false);
            m_Corpse.PhysicsSetRagdoll(true);
            m_Activated = true;
            m_Deadline = now + 500;
            Print("[MLCORPSE105] stage=activated head=" + head + " pelvis=" + pelvis + " crawling=" + m_DeathCrawling + " raisedArms=" + m_DeathArmsRaised + " gait=" + m_DeathGait);
        }
        if (!m_Replaced)
        {
            if (!m_Corpse.PhysicsIsRagdoll())
            {
                if (GetGame().GetTime() >= m_Deadline)
                {
                    Print("[MLCORPSE105] stage=failed reason=ragdoll_activation_timeout");
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
            Print("[MLCORPSE105] stage=momentum velocity=" + m_DeathVelocity + " previousVelocity=" + initialVelocity + " mass=" + mass + " impulse=" + impulse);
            m_Replaced = true;
            Visibility(m_Corpse, true);
            m_RevealedAt = GetGame().GetTime();
            m_RevealPelvis = m_Corpse.GetBonePositionWS(m_Corpse.GetBoneIndexByName("Pelvis"));
            Print("[MLCORPSE105] stage=revealed shape=" + shape + " ragdoll=" + m_Corpse.PhysicsIsRagdoll() + " position=" + m_Corpse.GetPosition());
        }
        int sinceReveal = GetGame().GetTime() - m_RevealedAt;
        if (m_Replaced && ((m_TraceStage == 0 && sinceReveal >= 100) || (m_TraceStage == 1 && sinceReveal >= 300)))
        {
            vector pelvisWorld = m_Corpse.GetBonePositionWS(m_Corpse.GetBoneIndexByName("Pelvis"));
            vector travel = pelvisWorld - m_RevealPelvis;
            Print("[MLCORPSE105] stage=followthrough elapsed=" + sinceReveal + " pelvisTravel=" + travel + " rootVelocity=" + GetVelocity(m_Corpse));
            m_TraceStage++;
        }
    }

    void Stop()
    {
        // Remove the replacement before restoring the original on a failure.
        if (m_Corpse)
        {
            m_Corpse.MovementLabReleaseDeathPoseInput();
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
