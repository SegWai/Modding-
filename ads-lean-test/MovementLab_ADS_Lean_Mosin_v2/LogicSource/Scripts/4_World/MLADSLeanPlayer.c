// Native Q/E input and weapon IK retained. Offline Mosin calibration only.
class MLADSLeanSettings
{
 static bool Enabled = true;
 static bool Inspection = false;
 static bool HasGraph = false;
 static string Status = "Waiting for graph validation";
};
modded class PlayerBase
{
 protected int m_MLADSLeanGateVar = -1;
 protected int m_MLADSLeanCanaryVar = -1;
 protected int m_MLADSLeanNativeLeanVar = -1;
 protected int m_MLADSLeanNativeMoveVar = -1;
 protected bool m_MLADSLeanBound;
 protected int m_MLADSLeanBindAttempts;
 protected int m_MLADSLeanNextBind;
 protected int m_MLADSLeanNextReport;
 protected float m_MLADSLeanGate;
 protected bool m_MLADSLeanLastTarget;

 override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
 {
  super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() != this || !GetAnimInterface())
   return;
  int now = GetGame().GetTime();
  if (!m_MLADSLeanBound && m_MLADSLeanBindAttempts < 5 && now >= m_MLADSLeanNextBind)
  {
   m_MLADSLeanBindAttempts++;
   m_MLADSLeanNextBind = now + 2000;
   m_MLADSLeanGateVar = GetAnimInterface().BindVariableFloat("MLADSLeanGate");
   m_MLADSLeanCanaryVar = GetAnimInterface().BindVariableFloat("MLADSLeanCanary");
   m_MLADSLeanNativeLeanVar = GetAnimInterface().BindVariableFloat("Lean");
   m_MLADSLeanNativeMoveVar = GetAnimInterface().BindVariableFloat("MovementSpeed");
   // Zero may be valid. Require four distinct valid bindings, not just >= 0.
   m_MLADSLeanBound = m_MLADSLeanGateVar >= 0 && m_MLADSLeanCanaryVar >= 0 && m_MLADSLeanNativeLeanVar >= 0 && m_MLADSLeanNativeMoveVar >= 0 && m_MLADSLeanGateVar != m_MLADSLeanCanaryVar && m_MLADSLeanGateVar != m_MLADSLeanNativeLeanVar && m_MLADSLeanGateVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanCanaryVar != m_MLADSLeanNativeLeanVar && m_MLADSLeanCanaryVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanNativeLeanVar != m_MLADSLeanNativeMoveVar;
   MLADSLeanSettings.HasGraph = m_MLADSLeanBound;
   Print("[MLADSLEAN2] bind_valid=" + m_MLADSLeanBound + " gate=" + m_MLADSLeanGateVar + " canary=" + m_MLADSLeanCanaryVar + " nativeLean=" + m_MLADSLeanNativeLeanVar + " nativeMove=" + m_MLADSLeanNativeMoveVar + " attempt=" + m_MLADSLeanBindAttempts);
  }
  HumanMovementState state = new HumanMovementState();
  GetMovementState(state);
  EntityAI held = GetHumanInventory().GetEntityInHands();
  bool mosin = held && held.IsKindOf("Mosin9130");
  bool upright = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool aiming = IsInIronsights() || IsInOptics();
  bool raised = IsRaised();
  bool ready = IsWeaponRaiseCompleted();
  bool target = m_MLADSLeanBound && MLADSLeanSettings.Enabled && IsAlive() && !IsUnconscious() && mosin && upright && state.m_iMovement == 0 && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE && raised && ready && (aiming || MLADSLeanSettings.Inspection);
  float targetValue = 0;
  if (target)
   targetValue = 1;
  float step = Math.Clamp(pDt, 0, 0.25) / 0.18;
  if (m_MLADSLeanGate < targetValue)
   m_MLADSLeanGate = Math.Min(targetValue, m_MLADSLeanGate + step);
  else
   m_MLADSLeanGate = Math.Max(targetValue, m_MLADSLeanGate - step);
  // Never write a float when the graph bindings failed validation.
  if (m_MLADSLeanBound)
   AnimSetFloat(m_MLADSLeanGateVar, m_MLADSLeanGate);
  MLADSLeanSettings.Status = "graph=" + m_MLADSLeanBound + " gate=" + m_MLADSLeanGate + " ADS=" + aiming + " raised=" + raised + " ready=" + ready + " idle=" + state.m_iMovement + " stance=" + state.m_iStanceIdx + " cmd=" + pCurrentCommandID;
  if (now >= m_MLADSLeanNextReport || target != m_MLADSLeanLastTarget)
  {
   m_MLADSLeanNextReport = now + 2000;
   m_MLADSLeanLastTarget = target;
   Print("[MLADSLEAN2] " + MLADSLeanSettings.Status + " mosin=" + mosin + " custom=" + MLADSLeanSettings.Enabled + " inspection=" + MLADSLeanSettings.Inspection);
  }
 }
};
