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
 ref ML172Snapshot NeutralReference;
 ref ML172Snapshot LeftReference;
 bool Failed[2];
 bool Tried;
 bool Bound;
 bool PlayerInput;
 bool HeldEditor;
 bool OtherHeldEditor;
 bool OneHandEditor;
 bool HeavyEditor;
 bool PolearmEditor;
 bool SmgWalkingEditor;
 bool SledgeWalkingEditor;
 bool OneHandWalkingEditor;
 bool ReferenceSmgWalkingBank;
 bool ReferenceToolWalkingBank;
 bool ReferenceOneHandWalkingBank;
 bool PistolBank;
 bool ReferencePistolBank;
 bool ReferenceBatBank;
 bool ReferenceOneHandBank;
 bool ReferenceHeavyBank;
 bool ReferencePolearmBank;
 EntityAI ReferenceItem;
 bool ReferenceItemSet;
 bool ReferenceHeldBank;
 int HeldVar = -1;
 float BindWait;
 int Attempts;
 int ReportedSide = -2;
 int LastSide = -1;
 float Settled;
 float NeutralTime;
 bool NeutralTried;
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
  HeldVar = actor.GetAnimInterface().BindVariableFloat("ML187HeldLean");
  GateVar = actor.GetAnimInterface().BindVariableFloat("MLADSLeanGate");
  SmoothVar = actor.GetAnimInterface().BindVariableFloat("MLADSLeanSmoothLow");
  CanaryVar = actor.GetAnimInterface().BindVariableFloat("MLADSLeanCanary");
  PreviewVar = actor.GetAnimInterface().BindVariableFloat("ML184PreviewActive");
  PreviewLeanVar = actor.GetAnimInterface().BindVariableFloat("ML184PreviewLean");
  Bound = HeldVar >= 0 && PreviewVar >= 0 && PreviewLeanVar >= 0 && LeanVar >= 0 && RaisedVar >= 0 && ADSVar >= 0 && NativeVar >= 0 && ActiveVar >= 0 && GateVar >= 0 && SmoothVar >= 0 && CanaryVar >= 0;
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
   if (OneHandWalkingEditor)
   {
    ML211WeaponState.Bound = Bound;
    ML211WeaponState.ArmsReady = Bound;
    ML211BodyState.Bound = Bound;
   }
   if (SledgeWalkingEditor)
   {
    ML209WeaponState.Bound = Bound;
    ML209WeaponState.ArmsReady = Bound;
    ML209BodyState.Bound = Bound;
   }
   if (SmgWalkingEditor)
   {
    ML207WeaponState.Bound = Bound;
    ML207WeaponState.ArmsReady = Bound;
    ML207BodyState.Bound = Bound;
   }
   if (PolearmEditor)
   {
    ML204WeaponState.Bound = Bound;
    ML204WeaponState.ArmsReady = Bound;
    ML204BodyState.Bound = Bound;
   }
   if (HeavyEditor)
   {
    ML202WeaponState.Bound = Bound;
    ML202WeaponState.ArmsReady = Bound;
    ML202BodyState.Bound = Bound;
   }
   if (OneHandEditor)
   {
    ML200WeaponState.Bound = Bound;
    ML200WeaponState.ArmsReady = Bound;
    ML200BodyState.Bound = Bound;
   }
   if (OtherHeldEditor)
   {
    ML193WeaponState.Bound = Bound;
    ML193WeaponState.ArmsReady = Bound;
    ML193BodyState.Bound = Bound;
   }
   if (HeldEditor)
   {
    ML190WeaponState.Bound = Bound;
    ML190WeaponState.ArmsReady = Bound;
    ML190BodyState.Bound = Bound;
   }
   ML183WeaponState.ArmsReady = Bound;
   ML183BodyState.Bound = Bound;
  }
  Print("[MLSHARED187] native_reference=" + nativeReference + " bound=" + Bound);
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
  if (left && !NeutralReference)
   return null;
  ML172Snapshot target = ML183Targets.Build(left);
  ML172Snapshot rightTarget = ML183Targets.Build(false);
  array<vector> positions = new array<vector>;
  array<ref ML144Rot> rotations = new array<ref ML144Rot>;
  array<float> solved = new array<float>;
  for (int boneIndex = 0; boneIndex < 14; boneIndex++)
  {
   ML172Frame sourceBone = source.Frames[boneIndex];
   ML172Frame targetBone = target.Frames[boneIndex];
   ML144Rot desiredRotation = targetBone.Orientation;
   if (left && boneIndex > 0 && boneIndex < 8)
   {
    // Reflect a deformation, NEVER a bone's absolute basis. Neutral bone
    // axes are not model XYZ: S * R * S alone can invert the torso/neck.
    ML172Frame neutralBone = NeutralReference.Frames[boneIndex];
    ML172Frame rightBone = rightTarget.Frames[boneIndex];
    ML144Rot neutralInverse = neutralBone.Orientation.Inverse();
    ML144Rot deformation = rightBone.Orientation.Times(neutralInverse);
    ML144Rot reflected = new ML144Rot;
    vector rowA = deformation.A;
    vector rowB = deformation.B;
    vector rowC = deformation.C;
    reflected.A = Vector(rowA[0], -rowA[1], -rowA[2]);
    reflected.B = Vector(-rowB[0], rowB[1], rowB[2]);
    reflected.C = Vector(-rowC[0], rowC[1], rowC[2]);
    desiredRotation = reflected.Times(neutralBone.Orientation);
   }
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
   ML144Rot correction = desiredRotation.Times(currentInverse);
   correction.AppendNative(solved);
   vector translation = desiredPosition - currentPosition;
   if (translation.Length() > 0.6)
    return null;
   solved.Insert(translation[0]);
   solved.Insert(translation[1]);
   solved.Insert(translation[2]);
   positions.Insert(desiredPosition);
   rotations.Insert(desiredRotation);
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
 bool ConfigureLineup(PlayerBase actor)
 {
  EntityAI item = actor.GetHumanInventory().GetEntityInHands();
  int kind = ItemBehaviorType.EMPTYHANDED;
  if (item)
  {
   HumanItemAccessor accessor = actor.GetItemAccessor();
   if (!accessor)
    return false;
   HumanItemBehaviorCfg behavior = accessor.GetItemInHandsBehaviourCfg();
   if (!behavior)
    return false;
   kind = behavior.m_iType;
  }
  bool walkingPreview = actor.ML213UsesWalkingPreview();
  bool smg = walkingPreview && MLHeldCategory192.IsSMG(item) && kind == ItemBehaviorType.FIREARMS;
  bool rifle = kind == ItemBehaviorType.FIREARMS && !smg;
  bool pistol = kind == ItemBehaviorType.PISTOLS;
  bool toolHolding = kind == ItemBehaviorType.TWOHANDED || kind == ItemBehaviorType.POLEARMS;
  bool sledge = walkingPreview && MLHeldCategory192.IsWalkingTool(item) && toolHolding;
  bool twoHands = kind == ItemBehaviorType.TWOHANDED && !sledge;
  bool flash = walkingPreview && kind == ItemBehaviorType.ONEHANDED;
  bool oneHand = kind == ItemBehaviorType.ONEHANDED && !flash;
  bool heavy = kind == ItemBehaviorType.HEAVY;
  bool polearm = kind == ItemBehaviorType.POLEARMS && !sledge;
  bool changed = !ReferenceItemSet || ReferenceItem != item;
  changed = changed || HeldEditor != rifle || PistolBank != pistol || SmgWalkingEditor != smg;
  changed = changed || OtherHeldEditor != twoHands || OneHandEditor != oneHand || SledgeWalkingEditor != sledge;
  changed = changed || HeavyEditor != heavy || PolearmEditor != polearm || OneHandWalkingEditor != flash;
  HeldEditor = rifle;
  SmgWalkingEditor = smg;
  PistolBank = pistol;
  OtherHeldEditor = twoHands;
  SledgeWalkingEditor = sledge;
  OneHandEditor = oneHand;
  OneHandWalkingEditor = flash;
  HeavyEditor = heavy;
  PolearmEditor = polearm;
  if (changed)
  {
   ReferenceItemSet = true;
   ReferenceItem = item;
   NeutralReference = null;
   LeftReference = null;
   LeftSolved = null;
   RightSolved = null;
   Failed[0] = false;
   Failed[1] = false;
   NeutralTried = false;
   NeutralTime = 0;
   Settled = 0;
   LastSide = -1;
   for (int resetIndex = 0; resetIndex < Last.Count(); resetIndex++)
    Last[resetIndex] = 1000;
  }
  return true;
 }
 void UpdatePlayer(PlayerBase actor, float dt, float lean)
 {
  PlayerInput = true;
  EntityAI currentItem = actor.GetHumanInventory().GetEntityInHands();
  bool referenceChanged = !ReferenceItemSet || currentItem != ReferenceItem;
  referenceChanged = referenceChanged || ReferenceHeldBank != HeldEditor || ReferencePistolBank != PistolBank;
  referenceChanged = referenceChanged || ReferenceBatBank != OtherHeldEditor || ReferenceOneHandBank != OneHandEditor;
  referenceChanged = referenceChanged || ReferenceHeavyBank != HeavyEditor || ReferencePolearmBank != PolearmEditor;
  referenceChanged = referenceChanged || ReferenceSmgWalkingBank != SmgWalkingEditor || ReferenceToolWalkingBank != SledgeWalkingEditor;
  referenceChanged = referenceChanged || ReferenceOneHandWalkingBank != OneHandWalkingEditor;
  if (referenceChanged)
  {
   ReferenceItemSet = true;
   ReferenceItem = currentItem;
   ReferenceHeldBank = HeldEditor;
   ReferencePistolBank = PistolBank;
   ReferenceBatBank = OtherHeldEditor;
   ReferenceOneHandBank = OneHandEditor;
   ReferenceHeavyBank = HeavyEditor;
   ReferencePolearmBank = PolearmEditor;
   ReferenceSmgWalkingBank = SmgWalkingEditor;
   ReferenceToolWalkingBank = SledgeWalkingEditor;
   ReferenceOneHandWalkingBank = OneHandWalkingEditor;
   NeutralReference = null;
   LeftReference = null;
   LeftSolved = null;
   RightSolved = null;
   Failed[0] = false;
   Failed[1] = false;
   NeutralTried = false;
   NeutralTime = 0;
   Settled = 0;
   LastSide = -1;
   for (int resetIndex = 0; resetIndex < Last.Count(); resetIndex++)
    Last[resetIndex] = 1000;
  }
  Update(actor, dt, lean, false);
 }
 void ReleasePlayer(PlayerBase actor)
 {
  if (!Bound)
   return;
  actor.AnimSetFloat(ActiveVar, 0);
  actor.AnimSetFloat(HeldVar, 0);
  actor.AnimSetFloat(PreviewVar, 0);
  actor.AnimSetFloat(PreviewLeanVar, 0);
  actor.AnimSetFloat(NativeVar, 0);
  // Force cached coefficient writes when this path is re-entered; other
  // stance banks own the same body controls between visits.
  for (int index = 0; index < Last.Count(); index++)
   Last[index] = 1000;
  LastSide = -1;
  Settled = 0;
  NeutralTime = 0;
 }
 void Update(PlayerBase actor, float dt, float lean, bool nativeReference)
 {
  ML183Preset.Init();
  if (HeldEditor)
   ML190Preset.Init();
  if (OtherHeldEditor)
   ML193Preset.Init();
  if (PistolBank)
   ML196Preset.Init();
  if (OneHandEditor)
   ML200Preset.Init();
  if (HeavyEditor)
   ML202Preset.Init();
  if (PolearmEditor)
   ML204Preset.Init();
  if (SmgWalkingEditor)
   ML207Preset.Init();
  if (SledgeWalkingEditor)
   ML209Preset.Init();
  if (OneHandWalkingEditor)
   ML211Preset.Init();
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
  if (!PlayerInput)
  {
   actor.AnimSetBool(RaisedVar, false);
   actor.AnimSetBool(ADSVar, false);
   actor.AnimSetFloat(LeanVar, lean);
   actor.AnimSetFloat(PreviewVar, 1);
   actor.AnimSetFloat(PreviewLeanVar, lean);
  }
  else
  {
   // Use real native Q/E and aiming state, not the removed NPC clock.
   actor.AnimSetFloat(PreviewVar, 0);
   actor.AnimSetFloat(PreviewLeanVar, 0);
  }
  bool heldPose = actor.GetHumanInventory().GetEntityInHands() != null;
  float heldWeight = 0;
  if (heldPose)
   heldWeight = 1;
  actor.AnimSetFloat(HeldVar, heldWeight);
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
   Print("[MLSHARED187] native_reference=" + nativeReference + " shared_lean=" + lean);
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
   sampled = LeftReference != null;
  else if (side == 1)
   sampled = RightSolved != null;
  if (side >= 0 && !sampled && !Failed[side] && Settled > 0.35)
  {
   ML172Snapshot source = Capture(actor);
   if (side == 0)
   {
    LeftReference = source;
    if (!LeftReference)
     Failed[0] = true;
   }
   else
   {
    RightSolved = Solve(source, false);
    if (!RightSolved || RightSolved.Count() != 84)
     Failed[1] = true;
   }
   Print("[MLSHARED187] native_side_sampled side=" + side);
  }
  // Centre has ZERO lean corrections and ZERO F6/F7 output. Sample once;
  // never sample during a partial transition or after corrected output.
  if (Math.AbsFloat(lean) < 0.001)
   NeutralTime += Math.Clamp(dt, 0, 0.1);
  else
   NeutralTime = 0;
  if (!NeutralTried && NeutralTime > 0.35)
  {
   NeutralTried = true;
   NeutralReference = Capture(actor);
   if (NeutralReference)
    Print("[MLSHARED187] neutral_bone_basis_cached");
  }
  if (LeftReference && NeutralReference && !LeftSolved && !Failed[0])
  {
   LeftSolved = Solve(LeftReference, true);
   if (!LeftSolved || LeftSolved.Count() != 84)
    Failed[0] = true;
   bool mirrorReady = !Failed[0];
   Print("[MLSHARED187] neutral_relative_mirror_ready=" + mirrorReady);
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
  ML149Data leftBody = ML183BodyState.Left;
  ML149Data rightBody = ML183BodyState.Right;
  if (HeldEditor)
  {
   leftValues = ML190WeaponState.LeftValues;
   rightValues = ML190WeaponState.RightValues;
   leftBody = ML190BodyState.Left;
   rightBody = ML190BodyState.Right;
  }
  if (OtherHeldEditor)
  {
   leftValues = ML193WeaponState.LeftValues;
   rightValues = ML193WeaponState.RightValues;
   leftBody = ML193BodyState.Left;
   rightBody = ML193BodyState.Right;
  }
  if (PistolBank)
  {
   leftValues = ML196WeaponState.LeftValues;
   rightValues = ML196WeaponState.RightValues;
   leftBody = ML196BodyState.Left;
   rightBody = ML196BodyState.Right;
  }
  if (OneHandEditor)
  {
   leftValues = ML200WeaponState.LeftValues;
   rightValues = ML200WeaponState.RightValues;
   leftBody = ML200BodyState.Left;
   rightBody = ML200BodyState.Right;
  }
  if (HeavyEditor)
  {
   leftValues = ML202WeaponState.LeftValues;
   rightValues = ML202WeaponState.RightValues;
   leftBody = ML202BodyState.Left;
   rightBody = ML202BodyState.Right;
  }
  if (PolearmEditor)
  {
   leftValues = ML204WeaponState.LeftValues;
   rightValues = ML204WeaponState.RightValues;
   leftBody = ML204BodyState.Left;
   rightBody = ML204BodyState.Right;
  }
  if (SmgWalkingEditor)
  {
   leftValues = ML207WeaponState.LeftValues;
   rightValues = ML207WeaponState.RightValues;
   leftBody = ML207BodyState.Left;
   rightBody = ML207BodyState.Right;
  }
  if (SledgeWalkingEditor)
  {
   leftValues = ML209WeaponState.LeftValues;
   rightValues = ML209WeaponState.RightValues;
   leftBody = ML209BodyState.Left;
   rightBody = ML209BodyState.Right;
  }
  if (OneHandWalkingEditor)
  {
   leftValues = ML211WeaponState.LeftValues;
   rightValues = ML211WeaponState.RightValues;
   leftBody = ML211BodyState.Left;
   rightBody = ML211BodyState.Right;
  }
  for (int armIndex = 0; armIndex < 9; armIndex++)
  {
   float armValue = WeightedArm(armIndex, leftValues, rightValues, lw, rw);
   if (heldPose && !HeldEditor && !OtherHeldEditor && !PistolBank && !OneHandEditor && !HeavyEditor && !PolearmEditor && !SmgWalkingEditor && !SledgeWalkingEditor && !OneHandWalkingEditor && armIndex < 6)
    armValue = 0;
   Write(actor, 84 + armIndex, armValue);
  }
  for (int partIndex = 0; partIndex < 24; partIndex++)
  {
   ML149Part leftPart = leftBody.Parts[partIndex];
   ML149Part rightPart = rightBody.Parts[partIndex];
   bool heldArmPart = heldPose && !HeldEditor && !OtherHeldEditor && !PistolBank && !OneHandEditor && !HeavyEditor && !PolearmEditor && !SmgWalkingEditor && !SledgeWalkingEditor && !OneHandWalkingEditor && partIndex >= 8 && partIndex <= 15;
   for (int componentIndex = 0; componentIndex < 6; componentIndex++)
   {
    float bodyValue = leftPart.ComponentValue(componentIndex) * lw;
    bodyValue += rightPart.ComponentValue(componentIndex) * rw;
    if (componentIndex < 3)
     bodyValue *= 0.01;
    else
     bodyValue *= -Math.DEG2RAD;
    if (heldArmPart)
     bodyValue = 0;
    int writeIndex = 93 + partIndex * 6 + componentIndex;
    Write(actor, writeIndex, bodyValue);
   }
  }
 }
};
