// Raised first-person view follows neutral rifle-relative framing and orientation.
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
   m_ML58EyeCorrection = vector.Zero;
  }
  vector headTM[4];
  player.GetBoneTransformMS(result.m_iDirectBone, headTM);
  vector nativeEye = result.m_CameraTM[3].Multiply4(headTM);
  vector weaponWS[4];
  vector playerWS[4];
  vector weaponMS[4];
  weapon.GetTransform(weaponWS);
  player.GetTransform(playerWS);
  Math3D.MatrixInvMultiply4(playerWS, weaponWS, weaponMS);
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
   vector sightPos;
   vector sightDir;
   weapon.GetCameraPoint(weapon.GetCurrentMuzzle(), sightPos, sightDir);
   vector sightMS[4];
   HumanItemAccessor accessor = player.GetItemAccessor();
   if (accessor.WeaponGetCameraPointMSTransform(weapon, sightPos, sightDir, sightMS))
   {
    for (int sightAxis = 0; sightAxis < 3; sightAxis++)
     desiredView[sightAxis] = sightMS[sightAxis];
    desiredEye = sightMS[3] - sightMS[2] * 0.12 + vector.Up * 0.06;
   }
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
  // Preserve the neutral rifle-to-view orientation as well as eye spacing.
  // The two basis vectors are interpolated then orthonormalized; free-look
  // fades to the original native camera. Only this first-person result changes.
  vector viewForward = result.m_CameraTM[2] * (1.0 - weight) + desiredView[2] * weight;
  vector viewUp = result.m_CameraTM[1] * (1.0 - weight) + desiredView[1] * weight;
  vector alignedView[4];
  if (viewForward.LengthSq() > 0.000001 && viewUp.LengthSq() > 0.000001)
  {
   Math3D.DirectionAndUpMatrix(viewForward.Normalized(), viewUp.Normalized(), alignedView);
   for (int outAxis = 0; outAxis < 3; outAxis++)
    result.m_CameraTM[outAxis] = alignedView[outAxis];
  }
  // Explicit player-model coordinates: do not feed a model-space correction
  // back through the head-bound camera's local offset interpretation.
  result.m_iDirectBone = -1;
  result.m_iDirectBoneMode = 0;
  result.m_fPositionModelSpace = 1.0;
  result.m_CameraTM[3] = correctedEye;
  m_ML59LogElapsed += step;
  if (m_ML59LogElapsed >= 1.0 && player.GetCurrentCamera() == this)
  {
   m_ML59LogElapsed = 0;
   string cameraReadback = "[MLCAM65] raised_alignment reference=" + m_ML58HasReference;
   cameraReadback += " weight=" + weight;
   cameraReadback += " eye_delta_ms=" + m_ML58EyeCorrection;
   cameraReadback += " view_forward_ms=" + result.m_CameraTM[2];
   cameraReadback += " weapon_side_axis_ms=" + weaponMS[2];
   cameraReadback += " bone_mode=" + result.m_iDirectBoneMode;
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
