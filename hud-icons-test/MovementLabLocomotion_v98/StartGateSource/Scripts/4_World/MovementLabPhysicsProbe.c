// Read-only offline fixture inspection. Never creates or changes a physics body.
class MovementLabPhysicsProbe
{
    static void Observe(EntityAI target, string label)
    {
        if (!target || GetGame().IsMultiplayer())
            return;
        Snapshot(target, label + "_now");
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(Snapshot, 100, false, target, label + "_100ms");
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(Snapshot, 300, false, target, label + "_300ms");
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(Snapshot, 1000, false, target, label + "_1000ms");
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(Snapshot, 3000, false, target, label + "_3000ms");
    }

    static void Snapshot(EntityAI target, string label)
    {
        if (!target || GetGame().IsMultiplayer())
            return;
        string id = "[MLPHY96] type=" + target.GetType() + " event=" + label + " t=" + GetGame().GetTime();
        Print(id + " stage=begin alive=" + target.IsAlive() + " position=" + target.GetPosition());
        PlayerBase human = PlayerBase.Cast(target);
        if (human)
            Print(id + " stage=human ragdoll=" + human.PhysicsIsRagdoll());
        Print(id + " stage=before_GetPhysics");
        Physics body = target.GetPhysics();
        if (!body)
        {
            Print(id + " stage=complete root=none bones=-1");
            return;
        }
        Print(id + " stage=before_GetNumBones");
        int count = body.GetNumBones();
        Print(id + " stage=root bones=" + count + " dynamic=" + body.IsDynamic() + " kinematic=" + body.IsKinematic());
        // Bounds protect the test from excessive/invalid native counts.
        if (count < 0 || count > 256)
        {
            Print(id + " stage=complete root=invalid_count bones=" + count);
            return;
        }
        int present = 0;
        int dynamicCount = 0;
        int kinematicCount = 0;
        int limit = count;
        if (limit > 32)
            limit = 32;
        for (int i = 0; i < limit; i++)
        {
            Print(id + " stage=before_GetBone index=" + i);
            Physics bone = body.GetBone(i);
            if (!bone)
                continue;
            present++;
            bool dynamicBone = bone.IsDynamic();
            bool kinematicBone = bone.IsKinematic();
            if (dynamicBone)
                dynamicCount++;
            if (kinematicBone)
                kinematicCount++;
            Print(id + " stage=bone index=" + i + " dynamic=" + dynamicBone + " kinematic=" + kinematicBone);
        }
        Print(id + " stage=complete root=present bones=" + count + " sampled=" + limit + " present=" + present + " dynamic=" + dynamicCount + " kinematic=" + kinematicCount);
    }
}
