// Offline M67 blast impulse. Native explosion damage/particles/fuse stay intact.
class MovementLabGrenadeBlast
{
    static const float RADIUS = 8.0;
    static const float FULL_STRENGTH_RADIUS = 2.0;
    static const float REFERENCE_SPEED = 5.555556; // 20 km/h in m/s

    static float StrengthAtDistance(float distance)
    {
        return Math.Clamp((RADIUS - distance) / (RADIUS - FULL_STRENGTH_RADIUS), 0.0, 1.0);
    }

    static void Apply(vector center)
    {
        if (GetGame().IsMultiplayer() || !MovementLabStartGate.Enabled)
            return;
        array<Object> objects = new array<Object>();
        array<CargoBase> cargos = new array<CargoBase>();
        GetGame().GetObjectsAtPosition3D(center, RADIUS + 1.0, objects, cargos);
        for (int i = 0; i < objects.Count(); i++)
        {
            EntityAI target = EntityAI.Cast(objects[i]);
            if (!target || (!PlayerBase.Cast(target) && !ZombieBase.Cast(target)))
                continue;
            vector targetPoint = target.GetPosition() + "0 0.8 0";
            float distance = vector.Distance(center, targetPoint);
            float strength = StrengthAtDistance(distance);
            if (strength <= 0)
                continue;

            // Don't push characters through solid cover. Ignore the target
            // itself so its own geometry doesn't block the trace.
            vector traceFrom = center + "0 0.15 0";
            vector contactPosition;
            vector contactNormal;
            int contactComponent;
            if (DayZPhysics.RaycastRV(traceFrom, targetPoint, contactPosition, contactNormal, contactComponent, null, null, target, false, false, ObjIntersectFire))
                continue;

            vector direction = targetPoint - center;
            direction[1] = 0;
            if (direction.Length() < 0.001)
                direction = "0 0 1";
            direction.Normalize();
            // Same scale as native transport-hit corpse impulse:
            // 40 * impact velocity, plus 40 * 1.5 vertical lift.
            vector impulse = direction * (40.0 * REFERENCE_SPEED * strength);
            impulse[1] = 60.0 * strength;
            dBodyActive(target, ActiveState.ACTIVE);
            dBodyApplyImpulse(target, impulse);
            Print("[MovementLab Blast] target=" + target.GetType() + " alive=" + target.IsAlive() + " distance=" + distance + " impulse=" + impulse);
        }
    }
}

modded class M67Grenade
{
    protected bool m_MovementLabBlastQueued;

    protected override void InitiateExplosion()
    {
        vector blastPosition = GetPosition();
        bool addImpulse = !m_MovementLabBlastQueued && !GetGame().IsMultiplayer() && MovementLabStartGate.Enabled;
        m_MovementLabBlastQueued = true;
        super.InitiateExplosion();
        if (addImpulse)
        {
            // Let explosion damage and NPC knockdown/death handlers run first.
            // Static callback keeps working after the grenade is deleted.
            GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(MovementLabGrenadeBlast.Apply, 150, false, blastPosition);
        }
    }
}
