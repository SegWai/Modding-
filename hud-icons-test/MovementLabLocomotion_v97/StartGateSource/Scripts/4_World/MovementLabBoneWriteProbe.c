// Calibration of the infected render-bone write path, not a ragdoll simulation.
modded class ZombieBase
{
    protected bool m_MovementLabBoneWriteEnabled;
    protected bool m_MovementLabBoneWriteCaptured;
    protected int m_MovementLabBoneWriteLastMode;
    protected int m_MovementLabBoneWriteStart;
    protected int m_MovementLabBoneWriteIndex = -1;
    protected int m_MovementLabBoneWriteFrames;
    protected vector m_MovementLabBoneWriteBase[4];

    void MovementLabBeginBoneWriteProbe()
    {
        if (IsAlive() || GetGame().IsMultiplayer())
            return;
        m_MovementLabBoneWriteIndex = GetBoneIndex("Head");
        if (m_MovementLabBoneWriteIndex < 0)
            m_MovementLabBoneWriteIndex = GetBoneIndex("head");
        Print("[MLBONE97] stage=start headIndex=" + m_MovementLabBoneWriteIndex + " disabled=" + GetIsSimulationDisabled());
        if (m_MovementLabBoneWriteIndex < 0)
            return;
        m_MovementLabBoneWriteStart = GetGame().GetTime();
        m_MovementLabBoneWriteEnabled = true;
        // Leave native simulation enabled: disabling it can suppress visual work.
        SetEventMask(EntityEvent.POSTFRAME);
    }

    override void EOnPostFrame(IEntity other, int extra)
    {
        super.EOnPostFrame(other, extra);
        if (!m_MovementLabBoneWriteEnabled || IsAlive() || GetGame().IsMultiplayer())
            return;
        int elapsed = GetGame().GetTime() - m_MovementLabBoneWriteStart;
        if (elapsed < 300)
            return;
        if (elapsed >= 3300)
        {
            // Stop writes and let the native pose own the corpse again.
            m_MovementLabBoneWriteEnabled = false;
            Print("[MLBONE97] stage=finished frames=" + m_MovementLabBoneWriteFrames);
            return;
        }
        if (!m_MovementLabBoneWriteCaptured)
        {
            GetBoneTransformMS(m_MovementLabBoneWriteIndex, m_MovementLabBoneWriteBase);
            m_MovementLabBoneWriteCaptured = true;
            Print("[MLBONE97] stage=captured position=" + m_MovementLabBoneWriteBase[3]);
        }
        vector pose[4];
        for (int axis = 0; axis < 4; axis++)
            pose[axis] = m_MovementLabBoneWriteBase[axis];
        // Deliberately obvious, bounded marker: head up/down, 0..0.35 units.
        // Always use the cached baseline; no accumulated per-frame drift.
        float lift = 0.175 + 0.175 * Math.Sin((elapsed - 300) * 0.006283185);
        pose[3][1] = pose[3][1] + lift;
        int mode = 1;
        if (elapsed >= 1800)
            mode = 2;
        bool firstInMode = mode != m_MovementLabBoneWriteLastMode;
        bool accepted = false;
        if (mode == 1)
        {
            if (firstInMode)
                Print("[MLBONE97] stage=before_SetBoneMatrix");
            accepted = SetBoneMatrix(this, m_MovementLabBoneWriteIndex, pose);
        }
        else
        {
            if (firstInMode)
                Print("[MLBONE97] stage=before_SetBoneGlobal");
            SetBoneGlobal(this, m_MovementLabBoneWriteIndex, pose);
        }
        if (firstInMode)
        {
            vector readback[4];
            bool readable = GetBoneMatrix(this, m_MovementLabBoneWriteIndex, readback);
            vector modelReadback[4];
            GetBoneTransformMS(m_MovementLabBoneWriteIndex, modelReadback);
            Print("[MLBONE97] stage=write_result mode=" + mode + " matrixAccepted=" + accepted + " readable=" + readable + " requested=" + pose[3] + " matrixReadback=" + readback[3] + " modelReadback=" + modelReadback[3]);
            m_MovementLabBoneWriteLastMode = mode;
        }
        m_MovementLabBoneWriteFrames++;
    }
}
