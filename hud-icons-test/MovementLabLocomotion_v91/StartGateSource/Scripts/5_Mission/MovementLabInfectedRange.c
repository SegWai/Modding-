class MovementLabInfectedSlot
{
    ZombieBase Body;
    vector SpawnPosition;
    int RespawnAt;
}

class MovementLabInfectedRange
{
    protected ref array<ref MovementLabInfectedSlot> m_Slots = new array<ref MovementLabInfectedSlot>();

    void MovementLabInfectedRange(PlayerBase player)
    {
        vector forward = player.GetDirection();
        forward[1] = 0;
        if (forward.Length() < 0.001)
            forward = "0 0 1";
        forward.Normalize();
        vector right = Vector(forward[2], 0, -forward[0]);
        for (int i = 0; i < 5; i++)
        {
            MovementLabInfectedSlot slot = new MovementLabInfectedSlot();
            float angle = (i - 2) * 6.0 * Math.DEG2RAD;
            vector direction = forward * Math.Cos(angle) + right * Math.Sin(angle);
            slot.SpawnPosition = player.GetPosition() + direction * 20.0;
            slot.SpawnPosition[1] = GetGame().SurfaceY(slot.SpawnPosition[0], slot.SpawnPosition[2]) + 0.2;
            m_Slots.Insert(slot);
            SpawnOne(slot);
        }
    }

    protected void SpawnOne(MovementLabInfectedSlot slot)
    {
        slot.Body = ZombieBase.Cast(GetGame().CreateObjectEx("ZmbM_HermitSkinny_Beige", slot.SpawnPosition, ECE_PLACE_ON_SURFACE | ECE_INITAI | ECE_EQUIP_ATTACHMENTS));
        slot.RespawnAt = 0;
        if (slot.Body)
        {
            slot.Body.SetAllowDamage(true);
            slot.Body.MovementLabSetRangePhysicsDeath();
            Print("[MovementLab Infected] Spawned at " + slot.SpawnPosition);
        }
        else
        {
            // A failed spawn is retried, without creating one every frame.
            slot.RespawnAt = GetGame().GetTime() + 5000;
            Print("[MovementLab Infected] ERROR spawning fixture; retry in five seconds.");
        }
    }

    void Update()
    {
        if (GetGame().IsMultiplayer())
            return;
        int now = GetGame().GetTime();
        for (int i = 0; i < m_Slots.Count(); i++)
        {
            MovementLabInfectedSlot slot = m_Slots[i];
            if (slot.Body && slot.Body.IsAlive())
                continue;
            if (slot.RespawnAt == 0)
                slot.RespawnAt = now + 5000;
            if (now >= slot.RespawnAt)
            {
                if (slot.Body)
                    GetGame().ObjectDelete(slot.Body);
                slot.Body = null;
                SpawnOne(slot);
            }
        }
    }

    void Shutdown()
    {
        for (int i = 0; i < m_Slots.Count(); i++)
        {
            if (m_Slots[i].Body)
                GetGame().ObjectDelete(m_Slots[i].Body);
        }
        m_Slots.Clear();
    }
}
