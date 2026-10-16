// Offline range fixtures only. Never change the selected player's damage rules.
modded class PlayerBase
{
    protected bool m_MovementLabRangeTarget;
    protected bool m_MovementLabRangeNonlethal;
    protected bool m_MovementLabRangeKnockoutPending;
    protected bool m_MovementLabRangeStandingRecovery;
    protected int m_MovementLabRangeWakeAt;

    void MovementLabSetRangeTarget(bool nonlethal = false)
    {
        m_MovementLabRangeTarget = true;
        m_MovementLabRangeNonlethal = nonlethal;
    }

    override bool EEOnDamageCalculated(TotalDamageResult damageResult, int damageType, EntityAI source, int component, string dmgZone, string ammo, vector modelPos, float speedCoef)
    {
        if (m_MovementLabRangeTarget && m_MovementLabRangeNonlethal && !GetGame().IsMultiplayer())
        {
            // Cancel BEFORE health/zone damage is applied, including lethal
            // headshots. Repeated hits while down do not restart the timer.
            if (!m_MovementLabRangeKnockoutPending && !m_MovementLabRangeStandingRecovery && !IsUnconscious())
                m_MovementLabRangeKnockoutPending = true;
            return false;
        }
        return super.EEOnDamageCalculated(damageResult, damageType, source, component, dmgZone, ammo, modelPos, speedCoef);
    }

    override void OnUnconsciousStart()
    {
        super.OnUnconsciousStart();
        if (m_MovementLabRangeTarget && m_MovementLabRangeNonlethal && !GetGame().IsMultiplayer())
        {
            m_MovementLabRangeWakeAt = GetGame().GetTime() + 5000;
            m_MovementLabRangeKnockoutPending = false;
        }
    }

    void MovementLabUpdateRangeRecovery()
    {
        if (!m_MovementLabRangeTarget || !m_MovementLabRangeNonlethal || GetGame().IsMultiplayer() || !IsAlive())
            return;
        SetHealthMax("", "Health");
        SetHealthMax("", "Blood");
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
            // Native unconscious command handles recovery rather than switching
            // physics ragdoll on a live character (which can break waking).
            SetHealthMax("", "Shock");
            m_ShouldBeUnconscious = false;
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
