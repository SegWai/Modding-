// Native snapshots are captured only while correction outputs are zero.
// Each walking direction/gait is solved ONCE, then uses cached graph controls.
// Never feed corrected output back into the solver every frame.
class ML172Frame
{
 vector Position;
 ref ML144Rot Orientation;
};
class ML172Snapshot
{
 ref array<ref ML172Frame> Frames = new array<ref ML172Frame>;
};
class ML172Solution
{
 ref array<float> Values;
 float Fade;
 bool Verified;
 float VerifyTime;
};
class ML172WalkUpper
{
 ref array<string> Names = new array<string>;
 ref array<int> Parents = new array<int>;
 ref array<int> Vars = new array<int>;
 ref array<float> Last = new array<float>;
 ref array<ref ML172Snapshot> Standing = new array<ref ML172Snapshot>;
 ref array<ref ML172Solution> Walking = new array<ref ML172Solution>;
 ref array<bool> Failed = new array<bool>;
 bool Tried;
 bool Bound;
 int ActiveVar = -1;
 int LastActive = -1;
 int Revision = -1;
 int BodyRevision = -1;
 bool DropMode;
 EntityAI HeldWeapon;
 int LastWalkKey = -1;
 int LastDirection;
 int SampleKey = -1;
 int LastPoseKey = -1;
 float StandTime;
 float WalkTime;
 void ML172WalkUpper()
 {
  Names.Insert("Pelvis");
  Parents.Insert(-1);
  Names.Insert("Spine");
  Parents.Insert(0);
  Names.Insert("Spine1");
  Parents.Insert(1);
  Names.Insert("Spine2");
  Parents.Insert(2);
  Names.Insert("Spine3");
  Parents.Insert(3);
  Names.Insert("Neck");
  Parents.Insert(4);
  Names.Insert("Neck1");
  Parents.Insert(5);
  Names.Insert("Head");
  Parents.Insert(6);
  Names.Insert("LeftShoulder");
  Parents.Insert(4);
  Names.Insert("LeftArm");
  Parents.Insert(8);
  Names.Insert("LeftArmRoll");
  Parents.Insert(9);
  Names.Insert("LeftForeArm");
  Parents.Insert(10);
  Names.Insert("LeftForeArmRoll");
  Parents.Insert(11);
  Names.Insert("LeftHand");
  Parents.Insert(12);
  Names.Insert("RightShoulder");
  Parents.Insert(4);
  Names.Insert("RightArm");
  Parents.Insert(14);
  Names.Insert("RightArmRoll");
  Parents.Insert(15);
  Names.Insert("RightForeArm");
  Parents.Insert(16);
  Names.Insert("RightForeArmRoll");
  Parents.Insert(17);
  Names.Insert("RightHand");
  Parents.Insert(18);
  for (int s = 0; s < 4; s++)
   Standing.Insert(null);
  for (int c = 0; c < 64; c++)
  {
   Walking.Insert(null);
   Failed.Insert(false);
  }
 }
 ML172Snapshot Capture(PlayerBase actor, float leanWeight)
 {
  ML172Snapshot snapshot = new ML172Snapshot;
  foreach (string boneName : Names)
  {
   int boneId = actor.GetBoneIndexByName(boneName);
   if (boneId == -1)
    return null;
   vector tm[4];
   actor.GetBoneTransformMS(boneId, tm);
   vector x = tm[0];
   vector y = tm[1];
   vector z = tm[2];
   if (x.LengthSq() < 0.5 || y.LengthSq() < 0.5 || z.LengthSq() < 0.5)
    return null;
   x.Normalize();
   y.Normalize();
   z.Normalize();
   ML172Frame poseFrame = new ML172Frame;
   poseFrame.Position = tm[3];
   poseFrame.Orientation = new ML144Rot;
   poseFrame.Orientation.A = Vector(x[0], y[0], z[0]);
   poseFrame.Orientation.B = Vector(x[1], y[1], z[1]);
   poseFrame.Orientation.C = Vector(x[2], y[2], z[2]);
   snapshot.Frames.Insert(poseFrame);
  }
  // Remove the known final rigid aim from the snapshot. Calibration is
  // limited to near-centre (no final arm re-solve), so this is reference-frame
  // conversion, not iterative correction of an already corrected output.
  HumanCommandWeapons aimFrame = actor.GetCommandModifier_Weapons();
  if (aimFrame)
  {
   ML144Values pitchValues = new ML144Values;
   pitchValues.Pitch = aimFrame.GetBaseAimingAngleUD() * leanWeight;
   pitchValues.Yaw = 0;
   pitchValues.Roll = 0;
   ML144Values yawValues = new ML144Values;
   yawValues.Pitch = 0;
   yawValues.Yaw = -aimFrame.GetBaseAimingAngleLR() * leanWeight;
   yawValues.Roll = 0;
   ML144Rot pitchInverse = ML144Math.Euler(pitchValues);
   ML144Rot yawInverse = ML144Math.Euler(yawValues);
   ML144Rot undoAim = pitchInverse.Times(yawInverse);
   ML172Frame aimPivot = snapshot.Frames[4];
   vector pivot = aimPivot.Position;
   for (int upperIndex = 4; upperIndex < 20; upperIndex++)
   {
    ML172Frame undoFrame = snapshot.Frames[upperIndex];
    vector relativeAim = undoFrame.Position - pivot;
    undoFrame.Position = pivot + undoAim.Apply(relativeAim);
    undoFrame.Orientation = undoAim.Times(undoFrame.Orientation);
   }
  }
  return snapshot;
 }
 ML172Solution Solve(ML172Snapshot target, ML172Snapshot source)
 {
  if (!target || !source || target.Frames.Count() != 20 || source.Frames.Count() != 20)
   return null;
  ML172Frame targetHip = target.Frames[0];
  ML172Frame sourceHip = source.Frames[0];
  vector hipShift = targetHip.Position - sourceHip.Position;
  hipShift[1] = 0;
  if (hipShift.Length() > 0.6)
   return null;
  float vertical = sourceHip.Position[1] - targetHip.Position[1];
  vector bob = Vector(0, vertical, 0);
  array<vector> desiredPositions = new array<vector>;
  array<ref ML144Rot> desiredRotations = new array<ref ML144Rot>;
  vector correctedHipPosition = sourceHip.Position + hipShift;
  desiredPositions.Insert(correctedHipPosition);
  desiredRotations.Insert(sourceHip.Orientation);
  ML172Solution solution = new ML172Solution;
  solution.Values = new array<float>;
  solution.Values.Insert(hipShift[0]);
  solution.Values.Insert(hipShift[2]);
  for (int i = 1; i < 20; i++)
  {
   int parentIndex = Parents[i];
   ML172Frame sourceParent = source.Frames[parentIndex];
   ML172Frame sourceBone = source.Frames[i];
   ML172Frame targetBone = target.Frames[i];
   ML144Rot sourceParentInverse = sourceParent.Orientation.Inverse();
   ML144Rot desiredParent = desiredRotations[parentIndex];
   ML144Rot inherited = desiredParent.Times(sourceParentInverse);
   vector relative = sourceBone.Position - sourceParent.Position;
   vector inheritedRelative = inherited.Apply(relative);
   vector desiredParentPosition = desiredPositions[parentIndex];
   vector currentPosition = desiredParentPosition + inheritedRelative;
   ML144Rot currentRotation = inherited.Times(sourceBone.Orientation);
   ML144Rot currentInverse = currentRotation.Inverse();
   ML144Rot correction = targetBone.Orientation.Times(currentInverse);
   correction.AppendNative(solution.Values);
   vector desiredPosition = targetBone.Position + bob;
   vector translation = desiredPosition - currentPosition;
   if (translation.Length() > 0.35)
    return null;
   solution.Values.Insert(translation[0]);
   solution.Values.Insert(translation[1]);
   solution.Values.Insert(translation[2]);
   desiredPositions.Insert(desiredPosition);
   desiredRotations.Insert(targetBone.Orientation);
  }
  if (solution.Values.Count() != 116)
   return null;
  foreach (float component : solution.Values)
  {
   if (component != component || Math.AbsFloat(component) > 3.141593)
    return null;
  }
  return solution;
 }
 void Write(PlayerBase actor, ML172Solution solution, float weight)
 {
  int active = 0;
  if (solution && weight > 0.000001)
   active = 1;
  for (int index = 0; index < 116; index++)
  {
   float value = 0;
   if (active == 1)
    value = solution.Values[index] * weight;
   if (Math.AbsFloat(Last[index] - value) > 0.000001)
   {
    Last[index] = value;
    actor.AnimSetFloat(Vars[index], value);
   }
  }
  if (active != LastActive)
  {
   actor.AnimSetFloat(ActiveVar, active);
   LastActive = active;
  }
 }
 void Update(PlayerBase actor, HumanMovementState state, float dt, float gate, float lean, float movementBlend, int profile, bool movingElbowReady)
 {
  if (!Tried)
  {
   Tried = true;
   Bound = true;
   ActiveVar = actor.GetAnimInterface().BindVariableFloat("ML172Active");
   Bound = ActiveVar >= 0;
   for (int bindIndex = 0; bindIndex < 116; bindIndex++)
   {
    int id = actor.GetAnimInterface().BindVariableFloat("ML172C" + bindIndex);
    Bound = Bound && id >= 0 && id != ActiveVar;
    foreach (int prior : Vars)
     Bound = Bound && id != prior;
    Vars.Insert(id);
    Last.Insert(1000);
   }
   Print("[MLWALK172] bound=" + Bound);
  }
  if (!Bound)
   return;
  EntityAI held = actor.GetHumanInventory().GetEntityInHands();
  bool changed = held != HeldWeapon || Revision != ML144State.ValuesRevision;
  changed = changed || BodyRevision != ML149State.GeometryRevision || DropMode != MLADSLeanSettings.ArmDropTest;
  if (changed)
  {
   HeldWeapon = held;
   Revision = ML144State.ValuesRevision;
   BodyRevision = ML149State.GeometryRevision;
   DropMode = MLADSLeanSettings.ArmDropTest;
   for (int clearStand = 0; clearStand < 4; clearStand++)
    Standing[clearStand] = null;
   for (int clearWalk = 0; clearWalk < 64; clearWalk++)
   {
    Walking[clearWalk] = null;
    Failed[clearWalk] = false;
   }
   StandTime = 0;
   WalkTime = 0;
   LastWalkKey = -1;
   SampleKey = -1;
  }
  int poseKey = 0;
  if (lean > 0)
   poseKey = 1;
  if (actor.IsInIronsights() || actor.IsInOptics())
   poseKey += 2;
  if (poseKey != LastPoseKey)
  {
   LastPoseKey = poseKey;
   StandTime = 0;
   WalkTime = 0;
  }
  bool erect = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool eligible = erect && state.m_iMovement <= 2 && profile == 1 && MLADSLeanSettings.Enabled && DropMode;
  eligible = eligible && actor.IsAlive() && !actor.IsUnconscious() && actor.IsRaised();
  HumanCommandWeapons aim = actor.GetCommandModifier_Weapons();
  bool centred = false;
  if (aim)
   centred = Math.AbsFloat(aim.GetBaseAimingAngleLR()) <= 1 && Math.AbsFloat(aim.GetBaseAimingAngleUD()) <= 1;
  bool full = eligible && gate > 0.98 && Math.AbsFloat(lean) > 0.98 && centred;
  full = full && actor.IsWeaponRaiseCompleted();
  float step = Math.Clamp(dt, 0, 0.05);
  bool idle = state.m_iMovement == 0 && movementBlend < 0.01;
  if (full && idle && !Standing[poseKey])
  {
   StandTime += step;
   if (StandTime > 0.6)
   {
    Write(actor, null, 0);
    Standing[poseKey] = Capture(actor, gate * Math.AbsFloat(lean));
    StandTime = 0;
    Print("[MLWALK172] standing_reference=" + poseKey + " captured=" + (Standing[poseKey] != null));
   }
  }
  else
   StandTime = 0;
  int walkKey = -1;
  if (state.m_iMovement > 0 && state.m_iMovement <= 2)
  {
   HumanInputController input = actor.GetInputController();
   float speed;
   vector direction;
   if (input)
    input.GetMovement(speed, direction);
   if (speed > 0 && direction.LengthSq() > 0.1)
   {
    float angle = Math.Atan2(direction[0], direction[2]) * Math.RAD2DEG;
    if (angle < 0)
     angle += 360;
    LastDirection = Math.Floor((angle + 22.5) / 45);
    if (LastDirection >= 8)
     LastDirection = 0;
   }
   int gaitOffset = 0;
   if (state.m_iMovement == 2)
    gaitOffset = 4;
   walkKey = poseKey + gaitOffset + LastDirection * 8;
   LastWalkKey = walkKey;
  }
  else if (LastWalkKey >= 0)
  {
   int priorPoseKey = LastWalkKey % 4;
   if (priorPoseKey == poseKey)
    walkKey = LastWalkKey;
  }
  if (walkKey != SampleKey)
  {
   SampleKey = walkKey;
   WalkTime = 0;
  }
  ML172Solution solution;
  if (walkKey >= 0)
   solution = Walking[walkKey];
  bool canLearn = full && state.m_iMovement > 0 && movementBlend > 0.98 && walkKey >= 0 && Standing[poseKey] != null;
  if (lean < 0 && !movingElbowReady)
   canLearn = false;
  if (walkKey >= 0 && Failed[walkKey])
   canLearn = false;
  if (canLearn && !solution)
  {
   Write(actor, null, 0);
   WalkTime += step;
   if (WalkTime > 0.5)
   {
    ML172Snapshot walkReference = Capture(actor, gate * Math.AbsFloat(lean));
    solution = Solve(Standing[poseKey], walkReference);
    Walking[walkKey] = solution;
    Failed[walkKey] = solution == null;
    Print("[MLWALK172] walking_reference=" + walkKey + " solved=" + (solution != null));
   }
  }
  else
   WalkTime = 0;
  float weight = 0;
  if (eligible && solution)
  {
   solution.Fade = Math.Min(1.0, solution.Fade + step / 0.12);
   weight = movementBlend * gate * Math.AbsFloat(lean) * solution.Fade;
  }
  Write(actor, solution, weight);
  // One read-only verification per learned direction. Never adjust coefficients
  // from this output; it only reports remaining native gait variation.
  if (solution && !solution.Verified && full && weight > 0.999 && Standing[poseKey] != null)
  {
   solution.VerifyTime += step;
   if (solution.VerifyTime > 0.4)
   {
    ML172Snapshot verifyPose = Capture(actor, gate * Math.AbsFloat(lean));
    if (verifyPose)
    {
     ML172Snapshot wantedPose = Standing[poseKey];
     ML172Frame verifyHip = verifyPose.Frames[0];
     ML172Frame wantedHip = wantedPose.Frames[0];
     float verifyBob = verifyHip.Position[1] - wantedHip.Position[1];
     vector verifyBobVector = Vector(0, verifyBob, 0);
     float maximumPositionError = 0;
     for (int verifyIndex = 1; verifyIndex < 20; verifyIndex++)
     {
      ML172Frame actualPart = verifyPose.Frames[verifyIndex];
      ML172Frame wantedPart = wantedPose.Frames[verifyIndex];
      vector wantedPosition = wantedPart.Position + verifyBobVector;
      float partError = vector.Distance(actualPart.Position, wantedPosition);
      maximumPositionError = Math.Max(maximumPositionError, partError);
     }
     Print("[MLWALK172] verify_key=" + walkKey + " upper_max_error_m=" + maximumPositionError);
    }
    solution.Verified = true;
   }
  }
 }
};
