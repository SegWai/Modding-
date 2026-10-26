// First-person camera retains native head parent and view rotation throughout.
// ADS/optic camera roll handling is unchanged. No graph/item/bone writes here.
class MLADSLeanCameraMath
{
 static float SmoothRoll(float current, float target, float dt)
 {
  float boundedDt = Math.Clamp(dt, 0, 0.05);
  float alpha = boundedDt / (0.18 + boundedDt);
  return current + (target - current) * alpha;
 }
 static void ApplyLocalRoll(float degrees, inout DayZPlayerCameraResult result)
 {
  if (Math.AbsFloat(degrees) < 0.0001)
   return;
  vector basis[3];
  basis[0] = result.m_CameraTM[0];
  basis[1] = result.m_CameraTM[1];
  basis[2] = result.m_CameraTM[2];
  vector localRoll[3];
  Math3D.YawPitchRollMatrix(Vector(0, 0, degrees), localRoll);
  vector tilted[3];
  Math3D.MatrixMultiply3(basis, localRoll, tilted);
  result.m_CameraTM[0] = tilted[0];
  result.m_CameraTM[1] = tilted[1];
  result.m_CameraTM[2] = tilted[2];
 }
};
modded class DayZPlayerCamera1stPerson
{
 protected float m_ML46RaisedRoll;
 protected EntityAI m_ML58ReferenceWeapon;
 protected bool m_ML58HasReference;
 protected vector m_ML58EyeWeaponLocal;
 protected vector m_ML58EyeCorrection;
 protected vector m_ML59ReferenceView[4];
 protected float m_ML59LogElapsed;
 protected bool m_ML85HasSightHeight;
 protected float m_ML85SightHeightRatio;
 protected vector m_ML79PreviousEyeOffset;
 protected bool m_ML79HasEyeSample;

 // Reframe the raised rifle without changing aim direction, bones or item pose.
 // Preserve neutral eye-to-weapon spacing as the custom pose moves the weapon.
 protected void ML58AlignRaisedView(float dt, PlayerBase player, inout DayZPlayerCameraResult result)
 {
  Weapon_Base weapon = Weapon_Base.Cast(player.GetHumanInventory().GetEntityInHands());
  bool supported = weapon && (weapon.IsKindOf("AK74") || weapon.IsKindOf("Mosin9130"));
  if (!supported || result.m_iDirectBoneMode != 1)
   return;
  if (m_ML58ReferenceWeapon != weapon)
  {
   m_ML58ReferenceWeapon = weapon;
   m_ML58HasReference = false;
   m_ML85HasSightHeight = false;
   m_ML58EyeCorrection = vector.Zero;
  }
  vector headTM[4];
  player.GetBoneTransformMS(result.m_iDirectBone, headTM);
  vector nativeEye = result.m_CameraTM[3].Multiply4(headTM);
  // Match the native camera path: use the current animation-pose camera
  // transform, not the separately updated world item transform.
  vector liveSightPosition;
  vector liveSightDirection;
  weapon.GetCameraPoint(weapon.GetCurrentMuzzle(), liveSightPosition, liveSightDirection);
  vector weaponMS[4];
  HumanItemAccessor poseAccessor = player.GetItemAccessor();
  if (!poseAccessor.WeaponGetCameraPointMSTransform(weapon, liveSightPosition, liveSightDirection, weaponMS))
   return;
  float weight = player.ML58RaisedViewWeight();
  if (player.IsRaised() && player.IsWeaponRaiseCompleted() && weight < 0.01)
  {
   m_ML58EyeWeaponLocal = nativeEye.InvMultiply4(weaponMS);
   vector neutralView[4];
   for (int viewAxis = 0; viewAxis < 3; viewAxis++)
    neutralView[viewAxis] = result.m_CameraTM[viewAxis];
   neutralView[3] = nativeEye;
   Math3D.MatrixInvMultiply4(weaponMS, neutralView, m_ML59ReferenceView);
   m_ML58HasReference = true;
   vector neutralSightDelta = weaponMS[3] - nativeEye;
   float neutralDepth = vector.Dot(neutralSightDelta, result.m_CameraTM[2]);
   if (neutralDepth > 0.04)
   {
    float neutralHeight = vector.Dot(neutralSightDelta, result.m_CameraTM[1]);
    m_ML85SightHeightRatio = neutralHeight / neutralDepth;
    m_ML85HasSightHeight = true;
   }
  }
  vector desiredEye = nativeEye;
  vector desiredView[4];
  for (int nativeAxis = 0; nativeAxis < 4; nativeAxis++)
   desiredView[nativeAxis] = result.m_CameraTM[nativeAxis];
  if (m_ML58HasReference)
  {
   Math3D.MatrixMultiply4(weaponMS, m_ML59ReferenceView, desiredView);
   desiredEye = desiredView[3];
  }
  else if (weight > 0)
  {
   // Safe raised-view fallback until a neutral raised reference is observed.
   for (int sightAxis = 0; sightAxis < 3; sightAxis++)
    desiredView[sightAxis] = weaponMS[sightAxis];
   desiredEye = weaponMS[3] - weaponMS[2] * 0.12 + vector.Up * 0.06;
  }
  // With a calibrated neutral raised eye, follow the current left-lean
  // rifle position fully. Its pose already contains the native lean blend.
  // Keep the old bounded fallback until that neutral reference is available.
  float positionWeight = weight;
  if (m_ML58HasReference)
  {
   positionWeight = player.ML85RaisedPositionWeight();
   if (player.ML85LeftRaisedViewActive() && m_ML85HasSightHeight)
   {
    // Hold the sight at the neutral raised screen height throughout Q.
    // Preserve horizontal framing/depth, and never rotate the view or gun.
    vector sightFromEye = weaponMS[3] - desiredEye;
    float sightDepth = vector.Dot(sightFromEye, result.m_CameraTM[2]);
    if (sightDepth > 0.04)
    {
     float sightHeight = vector.Dot(sightFromEye, result.m_CameraTM[1]);
     float heightError = sightHeight - sightDepth * m_ML85SightHeightRatio;
     desiredEye = desiredEye + result.m_CameraTM[1] * heightError;
    }
   }
  }
  HumanInputController cameraInput = player.GetInputController();
  if (cameraInput && cameraInput.CameraIsFreeLook())
  {
   weight = 0;
   positionWeight = 0;
  }
  vector targetCorrection = (desiredEye - nativeEye) * positionWeight;
  float step = Math.Clamp(dt, 0, 0.05);

  // The target already includes the shared custom pose gate and lean amount.
  // Apply it in the same update: do not wait for native raise completion and
  // start another camera-only transition after the arm pose has arrived.
  m_ML58EyeCorrection = targetCorrection;
  // Leave native head binding intact outside the correction; no persistent
  // unbound camera while lowered, neutral, or during ordinary shutdown.
  if (m_ML58EyeCorrection.LengthSq() < 0.000001)
   return;
  vector correctedEye = nativeEye + m_ML58EyeCorrection;
  // Always retain the native head parent and native view orientation.
  // Re-express the same corrected eye relative to that head. Never swap the
  // camera parent to the IK-controlled wrist, even after raise completion:
  // wrist pose/interpolation changes must not move the camera discontinuously.
  result.m_CameraTM[3] = correctedEye.InvMultiply4(headTM);
  result.m_bUpdateEveryFrame = false;
  bool wristReady = player.IsRaised() && player.IsWeaponRaiseCompleted();
  string cameraParent = "Head";
  vector modelViewForward = result.m_CameraTM[2];
  vector currentEyeOffset = result.m_CameraTM[3];
  float eyeOffsetStep = 0;
  if (m_ML79HasEyeSample)
   eyeOffsetStep = vector.Distance(currentEyeOffset, m_ML79PreviousEyeOffset);
  m_ML79PreviousEyeOffset = currentEyeOffset;
  m_ML79HasEyeSample = true;
  m_ML59LogElapsed += step;
  if ((m_ML59LogElapsed >= 1.0 || (eyeOffsetStep > 0.03 && m_ML59LogElapsed >= 0.10)) && player.GetCurrentCamera() == this)
  {
   m_ML59LogElapsed = 0;
   string cameraReadback = "[MLCAM91] raised_alignment reference=" + m_ML58HasReference;
   cameraReadback += " weight=" + weight;
   cameraReadback += " position_weight=" + positionWeight;
   cameraReadback += " neutral_sight_height_valid=" + m_ML85HasSightHeight;
   cameraReadback += " eye_delta_ms=" + m_ML58EyeCorrection;
   cameraReadback += " view_forward_ms=" + modelViewForward;
   cameraReadback += " pose_camera_forward_ms=" + weaponMS[2];
   cameraReadback += " bone_mode=" + result.m_iDirectBoneMode;
   cameraReadback += " parent_bone=" + cameraParent;
   cameraReadback += " raise_complete=" + wristReady;
   cameraReadback += " camera_timing=shared_pose_gate";
   cameraReadback += " eye_offset_step_m=" + eyeOffsetStep;
   cameraReadback += " head_local_eye=" + currentEyeOffset;
   Print(cameraReadback);
  }
 }
 override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
 {
  super.OnUpdate(pDt, pOutResult);
  PlayerBase leanPlayer = PlayerBase.Cast(m_pPlayer);
  float targetRoll = 0;
  if (leanPlayer)
  {
   // Native raised orientation stays level; no extra head/rifle camera roll.
   ML58AlignRaisedView(pDt, leanPlayer, pOutResult);
  }
  m_ML46RaisedRoll = MLADSLeanCameraMath.SmoothRoll(m_ML46RaisedRoll, targetRoll, pDt);
  MLADSLeanCameraMath.ApplyLocalRoll(m_ML46RaisedRoll, pOutResult);
  if (leanPlayer && leanPlayer.GetCurrentCamera() == this)
  {
   MLADSLeanSettings.FirstPersonRoll = m_ML46RaisedRoll;
   MLADSLeanSettings.FirstPersonRollCamera = GetCameraName();
  }
 }
};
// Optics inherits this OnUpdate; its own native AdjustCameraParameters still runs.
modded class DayZPlayerCameraIronsights
{
 protected float m_ML46SightRoll;
 override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
 {
  super.OnUpdate(pDt, pOutResult);
  PlayerBase leanPlayer = PlayerBase.Cast(m_pPlayer);
  float targetRoll = 0;
  if (leanPlayer)
   targetRoll = leanPlayer.MLADSLeanFirstPersonRollTarget(true);
  m_ML46SightRoll = MLADSLeanCameraMath.SmoothRoll(m_ML46SightRoll, targetRoll, pDt);
  MLADSLeanCameraMath.ApplyLocalRoll(m_ML46SightRoll, pOutResult);
  if (leanPlayer && leanPlayer.GetCurrentCamera() == this)
  {
   MLADSLeanSettings.FirstPersonRoll = m_ML46SightRoll;
   MLADSLeanSettings.FirstPersonRollCamera = GetCameraName();
  }
 }
};
