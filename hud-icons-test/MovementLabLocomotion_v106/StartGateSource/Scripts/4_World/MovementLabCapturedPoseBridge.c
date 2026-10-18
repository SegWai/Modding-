// Native graph-controlled captured pose. Generic SetBone* APIs are not used.
class MovementLabCapturedJoint
{
    vector Matrix[4];
    bool Valid;
}

class MovementLabCapturedPose
{
    ref array<string> Names;
    ref array<int> Parents;
    ref array<ref MovementLabCapturedJoint> Joints = new array<ref MovementLabCapturedJoint>();

    void MovementLabCapturedPose()
    {
        MovementLabCapturedPoseSpec.Build(Names, Parents);
        for (int i = 0; i < Names.Count(); i++)
            Joints.Insert(new MovementLabCapturedJoint());
    }

    static bool ValidMatrix(vector matrix[4])
    {
        return matrix[0].Length() > 0.98 && matrix[0].Length() < 1.02 && matrix[1].Length() > 0.98 && matrix[1].Length() < 1.02 && matrix[2].Length() > 0.98 && matrix[2].Length() < 1.02 && matrix[3].Length() < 20;
    }

    bool HasCore()
    {
        array<string> required = {"Pelvis", "Spine3", "Head", "LeftArm", "LeftForeArm", "RightArm", "RightForeArm", "LeftUpLeg", "LeftLeg", "RightUpLeg", "RightLeg"};
        for (int k = 0; k < required.Count(); k++)
        {
            int index = Names.Find(required[k]);
            if (index < 0 || !Joints[index].Valid)
                return false;
        }
        return true;
    }

    bool ReadInfected(ZombieBase actor)
    {
        int count = 0;
        for (int i = 0; i < Names.Count(); i++)
        {
            int id = actor.GetBoneIndexByName(Names[i]);
            if (id != -1)
                actor.GetBoneTransformMS(id, Joints[i].Matrix);
            Joints[i].Valid = id != -1 && ValidMatrix(Joints[i].Matrix);
            if (Joints[i].Valid)
                count++;
        }
        Print("[MLPOSE106] stage=captured valid=" + count + " core=" + HasCore());
        return HasCore();
    }

    bool ReadHuman(PlayerBase actor)
    {
        for (int i = 0; i < Names.Count(); i++)
        {
            int id = actor.GetBoneIndexByName(Names[i]);
            if (id != -1)
                actor.GetBoneTransformMS(id, Joints[i].Matrix);
            Joints[i].Valid = id != -1 && ValidMatrix(Joints[i].Matrix);
        }
        return HasCore();
    }
}

class MovementLabCapturedPoseBinding
{
    int RX;
    int RY;
    int RZ;
    int TX;
    int TY;
    int TZ;
}

class MovementLabCapturedPoseBridge
{
    protected PlayerBase m_Actor;
    protected ref MovementLabCapturedPose m_Target;
    protected ref MovementLabCapturedPose m_Reference;
    protected ref MovementLabCapturedPose m_Actual;
    protected ref array<ref MovementLabCapturedPoseBinding> m_Bindings = new array<ref MovementLabCapturedPoseBinding>();
    protected int m_Gate = -1;
    protected int m_Phase;
    protected int m_At;
    protected bool m_LoggedCheck;
    protected bool m_Failed;

    bool Begin(PlayerBase actor, MovementLabCapturedPose target)
    {
        if (!actor || !target || !target.HasCore())
            return false;
        m_Actor = actor;
        m_Target = target;
        m_Reference = new MovementLabCapturedPose();
        m_Actual = new MovementLabCapturedPose();
        HumanAnimInterface animation = actor.GetAnimInterface();
        if (!animation)
        {
            Print("[MLPOSE106] stage=failed reason=no_animation_interface");
            return false;
        }
        m_Gate = animation.BindVariableFloat("MLCapturedPoseActive");
        if (m_Gate < 0)
        {
            Print("[MLPOSE106] stage=failed reason=graph_gate_missing");
            return false;
        }
        for (int i = 0; i < target.Names.Count(); i++)
        {
            MovementLabCapturedPoseBinding binding = new MovementLabCapturedPoseBinding();
            string prefix = "MLCapturedPose_" + i;
            binding.RX = animation.BindVariableFloat(prefix + "_Rotate_X");
            binding.RY = animation.BindVariableFloat(prefix + "_Rotate_Y");
            binding.RZ = animation.BindVariableFloat(prefix + "_Rotate_Z");
            binding.TX = animation.BindVariableFloat(prefix + "_Translate_X");
            binding.TY = animation.BindVariableFloat(prefix + "_Translate_Y");
            binding.TZ = animation.BindVariableFloat(prefix + "_Translate_Z");
            if (binding.RX < 0 || binding.RY < 0 || binding.RZ < 0 || binding.TX < 0 || binding.TY < 0 || binding.TZ < 0)
            {
                Print("[MLPOSE106] stage=failed reason=graph_binding_missing joint=" + target.Names[i]);
                return false;
            }
            m_Bindings.Insert(binding);
        }
        actor.AnimSetFloat(m_Gate, 1);
        m_At = GetGame().GetTime();
        Print("[MLPOSE106] stage=bound controls=" + m_Bindings.Count() * 6);
        return true;
    }

    protected bool Apply()
    {
        int count = 0;
        for (int i = 0; i < m_Target.Names.Count(); i++)
        {
            if (!m_Target.Joints[i].Valid || !m_Reference.Joints[i].Valid)
                continue;
            int parent = m_Target.Parents[i];
            while (parent >= 0 && (!m_Target.Joints[parent].Valid || !m_Reference.Joints[parent].Valid))
                parent = m_Target.Parents[parent];
            vector current[4];
            if (parent < 0)
            {
                for (int axis = 0; axis < 4; axis++)
                    current[axis] = m_Reference.Joints[i].Matrix[axis];
            }
            else
            {
                vector relative[4];
                Math3D.MatrixInvMultiply4(m_Reference.Joints[parent].Matrix, m_Reference.Joints[i].Matrix, relative);
                Math3D.MatrixMultiply4(m_Target.Joints[parent].Matrix, relative, current);
            }
            vector desired[4];
            for (int component = 0; component < 4; component++)
                desired[component] = m_Target.Joints[i].Matrix[component];
            vector translation = desired[3] - current[3];
            if (translation.Length() > 10)
            {
                Print("[MLPOSE106] stage=failed reason=correction_out_of_range joint=" + m_Target.Names[i]);
                return false;
            }
            current[3] = "0 0 0";
            desired[3] = "0 0 0";
            Math3D.MatrixInverse4(current);
            vector delta[4];
            Math3D.MatrixMultiply4(desired, current, delta);
            // Native vector[4] stores basis columns, unlike the offline
            // solver's matrix rows. Fixed model axes X -> Y -> Z.
            float ry = Math.Asin(Math.Clamp(-delta[0][2], -1.0, 1.0));
            float rx;
            float rz;
            if (Math.AbsFloat(Math.Cos(ry)) > 0.0000001)
            {
                rx = Math.Atan2(delta[1][2], delta[2][2]);
                rz = Math.Atan2(delta[0][1], delta[0][0]);
            }
            else
            {
                rx = Math.Atan2(-delta[2][1], delta[1][1]);
                rz = 0;
            }
            MovementLabCapturedPoseBinding b = m_Bindings[i];
            m_Actor.AnimSetFloat(b.RX, rx);
            m_Actor.AnimSetFloat(b.RY, ry);
            m_Actor.AnimSetFloat(b.RZ, rz);
            m_Actor.AnimSetFloat(b.TX, translation[0]);
            m_Actor.AnimSetFloat(b.TY, translation[1]);
            m_Actor.AnimSetFloat(b.TZ, translation[2]);
            count++;
        }
        Print("[MLPOSE106] stage=applied joints=" + count);
        return count >= 11;
    }

    bool Step()
    {
        if (m_Failed || !m_Actor || GetGame().GetTime() - m_At < 33)
            return false;
        if (m_Phase == 0)
        {
            if (!m_Reference.ReadHuman(m_Actor))
                return false;
            if (!Apply())
            {
                m_Failed = true;
                return false;
            }
            m_Phase = 1;
            m_At = GetGame().GetTime();
            return false;
        }
        float positionError;
        float basisError;
        int checked;
        if (!Measure(positionError, basisError, checked))
            return false;
        bool matched = checked >= 11 && positionError <= 0.01 && basisError <= 0.035;
        if (!m_LoggedCheck || matched)
        {
            Print("[MLPOSE106] stage=verify matched=" + matched + " joints=" + checked + " positionError=" + positionError + " basisError=" + basisError);
            m_LoggedCheck = true;
        }
        return matched;
    }

    protected bool Measure(out float positionError, out float basisError, out int checked)
    {
        if (!m_Actual.ReadHuman(m_Actor))
            return false;
        positionError = 0;
        basisError = 0;
        checked = 0;
        for (int i = 0; i < m_Target.Names.Count(); i++)
        {
            if (!m_Target.Joints[i].Valid)
                continue;
            if (!m_Reference.Joints[i].Valid || !m_Actual.Joints[i].Valid)
                return false;
            positionError = Math.Max(positionError, vector.Distance(m_Actual.Joints[i].Matrix[3], m_Target.Joints[i].Matrix[3]));
            for (int axis = 0; axis < 3; axis++)
                basisError = Math.Max(basisError, vector.Distance(m_Actual.Joints[i].Matrix[axis], m_Target.Joints[i].Matrix[axis]));
            checked++;
        }
        return checked >= 11;
    }

    void ReportPhysicsSeed()
    {
        float positionError;
        float basisError;
        int checked;
        bool readable = Measure(positionError, basisError, checked);
        Print("[MLPOSE106] stage=physics_seed readable=" + readable + " joints=" + checked + " positionError=" + positionError + " basisError=" + basisError);
    }

    void Stop()
    {
        if (m_Actor && m_Gate >= 0)
            m_Actor.AnimSetFloat(m_Gate, 0);
        m_Actor = null;
    }
}
