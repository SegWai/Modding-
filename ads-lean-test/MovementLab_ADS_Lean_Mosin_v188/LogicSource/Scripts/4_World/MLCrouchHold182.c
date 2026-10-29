class ML182CrouchHold
{
 ref array<int> Vars = new array<int>;
 ref array<float> LeftSolved = new array<float>;
 ref array<float> RightSolved = new array<float>;
 bool Bound;
 bool Tried;
 bool Ready[2];
 vector ArmRoot[4];
 vector ArmElbow[4];
 vector ArmWrist[4];
 int Revision[2];
 int LastSide = -1;
 int InstallRevision = -1;
 float Settled;
 EntityAI Held;
 float Written[18];
 bool WrittenReady;
 bool ReadyNow;
 bool LeftReachValid = true;
 bool RightReachValid = true;
 void ML182CrouchHold()
 {
  Revision[0] = -1;
  Revision[1] = -1;
  for (int i = 0; i < 18; i++)
  {
   LeftSolved.Insert(0);
   RightSolved.Insert(0);
  }
 }
 void Bind(PlayerBase actor)
 {
  if (Tried)
   return;
  Tried = true;
  Bound = true;
  TStringArray names = new TStringArray;
  names.Insert("ML182CrouchEditor");
  for (int i = 0; i < 18; i++)
   names.Insert("ML182Hold" + i);
  foreach (string name : names)
  {
   int id = actor.GetAnimInterface().BindVariableFloat(name);
   if (id < 0)
    Bound = false;
   foreach (int previous : Vars)
   {
    if (id == previous)
     Bound = false;
   }
   Vars.Insert(id);
  }
  Print("[MLCROUCH182] hold_bound=" + Bound);
 }
 bool Capture(PlayerBase actor, int side)
 {
  for (int arm = 0; arm < 2; arm++)
  {
   string prefix = "Left";
   if (arm == 1)
    prefix = "Right";
   int rootIndex = actor.GetBoneIndexByName(prefix + "Arm");
   int elbowIndex = actor.GetBoneIndexByName(prefix + "ForeArm");
   int wristIndex = actor.GetBoneIndexByName(prefix + "Hand");
   if (rootIndex == -1 || elbowIndex == -1 || wristIndex == -1)
    return false;
   int index = side * 2 + arm;
   ArmRoot[index] = actor.GetBonePositionMS(rootIndex);
   ArmElbow[index] = actor.GetBonePositionMS(elbowIndex);
   ArmWrist[index] = actor.GetBonePositionMS(wristIndex);
   float upper = vector.Distance(ArmRoot[index], ArmElbow[index]);
   float lower = vector.Distance(ArmElbow[index], ArmWrist[index]);
   if (upper < 0.1 || upper > 0.6 || lower < 0.1 || lower > 0.6)
    return false;
  }
  return true;
 }
 void Write(PlayerBase actor, array<float> values, bool active)
 {
  if (!Bound)
   return;
  float enabled = 0;
  if (active)
   enabled = 1;
  actor.AnimSetFloat(Vars[0], enabled);
  for (int i = 0; i < 18; i++)
  {
   float value = 0;
   if (active)
    value = values[i];
   if (!WrittenReady || Written[i] != value)
   {
    actor.AnimSetFloat(Vars[i + 1], value);
    Written[i] = value;
   }
  }
  WrittenReady = true;
 }
 void Update(PlayerBase actor, HumanMovementState state, float dt, float gate, float lean)
 {
  Bind(actor);
  if (!Bound)
   return;
  if (InstallRevision != ML182WeaponState.InstallRevision)
  {
   InstallRevision = ML182WeaponState.InstallRevision;
   LeftReachValid = true;
   RightReachValid = true;
   Revision[0] = -1;
   Revision[1] = -1;
  }
  EntityAI heldNow = actor.GetHumanInventory().GetEntityInHands();
  if (heldNow != Held)
  {
   Held = heldNow;
   Ready[0] = false;
   Ready[1] = false;
   Revision[0] = -1;
   Revision[1] = -1;
   Settled = 0;
  }
  int side = 0;
  if (lean > 0)
   side = 1;
  if (side != LastSide)
  {
   LastSide = side;
   Settled = 0;
  }
  bool crouched = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDCROUCH;
  bool stable = crouched && state.m_iMovement == 0 && gate > 0.98 && Math.AbsFloat(lean) > 0.98;
  ReadyNow = Ready[side] && crouched && gate > 0.01;
  if (!Ready[side])
  {
   // New graph stage and body edits remain zero for the entire settle period.
   Write(actor, null, false);
   if (stable)
    Settled += Math.Clamp(dt, 0, 0.05);
   else
    Settled = 0;
   if (Settled <= 0.3)
    return;
   Ready[side] = Capture(actor, side);
   ReadyNow = Ready[side];
   if (!Ready[side])
    return;
   Revision[side] = -1;
   ML144State.Status = "Crouch reference ready. Edits affect blue only.";
   Print("[MLCROUCH182] base_reference_side=" + side);
  }
  array<float> solved = LeftSolved;
  if (side == 1)
   solved = RightSolved;
  if (Revision[side] != ML144State.ValuesRevision)
  {
   Revision[side] = ML144State.ValuesRevision;
   ML144Values value = ML144State.SideValues(side == 0);
   array<float> candidate = new array<float>;
   bool identity = value.X == 0 && value.Y == 0 && value.Z == 0;
   identity = identity && value.Pitch == 0 && value.Yaw == 0 && value.Roll == 0;
   bool ok = true;
   if (identity)
   {
    for (int zeroIndex = 0; zeroIndex < 18; zeroIndex++)
     candidate.Insert(0);
   }
   else
   {
    ML144Rot rotation = ML144Math.Euler(value);
    vector offset = Vector(value.X * 0.01, value.Y * 0.01, value.Z * 0.01);
    int leftIndex = side * 2;
    int rightIndex = leftIndex + 1;
    vector rightTarget = ArmWrist[rightIndex] + offset;
    vector handSpan = ArmWrist[leftIndex] - ArmWrist[rightIndex];
    vector leftTarget = rightTarget + rotation.Apply(handSpan);
    bool leftOK = ML144Math.Limb(ArmRoot[leftIndex], ArmElbow[leftIndex], ArmWrist[leftIndex], leftTarget, rotation, candidate);
    bool rightOK = ML144Math.Limb(ArmRoot[rightIndex], ArmElbow[rightIndex], ArmWrist[rightIndex], rightTarget, rotation, candidate);
    ok = leftOK && rightOK && candidate.Count() == 18;
   }
   if (side == 0)
    LeftReachValid = ok;
   else
    RightReachValid = ok;
   ML182WeaponState.ReachValid = LeftReachValid && RightReachValid;
   if (ok)
   {
    if (side == 0)
     LeftSolved = candidate;
    else
     RightSolved = candidate;
    solved = candidate;
   }
   else
    ML144State.Status = "Weapon target outside arm reach; previous hold retained.";
  }
  Write(actor, solved, ReadyNow);
 }
};
