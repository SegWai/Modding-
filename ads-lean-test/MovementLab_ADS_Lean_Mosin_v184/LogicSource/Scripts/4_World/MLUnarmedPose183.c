// Independent, single-path unarmed preview. Snapshot each native side ONCE
// with all new correction/editor outputs zero. Sliders never recapture a pose.
class ML183UnarmedPose
{
 ref TStringArray Bones = new TStringArray;
 ref array<int> Parents = new array<int>;
 ref array<int> Vars = new array<int>;
 ref array<float> Last = new array<float>;
 ref array<float> LeftSolved;
 ref array<float> RightSolved;
 bool Failed[2];
 bool Tried;
 bool Bound;
 float BindWait;
 int Attempts;
 int ReportedSide = -2;
 int LastSide = -1;
 float Settled;
 int LeanVar = -1;
 int RaisedVar = -1;
 int ADSVar = -1;
 int NativeVar = -1;
 int ActiveVar = -1;
 int GateVar = -1;
 int SmoothVar = -1;
 int CanaryVar = -1;
 int PreviewVar = -1;
 int PreviewLeanVar = -1;
 void ML183UnarmedPose()
 {
  Bones.Insert("Pelvis"); Parents.Insert(-1);
  Bones.Insert("Spine"); Parents.Insert(0);
  Bones.Insert("Spine1"); Parents.Insert(1);
  Bones.Insert("Spine2"); Parents.Insert(2);
  Bones.Insert("Spine3"); Parents.Insert(3);
  Bones.Insert("Neck"); Parents.Insert(4);
  Bones.Insert("Neck1"); Parents.Insert(5);
  Bones.Insert("Head"); Parents.Insert(6);
  Bones.Insert("LeftUpLeg"); Parents.Insert(0);
  Bones.Insert("LeftLeg"); Parents.Insert(8);
  Bones.Insert("LeftFoot"); Parents.Insert(9);
  Bones.Insert("RightUpLeg"); Parents.Insert(0);
  Bones.Insert("RightLeg"); Parents.Insert(11);
  Bones.Insert("RightFoot"); Parents.Insert(12);
 }
 void Bind(PlayerBase actor, bool nativeReference)
 {
  if (Tried)
   return;
  Tried = true;
  LeanVar = actor.GetAnimInterface().BindVariableFloat("Lean");
  RaisedVar = actor.GetAnimInterface().BindVariableBool("Raised");
  ADSVar = actor.GetAnimInterface().BindVariableBool("ADS");
  NativeVar = actor.GetAnimInterface().BindVariableFloat("ML169UseNative");
  ActiveVar = actor.GetAnimInterface().BindVariableFloat("ML183Unarmed");
  GateVar = actor.GetAnimInterface().BindVariableFloat("MLADSLeanGate");
  SmoothVar = actor.GetAnimInterface().BindVariableFloat("MLADSLeanSmoothLow");
  CanaryVar = actor.GetAnimInterface().BindVariableFloat("MLADSLeanCanary");
  PreviewVar = actor.GetAnimInterface().BindVariableFloat("ML184PreviewActive");
  PreviewLeanVar = actor.GetAnimInterface().BindVariableFloat("ML184PreviewLean");
  Bound = PreviewVar >= 0 && PreviewLeanVar >= 0 && LeanVar >= 0 && RaisedVar >= 0 && ADSVar >= 0 && NativeVar >= 0 && ActiveVar >= 0 && GateVar >= 0 && SmoothVar >= 0 && CanaryVar >= 0;
  if (!nativeReference)
  {
   TStringArray names = new TStringArray;
   for (int baseIndex = 0; baseIndex < 84; baseIndex++)
    names.Insert("ML183C" + baseIndex);
   for (int armIndex = 0; armIndex < 9; armIndex++)
    names.Insert("ML183F" + armIndex);
   TStringArray axes = {"TX", "TY", "TZ", "RX", "RY", "RZ"};
   foreach (string bodyBone : ML183BodyState.Bones)
   {
    foreach (string axisName : axes)
     names.Insert("ML149" + bodyBone + axisName);
   }
   foreach (string variableName : names)
   {
    int id = actor.GetAnimInterface().BindVariableFloat(variableName);
    Bound = Bound && id >= 0;
    foreach (int previous : Vars)
     Bound = Bound && previous != id;
    Vars.Insert(id);
    Last.Insert(1000);
   }
   Bound = Bound && Vars.Count() == 237;
   ML183WeaponState.Bound = Bound;
   ML183WeaponState.ArmsReady = Bound;
   ML183BodyState.Bound = Bound;
  }
  Print("[MLUNARMED184] native_reference=" + nativeReference + " bound=" + Bound);
 }
 ML172Snapshot Capture(PlayerBase actor)
 {
  ML172Snapshot snapshot = new ML172Snapshot;
  foreach (string boneName : Bones)
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
   x.Normalize(); y.Normalize(); z.Normalize();
   ML172Frame poseFrame = new ML172Frame;
   poseFrame.Position = tm[3];
   poseFrame.Orientation = new ML144Rot;
   poseFrame.Orientation.A = Vector(x[0], y[0], z[0]);
   poseFrame.Orientation.B = Vector(x[1], y[1], z[1]);
   poseFrame.Orientation.C = Vector(x[2], y[2], z[2]);
   snapshot.Frames.Insert(poseFrame);
  }
  return snapshot;
 }
 array<float> Solve(ML172Snapshot source, bool left)
 {
  if (!source || source.Frames.Count() != 14)
   return null;
  ML172Snapshot target = ML183Targets.Build(left);
  array<vector> positions = new array<vector>;
  array<ref ML144Rot> rotations = new array<ref ML144Rot>;
  array<float> solved = new array<float>;
  for (int boneIndex = 0; boneIndex < 14; boneIndex++)
  {
   ML172Frame sourceBone = source.Frames[boneIndex];
   ML172Frame targetBone = target.Frames[boneIndex];
   // Leave native pelvis and legs entirely unchanged. Keep their source
   // frames for parent propagation; their zero coefficients are not graphed.
   if (boneIndex == 0 || boneIndex >= 8)
   {
    for (int zeroComponent = 0; zeroComponent < 6; zeroComponent++)
     solved.Insert(0);
    positions.Insert(sourceBone.Position);
    rotations.Insert(sourceBone.Orientation);
    continue;
   }
   ML172Frame sourceHip = source.Frames[0];
   ML172Frame targetHip = target.Frames[0];
   vector relativeTarget = targetBone.Position - targetHip.Position;
   vector desiredPosition = sourceHip.Position + relativeTarget;
   vector currentPosition = sourceBone.Position;
   ML144Rot currentRotation = sourceBone.Orientation;
   int parentIndex = Parents[boneIndex];
   if (parentIndex >= 0)
   {
    ML172Frame sourceParent = source.Frames[parentIndex];
    ML144Rot parentInverse = sourceParent.Orientation.Inverse();
    ML144Rot desiredParent = rotations[parentIndex];
    ML144Rot inherited = desiredParent.Times(parentInverse);
    vector relative = sourceBone.Position - sourceParent.Position;
    vector inheritedRelative = inherited.Apply(relative);
    vector parentPosition = positions[parentIndex];
    currentPosition = parentPosition + inheritedRelative;
    currentRotation = inherited.Times(sourceBone.Orientation);
   }
   ML144Rot currentInverse = currentRotation.Inverse();
   ML144Rot correction = targetBone.Orientation.Times(currentInverse);
   correction.AppendNative(solved);
   vector translation = desiredPosition - currentPosition;
   if (translation.Length() > 0.6)
    return null;
   solved.Insert(translation[0]);
   solved.Insert(translation[1]);
   solved.Insert(translation[2]);
   positions.Insert(desiredPosition);
   rotations.Insert(targetBone.Orientation);
  }
  foreach (float component : solved)
  {
   if (component != component || Math.AbsFloat(component) > 3.141593)
    return null;
  }
  return solved;
 }
 void Write(PlayerBase actor, int index, float value)
 {
  if (Math.AbsFloat(Last[index] - value) < 0.000001)
   return;
  Last[index] = value;
  actor.AnimSetFloat(Vars[index], value);
 }
 float WeightedArm(int index, ML144Values left, ML144Values right, float lw, float rw)
 {
  float value;
  switch (index)
  {
   case 0: value = left.LeftPitch * lw + right.LeftPitch * rw; break;
   case 1: value = left.LeftYaw * lw + right.LeftYaw * rw; break;
   case 2: value = left.LeftRoll * lw + right.LeftRoll * rw; break;
   case 3: value = left.RightPitch * lw + right.RightPitch * rw; break;
   case 4: value = left.RightYaw * lw + right.RightYaw * rw; break;
   case 5: value = left.RightRoll * lw + right.RightRoll * rw; break;
   case 6: value = left.HeadPitch * lw + right.HeadPitch * rw; break;
   case 7: value = left.HeadYaw * lw + right.HeadYaw * rw; break;
   case 8: value = left.HeadRoll * lw + right.HeadRoll * rw; break;
  }
  return -value * Math.DEG2RAD;
 }
 void Update(PlayerBase actor, float dt, float lean, bool nativeReference)
 {
  ML183Preset.Init();
  if (!Bound && Attempts < 5)
  {
   BindWait += Math.Clamp(dt, 0, 0.1);
   if (BindWait >= 0.5)
   {
    BindWait = 0;
    Attempts++;
    Tried = false;
    Vars.Clear();
    Last.Clear();
    Bind(actor, nativeReference);
   }
  }
  if (!Bound || !actor.IsAlive() || actor.IsUnconscious() || !actor.GetCommand_Move())
   return;
  // Never force raised arms or ADS on an empty-handed actor.
  actor.AnimSetBool(RaisedVar, false);
  actor.AnimSetBool(ADSVar, false);
  actor.AnimSetFloat(LeanVar, lean);
  actor.AnimSetFloat(PreviewVar, 1);
  actor.AnimSetFloat(PreviewLeanVar, lean);
  actor.AnimSetFloat(NativeVar, 1);
  actor.AnimSetFloat(GateVar, 0);
  actor.AnimSetFloat(SmoothVar, 0);
  actor.AnimSetFloat(CanaryVar, 0.731);
  int reportSide = 0;
  if (lean < -0.99)
   reportSide = -1;
  else if (lean > 0.99)
   reportSide = 1;
  if (reportSide != ReportedSide)
  {
   ReportedSide = reportSide;
   Print("[MLUNARMED184] native_reference=" + nativeReference + " shared_lean=" + lean);
  }
  if (nativeReference)
  {
   actor.AnimSetFloat(ActiveVar, 0);
   return;
  }
  actor.AnimSetFloat(ActiveVar, 1);
  int side = -1;
  if (lean < -0.99)
   side = 0;
  else if (lean > 0.99)
   side = 1;
  if (side != LastSide)
  {
   LastSide = side;
   Settled = 0;
  }
  else
   Settled += Math.Clamp(dt, 0, 0.1);
  bool sampled = false;
  if (side == 0)
   sampled = LeftSolved != null;
  else if (side == 1)
   sampled = RightSolved != null;
  if (side >= 0 && !sampled && !Failed[side] && Settled > 0.35)
  {
   ML172Snapshot source = Capture(actor);
   array<float> solved = Solve(source, side == 0);
   if (solved && solved.Count() == 84)
   {
    if (side == 0)
     LeftSolved = solved;
    else
     RightSolved = solved;
    Print("[MLUNARMED184] cached_native_unarmed_reference side=" + side);
   }
   else
   {
    Failed[side] = true;
    Print("[MLUNARMED184] reference rejected side=" + side);
   }
  }
  float lw = 0;
  float rw = 0;
  if (LeftSolved)
   lw = Math.Clamp(-lean, 0, 1);
  if (RightSolved)
   rw = Math.Clamp(lean, 0, 1);
  for (int baseIndex = 0; baseIndex < 84; baseIndex++)
  {
   float value = 0;
   if (LeftSolved)
    value += LeftSolved[baseIndex] * lw;
   if (RightSolved)
    value += RightSolved[baseIndex] * rw;
   Write(actor, baseIndex, value);
  }
  ML144Values leftValues = ML183WeaponState.LeftValues;
  ML144Values rightValues = ML183WeaponState.RightValues;
  for (int armIndex = 0; armIndex < 9; armIndex++)
   Write(actor, 84 + armIndex, WeightedArm(armIndex, leftValues, rightValues, lw, rw));
  for (int partIndex = 0; partIndex < 24; partIndex++)
  {
   ML149Part leftPart = ML183BodyState.Left.Parts[partIndex];
   ML149Part rightPart = ML183BodyState.Right.Parts[partIndex];
   for (int componentIndex = 0; componentIndex < 6; componentIndex++)
   {
    float bodyValue = leftPart.ComponentValue(componentIndex) * lw;
    bodyValue += rightPart.ComponentValue(componentIndex) * rw;
    if (componentIndex < 3)
     bodyValue *= 0.01;
    else
     bodyValue *= -Math.DEG2RAD;
    int writeIndex = 93 + partIndex * 6 + componentIndex;
    Write(actor, writeIndex, bodyValue);
   }
  }
 }
};
