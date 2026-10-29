// Camera framing only. The shared animation pose and native camera collision
// remain untouched. Both native/custom comparison modes use the same framing.
modded class DayZPlayerCamera3rdPerson
{
 override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
 {
  super.OnUpdate(pDt, pOutResult);
  if (GetGame().IsMultiplayer() || !m_MovementState)
   return;
  if (m_MovementState.m_CommandTypeId != DayZPlayerConstants.COMMANDID_MOVE)
   return;
  bool standingFrame = m_MovementState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || m_MovementState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool crouchingFrame = m_MovementState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH || m_MovementState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDCROUCH;
  if (!standingFrame && !crouchingFrame)
   return;
  pOutResult.m_fDistance = Math.Max(pOutResult.m_fDistance, 4.0);
  vector inspectionPivot = pOutResult.m_CameraTM[3];
  float pivotDrop = 0.10;
  if (standingFrame)
   pivotDrop = 0.35;
  inspectionPivot[1] = inspectionPivot[1] - pivotDrop;
  pOutResult.m_CameraTM[3] = inspectionPivot;
 }
};
