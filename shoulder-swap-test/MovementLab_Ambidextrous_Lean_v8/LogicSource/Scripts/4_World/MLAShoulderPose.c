// Experimental handedness layer. Inventory/FSM stays native; never duplicate,
// delete, detach, or locally teleport a held weapon. Graph publishes left pose.
class MLAShoulderSettings
{
 static bool LeftRequested;
 static bool LeftActive;
 static bool NeutralReady;
};
class MLAShoulderSolution
{
 ref ML172Frame SourceWeaponFrame;
 bool ContactReported;
 ref ML144Rot TriggerBasis;
 vector TriggerOffset;
 ref ML144Rot AnchorPelvisBasis;
 vector AnchorPelvisPosition;
 ref array<float> Values = new array<float>;
};
class MLAShoulderPose
{
 ref TStringArray Names = new TStringArray;
 ref array<int> Parents = new array<int>;
 ref array<int> Opposite = new array<int>;
 ref array<int> Vars = new array<int>;
 ref array<float> Last = new array<float>;
 ref array<ref MLAShoulderSolution> Cache = new array<ref MLAShoulderSolution>;
 ref array<bool> Failed = new array<bool>;
 ref ML172Snapshot Neutral;
 EntityAI HeldWeapon;
 bool Tried;
 bool Bound;
 bool NeutralTried;
 bool NoticeShown;
 string LastStatus;
 int ActiveVar = -1;
 ref array<int> AnchorVars = new array<int>;
 float LastAnchor[6];
 int PreviousKey = -1;
 float Settled;
 float NeutralTime;
 float ContactSettle;
 int ContactKey = -1;
 int CaptureRevision = -1;
 int BodyRevision = -1;
 void MLAShoulderPose()
 {
  BuildNames();
  for (int key = 0; key < 36; key++)
  {
   Cache.Insert(null);
   Failed.Insert(false);
  }
 }
 void BuildNames()
 {
  Names.Insert("Spine3"); Parents.Insert(-1); Opposite.Insert(0);
  Names.Insert("Neck"); Parents.Insert(0); Opposite.Insert(1);
  Names.Insert("Neck1"); Parents.Insert(1); Opposite.Insert(2);
  Names.Insert("Head"); Parents.Insert(2); Opposite.Insert(3);
  Names.Insert("LeftShoulder"); Parents.Insert(0); Opposite.Insert(27);
  Names.Insert("LeftArm"); Parents.Insert(4); Opposite.Insert(28);
  Names.Insert("LeftArmRoll"); Parents.Insert(5); Opposite.Insert(29);
  Names.Insert("LeftForeArm"); Parents.Insert(6); Opposite.Insert(30);
  Names.Insert("LeftForeArmRoll"); Parents.Insert(7); Opposite.Insert(31);
  Names.Insert("LeftHand"); Parents.Insert(8); Opposite.Insert(32);
  Names.Insert("LeftHandRing"); Parents.Insert(9); Opposite.Insert(33);
  Names.Insert("LeftHandRing1"); Parents.Insert(10); Opposite.Insert(34);
  Names.Insert("LeftHandRing2"); Parents.Insert(11); Opposite.Insert(35);
  Names.Insert("LeftHandRing3"); Parents.Insert(12); Opposite.Insert(36);
  Names.Insert("LeftHandMiddle1"); Parents.Insert(9); Opposite.Insert(40);
  Names.Insert("LeftHandMiddle2"); Parents.Insert(14); Opposite.Insert(41);
  Names.Insert("LeftHandMiddle3"); Parents.Insert(15); Opposite.Insert(42);
  Names.Insert("LeftHandIndex1"); Parents.Insert(9); Opposite.Insert(43);
  Names.Insert("LeftHandIndex2"); Parents.Insert(17); Opposite.Insert(44);
  Names.Insert("LeftHandIndex3"); Parents.Insert(18); Opposite.Insert(45);
  Names.Insert("LeftHandThumb1"); Parents.Insert(9); Opposite.Insert(37);
  Names.Insert("LeftHandThumb2"); Parents.Insert(20); Opposite.Insert(38);
  Names.Insert("LeftHandThumb3"); Parents.Insert(21); Opposite.Insert(39);
  Names.Insert("LeftHandPinky"); Parents.Insert(9); Opposite.Insert(46);
  Names.Insert("LeftHandPinky1"); Parents.Insert(23); Opposite.Insert(47);
  Names.Insert("LeftHandPinky2"); Parents.Insert(24); Opposite.Insert(48);
  Names.Insert("LeftHandPinky3"); Parents.Insert(25); Opposite.Insert(49);
  Names.Insert("RightShoulder"); Parents.Insert(0); Opposite.Insert(4);
  Names.Insert("RightArm"); Parents.Insert(27); Opposite.Insert(5);
  Names.Insert("RightArmRoll"); Parents.Insert(28); Opposite.Insert(6);
  Names.Insert("RightForeArm"); Parents.Insert(29); Opposite.Insert(7);
  Names.Insert("RightForeArmRoll"); Parents.Insert(30); Opposite.Insert(8);
  Names.Insert("RightHand"); Parents.Insert(31); Opposite.Insert(9);
  Names.Insert("RightHandRing"); Parents.Insert(32); Opposite.Insert(10);
  Names.Insert("RightHandRing1"); Parents.Insert(33); Opposite.Insert(11);
  Names.Insert("RightHandRing2"); Parents.Insert(34); Opposite.Insert(12);
  Names.Insert("RightHandRing3"); Parents.Insert(35); Opposite.Insert(13);
  Names.Insert("RightHandThumb1"); Parents.Insert(32); Opposite.Insert(20);
  Names.Insert("RightHandThumb2"); Parents.Insert(37); Opposite.Insert(21);
  Names.Insert("RightHandThumb3"); Parents.Insert(38); Opposite.Insert(22);
  Names.Insert("RightHandMiddle1"); Parents.Insert(32); Opposite.Insert(14);
  Names.Insert("RightHandMiddle2"); Parents.Insert(40); Opposite.Insert(15);
  Names.Insert("RightHandMiddle3"); Parents.Insert(41); Opposite.Insert(16);
  Names.Insert("RightHandIndex1"); Parents.Insert(32); Opposite.Insert(17);
  Names.Insert("RightHandIndex2"); Parents.Insert(43); Opposite.Insert(18);
  Names.Insert("RightHandIndex3"); Parents.Insert(44); Opposite.Insert(19);
  Names.Insert("RightHandPinky"); Parents.Insert(32); Opposite.Insert(23);
  Names.Insert("RightHandPinky1"); Parents.Insert(46); Opposite.Insert(24);
  Names.Insert("RightHandPinky2"); Parents.Insert(47); Opposite.Insert(25);
  Names.Insert("RightHandPinky3"); Parents.Insert(48); Opposite.Insert(26);
 }
 void Bind(PlayerBase actor)
 {
  if (Tried)
   return;
  Tried = true;
  ActiveVar = actor.GetAnimInterface().BindVariableFloat("MLASwapActive");
  Bound = ActiveVar >= 0;
  int count = Names.Count() * 6;
  for (int index = 0; index < count; index++)
  {
   int id = actor.GetAnimInterface().BindVariableFloat("MLASwapC" + index);
   Bound = Bound && id >= 0 && id != ActiveVar;
   foreach (int previous : Vars)
    Bound = Bound && id != previous;
   Vars.Insert(id);
   Last.Insert(1000);
  }
  for (int anchor = 0; anchor < 6; anchor++)
  {
   int anchorId = actor.GetAnimInterface().BindVariableFloat("MLASwapAnchor" + anchor);
   Bound = Bound && anchorId >= 0;
   AnchorVars.Insert(anchorId);
   LastAnchor[anchor] = 1000;
  }
  Print("[MLASHOULDER8] full-profile build; bound=" + Bound + " coefficients=" + Vars.Count());
 }
 ML172Snapshot Capture(PlayerBase actor)
 {
  ML172Snapshot result = new ML172Snapshot;
  foreach (string boneName : Names)
  {
   int boneId = actor.GetBoneIndexByName(boneName);
   if (boneId == -1)
   {
    Print("[MLASHOULDER] capture missing bone=" + boneName);
    return null;
   }
   vector tm[4];
   actor.GetBoneTransformMS(boneId, tm);
   vector x = tm[0]; vector y = tm[1]; vector z = tm[2];
   if (x.LengthSq() < 0.5 || y.LengthSq() < 0.5 || z.LengthSq() < 0.5)
   {
    Print("[MLASHOULDER] capture invalid frame=" + boneName);
    return null;
   }
   x.Normalize(); y.Normalize(); z.Normalize();
   ML172Frame frame = new ML172Frame;
   frame.Position = tm[3];
   frame.Orientation = new ML144Rot;
   frame.Orientation.A = Vector(x[0], y[0], z[0]);
   frame.Orientation.B = Vector(x[1], y[1], z[1]);
   frame.Orientation.C = Vector(x[2], y[2], z[2]);
   result.Frames.Insert(frame);
  }
  return result;
 }
 ML172Frame ReadWeaponFrame(PlayerBase actor)
 {
  Weapon_Base gun = Weapon_Base.Cast(actor.GetHumanInventory().GetEntityInHands());
  HumanItemAccessor accessor = actor.GetItemAccessor();
  if (!gun || !accessor)
   return null;
  vector sightPosition;
  vector sightDirection;
  gun.GetCameraPoint(gun.GetCurrentMuzzle(), sightPosition, sightDirection);
  vector tm[4];
  if (!accessor.WeaponGetCameraPointMSTransform(gun, sightPosition, sightDirection, tm))
   return null;
  vector x = tm[0]; vector y = tm[1]; vector z = tm[2];
  if (x.LengthSq() < 0.5 || y.LengthSq() < 0.5 || z.LengthSq() < 0.5)
   return null;
  x.Normalize(); y.Normalize(); z.Normalize();
  ML172Frame frame = new ML172Frame;
  frame.Position = tm[3];
  frame.Orientation = new ML144Rot;
  frame.Orientation.A = Vector(x[0], y[0], z[0]);
  frame.Orientation.B = Vector(x[1], y[1], z[1]);
  frame.Orientation.C = Vector(x[2], y[2], z[2]);
  return frame;
 }
 void ReportContact(PlayerBase actor, MLAShoulderSolution solution, int key, float dt)
 {
  if (!solution || !solution.SourceWeaponFrame)
  {
   ContactKey = -1;
   ContactSettle = 0;
   return;
  }
  if (ContactKey != key)
  {
   ContactKey = key;
   ContactSettle = 0;
  }
  ContactSettle += Math.Clamp(dt, 0, 0.05);
  if (solution.ContactReported || ContactSettle < 0.25)
   return;
  solution.ContactReported = true;
  ML172Frame actual = ReadWeaponFrame(actor);
  ML172Frame itemFrame = ReadItemFrame(actor);
  ML172Frame anchorFrame = ReadBoneFrame(actor, "Weapon");
  if (itemFrame)
   Print("[MLASHOULDER8] actual_item_model_position=" + itemFrame.Position);
  if (anchorFrame)
   Print("[MLASHOULDER8] profile_anchor_position=" + anchorFrame.Position);
  Print("[MLASHOULDER8] full_profile_offset=" + solution.TriggerOffset);
  if (!actual)
   return;
  ML172Frame original = solution.SourceWeaponFrame;
  vector a = actual.Orientation.A; vector b = actual.Orientation.B; vector c = actual.Orientation.C;
  vector x = original.Orientation.A; vector y = original.Orientation.B; vector z = original.Orientation.C;
  vector sourceForward = Vector(x[2], y[2], z[2]);
  vector currentForward = Vector(a[2], b[2], c[2]);
  vector sourceUp = Vector(x[1], y[1], z[1]);
  vector currentUp = Vector(a[1], b[1], c[1]);
  float forwardDot = vector.Dot(sourceForward, currentForward);
  float upDot = vector.Dot(sourceUp, currentUp);
  Print("[MLASHOULDER8] context=" + key + " original_sightMS=" + original.Position + " left_sightMS=" + actual.Position);
  Print("[MLASHOULDER8] source_forward=" + sourceForward + " left_forward=" + currentForward + " forward_dot=" + forwardDot + " up_dot=" + upDot);
  int leftHand = actor.GetBoneIndexByName("LeftHand");
  int rightHand = actor.GetBoneIndexByName("RightHand");
  if (leftHand != -1 && rightHand != -1)
  {
   vector triggerPosition = actor.GetBonePositionMS(leftHand);
   vector supportPosition = actor.GetBonePositionMS(rightHand);
   Print("[MLASHOULDER8] left_trigger_wristMS=" + triggerPosition + " right_support_wristMS=" + supportPosition);
  }
 }
 ML144Rot ReflectRotation(ML144Rot deformation)
 {
  ML144Rot reflected = new ML144Rot;
  vector a = deformation.A; vector b = deformation.B; vector c = deformation.C;
  reflected.A = Vector(a[0], -a[1], -a[2]);
  reflected.B = Vector(-b[0], b[1], b[2]);
  reflected.C = Vector(-c[0], c[1], c[2]);
  return reflected;
 }
 MLAShoulderSolution Solve(PlayerBase actor, ML172Snapshot source)
 {
  if (!Neutral || !source || source.Frames.Count() != Names.Count())
   return null;
  ML172Frame root = source.Frames[0];
  ML172Frame neutralRoot = Neutral.Frames[0];
  ML144Rot neutralRootInverse = neutralRoot.Orientation.Inverse();
  // Anatomical chest frame is its deformation from neutral, not the bone's
  // own non-XYZ basis. The approved torso/legs/lean direction stay unchanged.
  ML144Rot chest = root.Orientation.Times(neutralRootInverse);
  ML144Rot chestInverse = chest.Inverse();
  array<vector> positions = new array<vector>;
  array<ref ML144Rot> rotations = new array<ref ML144Rot>;
  MLAShoulderSolution solution = new MLAShoulderSolution;
  for (int index = 0; index < Names.Count(); index++)
  {
   ML172Frame sourceBone = source.Frames[index];
   if (index == 0)
   {
    for (int zero = 0; zero < 6; zero++)
     solution.Values.Insert(0);
    positions.Insert(root.Position);
    rotations.Insert(root.Orientation);
    continue;
   }
   int otherIndex = Opposite[index];
   ML172Frame oppositeBone = source.Frames[otherIndex];
   ML172Frame neutralOther = Neutral.Frames[otherIndex];
   ML172Frame neutralBone = Neutral.Frames[index];
   ML144Rot otherInverse = neutralOther.Orientation.Inverse();
   ML144Rot localOther = chestInverse.Times(oppositeBone.Orientation);
   ML144Rot deformation = localOther.Times(otherInverse);
   ML144Rot reflected = ReflectRotation(deformation);
   ML144Rot neutralApplied = reflected.Times(neutralBone.Orientation);
   ML144Rot desiredRotation = chest.Times(neutralApplied);
   vector oppositeRelative = oppositeBone.Position - root.Position;
   vector localPosition = chestInverse.Apply(oppositeRelative);
   localPosition[0] = -localPosition[0];
   vector rotatedPosition = chest.Apply(localPosition);
   vector desiredPosition = root.Position + rotatedPosition;
   int parentIndex = Parents[index];
   ML172Frame sourceParent = source.Frames[parentIndex];
   ML144Rot sourceParentInverse = sourceParent.Orientation.Inverse();
   ML144Rot desiredParent = rotations[parentIndex];
   ML144Rot inherited = desiredParent.Times(sourceParentInverse);
   vector relative = sourceBone.Position - sourceParent.Position;
   vector inheritedRelative = inherited.Apply(relative);
   vector desiredParentPosition = positions[parentIndex];
   vector currentPosition = desiredParentPosition + inheritedRelative;
   ML144Rot currentRotation = inherited.Times(sourceBone.Orientation);
   ML144Rot currentInverse = currentRotation.Inverse();
   ML144Rot correction = desiredRotation.Times(currentInverse);
   correction.AppendNative(solution.Values);
   vector translation = desiredPosition - currentPosition;
   if (translation.Length() > 0.65)
    return null;
   solution.Values.Insert(translation[0]);
   solution.Values.Insert(translation[1]);
   solution.Values.Insert(translation[2]);
   positions.Insert(desiredPosition);
   rotations.Insert(desiredRotation);
  }
  foreach (float component : solution.Values)
  {
   if (component != component || Math.AbsFloat(component) > 3.141593)
    return null;
  }
  int triggerIndex = Names.Find("RightHand");
  int leftIndex = Names.Find("LeftHand");
  ML172Frame nativeAnchor = ReadBoneFrame(actor, "Weapon");
  ML172Frame sourcePelvis = ReadBoneFrame(actor, "Pelvis");
  if (triggerIndex < 0 || leftIndex < 0 || !nativeAnchor || !sourcePelvis)
  {
   Print("[MLASHOULDER8] required weapon-anchor/pelvis bone unavailable");
   return null;
  }
  // Solve the COMPLETE native hand-to-sight rigid transform. Copying only
  // the original right-hand axes leaves the profile translation unmirrored.
  ML172Frame sourceSight = ReadWeaponFrame(actor);
  if (!sourceSight)
   return null;
  solution.SourceWeaponFrame = sourceSight;
  ML144Rot leftGrip = rotations[leftIndex];
  ML144Rot leftGripInverse = leftGrip.Inverse();
  ML172Frame sourceTrigger = source.Frames[triggerIndex];
  ML144Rot triggerInverse = sourceTrigger.Orientation.Inverse();
  ML144Rot sightInverse = sourceSight.Orientation.Inverse();
  // S * (C^-1 * sightR) * S: reflect position/forward/up while retaining
  // a proper right-handed weapon frame (never negative-scale the gun mesh).
  ML144Rot sightLocal = chestInverse.Times(sourceSight.Orientation);
  ML144Rot reflectedSight = ReflectRotation(sightLocal);
  ML144Rot desiredSight = chest.Times(reflectedSight);
  vector sightRelative = sourceSight.Position - root.Position;
  vector sightLocalPosition = chestInverse.Apply(sightRelative);
  sightLocalPosition[0] = -sightLocalPosition[0];
  vector sightReflectedPosition = chest.Apply(sightLocalPosition);
  vector desiredSightPosition = root.Position + sightReflectedPosition;
  ML144Rot inverseProfile = sightInverse.Times(sourceTrigger.Orientation);
  ML144Rot desiredAnchor = desiredSight.Times(inverseProfile);
  vector sightFromTrigger = sourceSight.Position - sourceTrigger.Position;
  vector profileOffset = triggerInverse.Apply(sightFromTrigger);
  vector desiredProfileOffset = desiredAnchor.Apply(profileOffset);
  vector desiredAnchorPosition = desiredSightPosition - desiredProfileOffset;
  vector leftPosition = positions[leftIndex];
  vector anchorFromLeft = desiredAnchorPosition - leftPosition;
  solution.TriggerBasis = leftGripInverse.Times(desiredAnchor);
  solution.TriggerOffset = leftGripInverse.Apply(anchorFromLeft);
  if (solution.TriggerOffset.Length() > 0.5)
   return null;
  ML144Rot pelvisInverse = sourcePelvis.Orientation.Inverse();
  solution.AnchorPelvisBasis = pelvisInverse.Times(nativeAnchor.Orientation);
  vector anchorRelative = nativeAnchor.Position - sourcePelvis.Position;
  solution.AnchorPelvisPosition = pelvisInverse.Apply(anchorRelative);
  return solution;
 }
 ML172Frame ReadBoneFrame(PlayerBase actor, string boneName)
 {
  int id = actor.GetBoneIndexByName(boneName);
  if (id == -1)
   return null;
  vector tm[4];
  actor.GetBoneTransformMS(id, tm);
  return FrameFromMatrix(tm);
 }
 ML172Frame FrameFromMatrix(vector tm[4])
 {
  vector x = tm[0]; vector y = tm[1]; vector z = tm[2];
  if (x.LengthSq() < 0.5 || y.LengthSq() < 0.5 || z.LengthSq() < 0.5)
   return null;
  x.Normalize(); y.Normalize(); z.Normalize();
  ML172Frame frame = new ML172Frame;
  frame.Position = tm[3];
  frame.Orientation = new ML144Rot;
  frame.Orientation.A = Vector(x[0], y[0], z[0]);
  frame.Orientation.B = Vector(x[1], y[1], z[1]);
  frame.Orientation.C = Vector(x[2], y[2], z[2]);
  return frame;
 }
 ML172Frame ReadItemFrame(PlayerBase actor)
 {
  EntityAI item = actor.GetHumanInventory().GetEntityInHands();
  if (!item)
   return null;
  vector actorWorld[4];
  vector itemWorld[4];
  vector itemModel[4];
  actor.GetTransform(actorWorld);
  item.GetTransform(itemWorld);
  Math3D.MatrixInvMultiply4(actorWorld, itemWorld, itemModel);
  return FrameFromMatrix(itemModel);
 }
 bool WriteAnchor(PlayerBase actor, MLAShoulderSolution solution)
 {
  array<float> values = new array<float>;
  if (solution)
  {
   ML172Frame hand = ReadBoneFrame(actor, "LeftHand");
   ML172Frame pelvis = ReadBoneFrame(actor, "Pelvis");
   if (!hand || !pelvis || !solution.TriggerBasis || !solution.AnchorPelvisBasis)
    return false;
   // Unedited anchor = current pelvis * cached native anchor-local frame.
   // Do NOT read Weapon after correction: that would feed output back in.
   ML144Rot sourceBasis = pelvis.Orientation.Times(solution.AnchorPelvisBasis);
   ML144Rot sourceInverse = sourceBasis.Inverse();
   ML144Rot desiredBasis = hand.Orientation.Times(solution.TriggerBasis);
   ML144Rot correction = desiredBasis.Times(sourceInverse);
   correction.AppendNative(values);
   vector parentRelative = pelvis.Orientation.Apply(solution.AnchorPelvisPosition);
   vector baselinePosition = pelvis.Position + parentRelative;
   vector handOffset = hand.Orientation.Apply(solution.TriggerOffset);
   vector desiredPosition = hand.Position + handOffset;
   vector translation = desiredPosition - baselinePosition;
   if (translation.Length() > 1.5)
    return false;
   values.Insert(translation[0]);
   values.Insert(translation[1]);
   values.Insert(translation[2]);
  }
  else
  {
   for (int zero = 0; zero < 6; zero++)
    values.Insert(0);
  }
  for (int index = 0; index < 6; index++)
  {
   float value = values[index];
   if (value != value || Math.AbsFloat(value) > 3.141593)
    return false;
  }
  for (int anchorWrite = 0; anchorWrite < 6; anchorWrite++)
  {
   if (LastAnchor[anchorWrite] != values[anchorWrite])
   {
    LastAnchor[anchorWrite] = values[anchorWrite];
    actor.AnimSetFloat(AnchorVars[anchorWrite], values[anchorWrite]);
   }
  }
  return true;
 }
 void Write(PlayerBase actor, MLAShoulderSolution solution)
 {
  bool active = solution != null;
  if (!WriteAnchor(actor, solution))
  {
   active = false;
   WriteAnchor(actor, null);
   Print("[MLASHOULDER8] anchor rejected; left publication disabled");
  }
  MLAShoulderSettings.LeftActive = active;
  float enabled = 0;
  if (active)
   enabled = 1;
  actor.AnimSetFloat(ActiveVar, enabled);
  for (int index = 0; index < Vars.Count(); index++)
  {
   float value = 0;
   if (active)
    value = solution.Values[index];
   if (Math.AbsFloat(Last[index] - value) > 0.000001)
   {
    Last[index] = value;
    actor.AnimSetFloat(Vars[index], value);
   }
  }
 }
 void ApplyCamera(PlayerBase actor)
 {
  HumanInputController cameraInput = actor.GetInputController();
  if (cameraInput)
   cameraInput.Override3rdIsRightShoulder(HumanInputControllerOverrideType.ENABLED, !MLAShoulderSettings.LeftActive);
 }
 void SetStatus(string message)
 {
  if (LastStatus == message)
   return;
  LastStatus = message;
  Print("[MLASHOULDER] " + message);
 }
 void Update(PlayerBase actor, HumanMovementState state, float dt)
 {
  Bind(actor);
  if (!Bound)
   return;
  if (!actor.IsAlive() || actor.IsUnconscious() || !actor.GetCommand_Move())
  {
   Write(actor, null);
   HumanInputController stoppedInput = actor.GetInputController();
   if (stoppedInput)
    stoppedInput.Override3rdIsRightShoulder(HumanInputControllerOverrideType.DISABLED, true);
   return;
  }
  EntityAI held = actor.GetHumanInventory().GetEntityInHands();
  bool standing = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool crouch = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDCROUCH;
  if (!NeutralTried && !held && standing && state.m_iMovement == 0 && !actor.IsRaised() && Math.AbsFloat(state.m_fLeaning) < 0.001)
  {
   NeutralTime += Math.Clamp(dt, 0, 0.1);
   if (NeutralTime > 0.4)
   {
    NeutralTried = true;
    Neutral = Capture(actor);
    MLAShoulderSettings.NeutralReady = Neutral != null;
    Print("[MLASHOULDER] neutral_reference_ready=" + (Neutral != null));
   }
  }
  else
   NeutralTime = 0;
  if (held != HeldWeapon)
  {
   HeldWeapon = held;
   for (int clear = 0; clear < Cache.Count(); clear++)
   {
    Cache[clear] = null;
    Failed[clear] = false;
   }
   PreviousKey = -1;
   Settled = 0;
  }
  bool supported = MLADSLeanWeaponSupport106.Profile(held) > 0;
  bool eligible = supported && (standing || crouch) && state.m_iMovement <= 2 && actor.IsRaised() && actor.IsWeaponRaiseCompleted();
  if (!eligible || !MLAShoulderSettings.LeftRequested || !MLADSLeanSettings.Enabled)
  {
   Write(actor, null);
   PreviousKey = -1;
   Settled = 0;
   ApplyCamera(actor);
   SetStatus("inactive: weapon not raised/ready, unsupported context, or right requested");
   return;
  }
  if (!Neutral)
  {
   Write(actor, null);
   ApplyCamera(actor);
   SetStatus("waiting for neutral skeleton reference");
   if (!NoticeShown)
   {
    Print("[MLASHOULDER] First stand centred empty-handed for half a second to cache neutral bone axes.");
    NoticeShown = true;
   }
   return;
  }
  int leanSide = 1;
  if (state.m_fLeaning < -0.98)
   leanSide = 0;
  else if (state.m_fLeaning > 0.98)
   leanSide = 2;
  bool leanStable = Math.AbsFloat(state.m_fLeaning) < 0.01 || Math.AbsFloat(state.m_fLeaning) > 0.98;
  int stanceKey = 0;
  if (crouch)
   stanceKey = 1;
  int key = stanceKey * 18 + state.m_iMovement * 6 + leanSide * 2;
  if (actor.IsInIronsights() || actor.IsInOptics())
   key++;
  if (key != PreviousKey)
  {
   PreviousKey = key;
   Settled = 0;
  }
  MLAShoulderSolution cached = Cache[key];
  if (!cached && !Failed[key])
  {
   // New context: outputs ZERO until sampling finishes. Never recapture the
   // corrected pose on later frames. Aim near centre to avoid baking aim twice.
   Write(actor, null);
   HumanCommandWeapons aim = actor.GetCommandModifier_Weapons();
   bool centred = false;
   if (aim)
    centred = Math.AbsFloat(aim.GetBaseAimingAngleUD()) < 5 && Math.AbsFloat(aim.GetBaseAimingAngleLR()) < 5;
   if (leanStable && centred && actor.MLAShoulderCaptureReady())
    Settled += Math.Clamp(dt, 0, 0.05);
   else
    Settled = 0;
   if (Settled > 0.4)
   {
    ML172Snapshot source = Capture(actor);
    cached = Solve(actor, source);
    Cache[key] = cached;
    Failed[key] = cached == null;
    Print("[MLASHOULDER] context=" + key + " solved=" + (cached != null));
   }
  }
  Write(actor, cached);
  ReportContact(actor, cached, key, dt);
  ApplyCamera(actor);
  if (cached)
   SetStatus("left pose ACTIVE: arms and weapon publisher enabled");
  else if (Failed[key])
   SetStatus("left solve REJECTED for current weapon/pose; camera stays right");
  else
   SetStatus("sampling right pose: raise gun and aim level briefly; camera stays right");
 }
};
