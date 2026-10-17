// Experimental native-human ragdoll driver for a frozen infected visual.
// No native infected death-animation mode is changed.
modded class PlayerBase
{
    protected bool m_MovementLabZombiePhysicsDriver;

    void MovementLabMakeZombiePhysicsDriver()
    {
        m_MovementLabZombiePhysicsDriver = true;
        SetInvisible(true);
        SetHealth("", "Health", 0);
        DisableSimulation(false);
        PhysicsSetRagdoll(true);
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
            return true;
        return super.HandleDeath(pCurrentCommandID);
    }
}

class MovementLabZombieRagdoll
{
    protected PlayerBase m_Driver;
    protected ZombieBase m_Visual;
    protected ref array<int> m_SourceBones = new array<int>();
    protected ref array<int> m_TargetBones = new array<int>();
    protected int m_OriginalLayer;
    protected bool m_VisualSuspended;
    protected int m_ActivationDeadline;
    protected vector m_InitialVelocity;

    bool Start(ZombieBase corpse, vector velocityAtDeath)
    {
        if (!corpse || corpse.IsAlive() || GetGame().IsMultiplayer())
            return false;
        m_Visual = corpse;
        Object created = GetGame().CreatePlayer(null, "SurvivorM_Denis", corpse.GetPosition(), 0, "NONE");
        m_Driver = PlayerBase.Cast(created);
        if (!m_Driver)
        {
            if (created)
                GetGame().ObjectDelete(created);
            return false;
        }
        m_Driver.SetInvisible(true);
        m_Driver.SetOrientation(corpse.GetOrientation());
        array<string> names = {"Pelvis", "Spine", "Spine1", "Spine2", "Spine3", "Neck", "Head", "LeftShoulder", "LeftArm", "LeftArmRoll", "LeftForeArm", "LeftForeArmRoll", "LeftHand", "RightShoulder", "RightArm", "RightArmRoll", "RightForeArm", "RightForeArmRoll", "RightHand", "LeftUpLeg", "LeftUpLegRoll", "LeftLeg", "LeftLegRoll", "LeftFoot", "LeftToeBase", "RightUpLeg", "RightUpLegRoll", "RightLeg", "RightLegRoll", "RightFoot", "RightToeBase"};
        for (int i = 0; i < names.Count(); i++)
        {
            int source = m_Driver.GetBoneIndexByName(names[i]);
            int target = corpse.GetBoneIndex(names[i]);
            if (source >= 0 && target >= 0)
            {
                m_SourceBones.Insert(source);
                m_TargetBones.Insert(target);
            }
        }
        // Require head, pelvis and both arms/legs before altering the corpse.
        array<string> required = {"Pelvis", "Head", "LeftArm", "RightArm", "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg"};
        bool compatible = m_SourceBones.Count() >= 12;
        for (int key = 0; key < required.Count(); key++)
        {
            if (m_Driver.GetBoneIndexByName(required[key]) < 0 || corpse.GetBoneIndex(required[key]) < 0)
                compatible = false;
        }
        if (!compatible)
        {
            Print("[MovementLab Zombie Ragdoll] Incompatible bone map; matched=" + m_SourceBones.Count() + "; native corpse retained.");
            Stop();
            return false;
        }
        // Initialize the driver from the infected's last pose, then hand control
        // to the real Human ragdoll, rather than a scripted fall animation.
        for (int pose = 0; pose < m_SourceBones.Count(); pose++)
        {
            vector initial[4];
            corpse.GetBoneTransformMS(m_TargetBones[pose], initial);
            SetBoneGlobal(m_Driver, m_SourceBones[pose], initial);
        }
        m_Driver.MovementLabMakeZombiePhysicsDriver();
        // Activation can take a native simulation tick. Keep the existing
        // corpse untouched until the driver confirms an actual ragdoll state.
        m_ActivationDeadline = GetGame().GetTime() + 500;
        m_InitialVelocity = velocityAtDeath;
        return true;
    }

    void Update()
    {
        if (!m_Driver || !m_Visual)
            return;
        if (!m_VisualSuspended)
        {
            if (!m_Driver.PhysicsIsRagdoll())
            {
                if (GetGame().GetTime() >= m_ActivationDeadline)
                {
                    Print("[MovementLab Zombie Ragdoll] Native driver failed to activate within 500ms; native corpse retained.");
                    Stop();
                }
                return;
            }
            m_OriginalLayer = dBodyGetInteractionLayer(m_Visual);
            m_Visual.DisableSimulation(true);
            dBodySetInteractionLayer(m_Visual, 0);
            m_VisualSuspended = true;
            if (m_InitialVelocity.Length() > 0.01)
                dBodyApplyImpulse(m_Driver, m_InitialVelocity * 80.0);
            Print("[MovementLab Zombie Ragdoll] Actual human ragdoll state confirmed; infected bone driver active.");
        }
        vector world[4];
        m_Driver.GetTransform(world);
        m_Visual.SetTransform(world);
        for (int i = 0; i < m_SourceBones.Count(); i++)
        {
            vector pose[4];
            m_Driver.GetBoneTransformMS(m_SourceBones[i], pose);
            SetBoneGlobal(m_Visual, m_TargetBones[i], pose);
        }
    }

    void Stop()
    {
        if (m_Visual && m_VisualSuspended)
        {
            dBodySetInteractionLayer(m_Visual, m_OriginalLayer);
            m_Visual.DisableSimulation(false);
        }
        m_VisualSuspended = false;
        if (m_Driver)
            GetGame().ObjectDelete(m_Driver);
        m_Driver = null;
        m_Visual = null;
    }
}
