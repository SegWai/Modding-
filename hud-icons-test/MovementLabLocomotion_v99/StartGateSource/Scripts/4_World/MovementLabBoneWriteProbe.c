// Calibration of the infected render-bone write path, not a ragdoll simulation.
modded class ZombieBase
{
    protected bool m_MovementLabBoneWriteEnabled;
    protected bool m_MovementLabBoneWriteCaptured;
    protected int m_MovementLabBoneWriteLastMode;
    protected int m_MovementLabBoneWriteStart;
    protected int m_MovementLabBoneWriteIndex = -1;
    protected int m_MovementLabBoneWriteFrames;
    protected int m_MovementLabBoneWriteModelIndex = -1;
    protected vector m_MovementLabBoneWriteBase[4];

    void MovementLabBeginBoneWriteProbe()
    {
        if (IsAlive() || GetGame().IsMultiplayer())
            return;
        m_MovementLabBoneWriteIndex = GetBoneIndexByName("Head");
        if (m_MovementLabBoneWriteIndex < 0)
            m_MovementLabBoneWriteIndex = GetBoneIndexByName("head");
        int proxyIndex = GetBoneIndex("Head");
        m_MovementLabBoneWriteModelIndex = proxyIndex;
        Print("[MLBONE99] stage=lookup skeletalIndex=" + m_MovementLabBoneWriteIndex + " proxyIndex=" + proxyIndex);
        Print("[MLBONE99] stage=start headIndex=" + m_MovementLabBoneWriteIndex + " disabled=" + GetIsSimulationDisabled());
        if (m_MovementLabBoneWriteIndex < 0 || m_MovementLabBoneWriteModelIndex < 0)
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
            Print("[MLBONE99] stage=finished frames=" + m_MovementLabBoneWriteFrames);
            return;
        }
        if (!m_MovementLabBoneWriteCaptured)
        {
            GetBoneTransformMS(m_MovementLabBoneWriteIndex, m_MovementLabBoneWriteBase);
            vector bonePosition = GetBonePositionMS(m_MovementLabBoneWriteIndex);
            Print("[MLBONE99] stage=position_check positionMS=" + bonePosition + " matrixPosition=" + m_MovementLabBoneWriteBase[3] + " axis0=" + m_MovementLabBoneWriteBase[0]);
            // Never submit the all-zero basis observed in v97. Native matrix
            // reading may be unavailable even when bone-position reading works.
            if (m_MovementLabBoneWriteBase[0].Length() < 0.1 || m_MovementLabBoneWriteBase[1].Length() < 0.1 || m_MovementLabBoneWriteBase[2].Length() < 0.1)
            {
                if (bonePosition.Length() < 0.01)
                {
                    Print("[MLBONE99] stage=aborted reason=no_valid_bone_position_or_matrix");
                    m_MovementLabBoneWriteEnabled = false;
                    return;
                }
                Math3D.MatrixIdentity4(m_MovementLabBoneWriteBase);
                m_MovementLabBoneWriteBase[3] = bonePosition;
                Print("[MLBONE99] stage=identity_basis_fallback position=" + bonePosition);
            }
            m_MovementLabBoneWriteCaptured = true;
            Print("[MLBONE99] stage=captured position=" + m_MovementLabBoneWriteBase[3]);
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
                Print("[MLBONE99] stage=before_SetBoneMatrix");
            accepted = SetBoneMatrix(this, m_MovementLabBoneWriteModelIndex, pose);
        }
        else
        {
            if (firstInMode)
                Print("[MLBONE99] stage=before_SetBoneGlobal");
            SetBoneGlobal(this, m_MovementLabBoneWriteModelIndex, pose);
        }
        if (firstInMode)
        {
            vector readback[4];
            bool readable = GetBoneMatrix(this, m_MovementLabBoneWriteModelIndex, readback);
            vector modelReadback[4];
            GetBoneTransformMS(m_MovementLabBoneWriteIndex, modelReadback);
            Print("[MLBONE99] stage=write_result mode=" + mode + " writerIndex=" + m_MovementLabBoneWriteModelIndex + " matrixAccepted=" + accepted + " readable=" + readable + " requested=" + pose[3] + " matrixReadback=" + readback[3] + " modelReadback=" + modelReadback[3]);
            m_MovementLabBoneWriteLastMode = mode;
        }
        m_MovementLabBoneWriteFrames++;
    }
}
