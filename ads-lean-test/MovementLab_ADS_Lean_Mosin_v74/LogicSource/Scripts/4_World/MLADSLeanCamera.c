// Raised first-person view retains native look direction and rifle-relative eye spacing.
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

 // Reframe eye position only; never borrow orientation from the rifle pose.
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
  HumanInputController cameraInput = player.GetInputController();
  if (cameraInput && cameraInput.CameraIsFreeLook())
   weight = 0;
  vector targetCorrection = (desiredEye - nativeEye) * weight;
  float step = Math.Clamp(dt, 0, 0.05);

  // The graph already smooths lean/raise. Do not add a second independent
  // position filter here while orientation follows the current rifle pose.
  m_ML58EyeCorrection = targetCorrection;
  // Leave native head binding intact outside the correction; no persistent
  // unbound camera while lowered, neutral, or during ordinary shutdown.
  if (weight < 0.0001 && m_ML58EyeCorrection.LengthSq() < 0.000001)
   return;
  vector correctedEye = nativeEye + m_ML58EyeCorrection;
  // Keep native input-driven orientation from super.OnUpdate. Rifle pose
  // rotation must never steer the player's view when raising during a lean.
  // Preserve the existing eye spacing and interpolated wrist parent below.
  // Preserve native model-space look direction, but express it relative to
  // the rifle-holding wrist. The engine then samples the rendered/interpolated
  // wrist for camera and arms together, instead of an unbound script snapshot.
  int primaryHand = player.GetBoneIndexByName("RightHand");
  if (primaryHand == -1)
   return;
  vector modelView[4];
  for (int modelAxis = 0; modelAxis < 3; modelAxis++)
   modelView[modelAxis] = result.m_CameraTM[modelAxis];
  modelView[3] = correctedEye;
  vector modelViewForward = modelView[2];
  vector primaryPose[4];
  player.GetBoneTransformMS(primaryHand, primaryPose);
  Math3D.MatrixInvMultiply4(primaryPose, modelView, result.m_CameraTM);
  result.m_iDirectBone = primaryHand;
  result.m_iDirectBoneMode = 3;
  result.m_fPositionModelSpace = 0;
  result.m_fUseHeading = 0;
  result.m_fDistance = 0;
  result.m_fIgnoreParentRoll = 0;
  result.m_fIgnoreParentPitch = 0;
  result.m_fIgnoreParentYaw = 0;
  result.m_bUpdateEveryFrame = false;
  m_ML59LogElapsed += step;
  if (m_ML59LogElapsed >= 1.0 && player.GetCurrentCamera() == this)
  {
   m_ML59LogElapsed = 0;
   string cameraReadback = "[MLCAM74] raised_alignment reference=" + m_ML58HasReference;
   cameraReadback += " weight=" + weight;
   cameraReadback += " eye_delta_ms=" + m_ML58EyeCorrection;
   cameraReadback += " view_forward_ms=" + modelViewForward;
   cameraReadback += " pose_camera_forward_ms=" + weaponMS[2];
   cameraReadback += " bone_mode=" + result.m_iDirectBoneMode;
   cameraReadback += " parent_bone=RightHand";
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
