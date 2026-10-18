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
        array<string> preferred = {"ZmbM_HermitSkinny_Beige"};
        array<string> used = new array<string>();
        for (int i = 0; i < 1; i++)
        {
            MovementLabInfectedSlot slot = new MovementLabInfectedSlot();
            slot.ClassName = SelectClass(preferred[i], used);
            if (slot.ClassName == "")
            {
                Print("[MovementLab Infected] ERROR: no distinct public infected class available.");
                continue;
            }
            used.Insert(slot.ClassName);
            float angle = 0;
            vector direction = forward * Math.Cos(angle) + right * Math.Sin(angle);
            slot.SpawnPosition = player.GetPosition() + direction * 20.0;
            slot.SpawnPosition[1] = GetGame().SurfaceY(slot.SpawnPosition[0], slot.SpawnPosition[2]) + 0.2;
            m_Slots.Insert(slot);
            SpawnOne(slot);
        }
    }

    protected string SelectClass(string preferred, array<string> used)
    {
        if (GetGame().ConfigGetInt("CfgVehicles " + preferred + " scope") == 2 && used.Find(preferred) < 0)
            return preferred;
        int count = GetGame().ConfigGetChildrenCount("CfgVehicles");
        for (int i = 0; i < count; i++)
        {
            string candidate;
            GetGame().ConfigGetChildName("CfgVehicles", i, candidate);
            if (candidate.IndexOf("Zmb") != 0 || used.Find(candidate) >= 0)
                continue;
            if (GetGame().ConfigGetInt("CfgVehicles " + candidate + " scope") == 2)
                return candidate;
        }
        return "";
    }

    protected void SpawnOne(MovementLabInfectedSlot slot)
    {
        // Refuse to create a second entity for an occupied slot.
        if (slot.Body)
            return;
        Object created = GetGame().CreateObjectEx(slot.ClassName, slot.SpawnPosition, ECE_PLACE_ON_SURFACE | ECE_INITAI | ECE_EQUIP_ATTACHMENTS);
        slot.Body = ZombieBase.Cast(created);
        slot.RespawnAt = 0;
        slot.DeathConfirmed = false;
        slot.MissingLogged = false;
        slot.CorpseAttempted = false;
        if (slot.Body)
        {
            slot.Body.SetAllowDamage(true);
            slot.Body.MovementLabSetRangeSlot(slot);
            Print("[MovementLab Infected] Spawned " + slot.ClassName + " at " + slot.SpawnPosition);
        }
        else
        {
            // A failed cast must never leave an untracked live zombie behind.
            if (created)
                GetGame().ObjectDelete(created);
            Print("[MovementLab Infected] ERROR creating " + slot.ClassName + "; no automatic retry without a confirmed death.");
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
            // Only EEKilled arms a timer. Null/missing/streamed references and
            // spawn failures never create another entity on a periodic timer.
            if (!slot.DeathConfirmed || slot.RespawnAt == 0)
            {
                if (!slot.Body && !slot.MissingLogged)
                {
                    slot.MissingLogged = true;
                    Print("[MovementLab Infected] Missing " + slot.ClassName + "; not replacing without EEKilled.");
                }
                continue;
            }
            if (!slot.CorpseAttempted && slot.Body && !slot.Body.IsAlive())
            {
                slot.CorpseAttempted = true;
                slot.Corpse = new MovementLabConfiguredCorpse();
                if (!slot.Corpse.Start(slot.Body))
                {
                    slot.Corpse.Stop();
                    slot.Corpse = null;
                }
            }
            if (slot.Corpse)
                slot.Corpse.Update();
            if (now < slot.RespawnAt)
                continue;
            if (slot.Body && slot.Body.IsAlive())
                continue;
            if (slot.Corpse)
                slot.Corpse.Stop();
            slot.Corpse = null;
            if (slot.Body)
                GetGame().ObjectDelete(slot.Body);
            slot.Body = null;
            slot.RespawnAt = 0;
            slot.DeathConfirmed = false;
            SpawnOne(slot);
        }
    }

    void Shutdown()
    {
        for (int i = 0; i < m_Slots.Count(); i++)
        {
            if (m_Slots[i].Corpse)
                m_Slots[i].Corpse.Stop();
            m_Slots[i].Corpse = null;
            if (m_Slots[i].Body)
                GetGame().ObjectDelete(m_Slots[i].Body);
        }
        m_Slots.Clear();
    }
}
