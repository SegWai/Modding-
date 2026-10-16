// Offline range fixtures only. Never change the selected player's damage rules.
modded class PlayerBase
{
    protected bool m_MovementLabRangeTarget;
    protected bool m_MovementLabRangeNonlethal;
    protected int m_MovementLabRangeRagdollOffAt;
    protected bool m_MovementLabRangeRagdollStopped;
    protected bool m_MovementLabRangeKnockoutPending;
    protected bool m_MovementLabRangeStandingRecovery;
    protected int m_MovementLabRangeWakeAt;
    protected float m_MovementLabRangeRemainingHealth;
    protected float m_MovementLabRangeQueuedDamage;

    void MovementLabSetRangeTarget(bool nonlethal = false)
    {
        m_MovementLabRangeTarget = true;
        m_MovementLabRangeNonlethal = nonlethal;
        m_MovementLabRangeRemainingHealth = GetMaxHealth("", "Health");
        // Living, conscious targets must retain their native animated pose.
        PhysicsSetRagdoll(false);
    }

    override bool EEOnDamageCalculated(TotalDamageResult damageResult, int damageType, EntityAI source, int component, string dmgZone, string ammo, vector modelPos, float speedCoef)
    {
        if (m_MovementLabRangeTarget && m_MovementLabRangeNonlethal && !GetGame().IsMultiplayer())
        {
            // Keep incoming engine-calculated damage/mitigation, but apply only
            // global health ourselves. Veto engine zone/shock/blood damage so a
            // fatal head zone cannot kill this reusable nonlethal range target.
            if (!m_MovementLabRangeKnockoutPending && !m_MovementLabRangeStandingRecovery && !IsUnconscious() && damageResult)
            {
                float hitDamage = damageResult.GetDamage("", "Health");
                if (hitDamage <= 0 && dmgZone != "")
                    hitDamage = damageResult.GetDamage(dmgZone, "Health");
                if (hitDamage <= 0)
                    hitDamage = damageResult.GetHighestDamage("Health");
                // Queue changes outside the pre-damage callback: the engine
                // veto must not overwrite manually adjusted global health.
                if (hitDamage > 0)
                    m_MovementLabRangeQueuedDamage += hitDamage;
                Print("[MovementLab Female Hit] zone=" + dmgZone + " healthDamage=" + hitDamage + " queued=" + m_MovementLabRangeQueuedDamage);

            }
            return false;
        }
        return super.EEOnDamageCalculated(damageResult, damageType, source, component, dmgZone, ammo, modelPos, speedCoef);
    }

    override void EEKilled(Object killer)
    {
        if (m_MovementLabRangeTarget && !m_MovementLabRangeNonlethal && !GetGame().IsMultiplayer())
        {
            PhysicsSetRagdoll(true);
            m_MovementLabRangeRagdollOffAt = GetGame().GetTime() + 4000;
        }
        super.EEKilled(killer);
    }

    override bool HandleDeath(int pCurrentCommandID)
    {
        if (m_MovementLabRangeTarget && !m_MovementLabRangeNonlethal && !GetGame().IsMultiplayer() && !IsAlive())
        {
            // Keep the existing physics body; don't replace it with a native
            // death-animation command before the four-second switch-off.
            return true;
        }
        return super.HandleDeath(pCurrentCommandID);
    }

    void MovementLabUpdateRangeRagdoll()
    {
        if (!m_MovementLabRangeTarget || GetGame().IsMultiplayer())
            return;
        if (!m_MovementLabRangeNonlethal && !IsAlive() && !m_MovementLabRangeRagdollStopped && m_MovementLabRangeRagdollOffAt > 0 && GetGame().GetTime() >= m_MovementLabRangeRagdollOffAt)
        {
            PhysicsSetRagdoll(false);
            DisableSimulation(true);
            m_MovementLabRangeRagdollStopped = true;
        }
    }

    override void OnUnconsciousStart()
    {
        super.OnUnconsciousStart();
        if (m_MovementLabRangeTarget && m_MovementLabRangeNonlethal && !GetGame().IsMultiplayer())
        {
            PhysicsSetRagdoll(true);
            m_MovementLabRangeWakeAt = GetGame().GetTime() + 5000;
            m_MovementLabRangeKnockoutPending = false;
        }
    }

    void MovementLabUpdateRangeRecovery()
    {
        if (!m_MovementLabRangeTarget || !m_MovementLabRangeNonlethal || GetGame().IsMultiplayer() || !IsAlive())
            return;
        if (m_MovementLabRangeQueuedDamage > 0)
        {
            if (!IsUnconscious() && !m_MovementLabRangeStandingRecovery && m_MovementLabRangeWakeAt == 0)
            {
                m_MovementLabRangeRemainingHealth -= m_MovementLabRangeQueuedDamage;
                if (m_MovementLabRangeRemainingHealth <= 0)
                {
                    SetHealth("", "Health", 1);
                    m_MovementLabRangeKnockoutPending = true;
                }
                else
                    SetHealth("", "Health", m_MovementLabRangeRemainingHealth);
            }
            m_MovementLabRangeQueuedDamage = 0;
        }
        if (m_MovementLabRangeKnockoutPending && !GetCommand_Unconscious())
        {
            SetHealth("", "Shock", 0);
            m_ShouldBeUnconscious = true;
            // These targets have no controlling client. Explicitly start the
            // native command rather than waiting for a controller transition.
            HumanCommandUnconscious unconscious = StartCommand_Unconscious(0);
            if (unconscious)
            {
                m_IsUnconscious = true;
                OnUnconsciousStart();
                Print("[MovementLab Female KO] Native unconscious command started; wake in five seconds.");
            }
        }
        GetStatWater().Set(GetStatWater().GetMax());
        GetStatEnergy().Set(GetStatEnergy().GetMax());
        if (m_MovementLabRangeKnockoutPending || m_MovementLabRangeWakeAt > 0)
        {
            if (m_MovementLabRangeWakeAt == 0 || GetGame().GetTime() < m_MovementLabRangeWakeAt)
            {
                SetHealth("", "Shock", 0);
                m_ShouldBeUnconscious = true;
                return;
            }
            // Restore animated control before the native wake/stand sequence.
            // Full physics ragdoll cannot keep a conscious target upright.
            PhysicsSetRagdoll(false);
            SetHealthMax("", "Health");
            m_MovementLabRangeRemainingHealth = GetMaxHealth("", "Health");
            SetHealthMax("", "Blood");
            SetHealthMax("", "Shock");
            m_ShouldBeUnconscious = false;
            HumanCommandUnconscious wakeCommand = GetCommand_Unconscious();
            if (wakeCommand)
                wakeCommand.WakeUp(DayZPlayerConstants.STANCEIDX_ERECT);
            m_IsUnconscious = false;
            OnUnconsciousStop(DayZPlayerConstants.COMMANDID_UNCONSCIOUS);
            Print("[MovementLab Female Wake] Five seconds elapsed; health restored and upright recovery requested.");
            m_MovementLabRangeWakeAt = 0;
            m_MovementLabRangeStandingRecovery = true;
        }
        if (m_MovementLabRangeStandingRecovery)
        {
            SetHealthMax("", "Shock");
            m_ShouldBeUnconscious = false;
            if (!IsUnconscious())
            {
                HumanCommandMove move = GetCommand_Move();
                if (move)
                {
                    HumanMovementState state = new HumanMovementState();
                    GetMovementState(state);
                    if (state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT)
                    {
                        move.ForceStance(-1);
                        m_MovementLabRangeStandingRecovery = false;
                    }
                    else
                        move.ForceStanceUp(DayZPlayerConstants.STANCEIDX_ERECT);
                }
            }
        }
    }
}
