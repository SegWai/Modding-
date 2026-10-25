// Native Q/E input and weapon IK are retained. Offline Mosin calibration only.
class MLADSLeanSettings
{
 static bool Enabled = true;
 static bool Inspection = false;
 static bool HasGraph = false;
};

modded class PlayerBase
{
 protected int m_MLADSLeanGateVar = -1;
 protected bool m_MLADSLeanBound;
 protected float m_MLADSLeanGate;
 protected bool m_MLADSLeanLastTarget;

 override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
 {
  super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() != this || !GetAnimInterface())
   return;
  if (!m_MLADSLeanBound)
  {
   m_MLADSLeanBound = true;
   m_MLADSLeanGateVar = GetAnimInterface().BindVariableFloat("MLADSLeanGate");
   MLADSLeanSettings.HasGraph = m_MLADSLeanGateVar >= 0;
   Print("[MLADSLEAN1] gate_binding=" + m_MLADSLeanGateVar);
   if (m_MLADSLeanGateVar < 0)
    Print("[MLADSLEAN1] Native workspace active or graph control missing; native lean remains.");
  }
  if (m_MLADSLeanGateVar < 0)
   return;
  HumanMovementState state = new HumanMovementState();
  GetMovementState(state);
  EntityAI held = GetHumanInventory().GetEntityInHands();
  bool mosin = held && held.IsKindOf("Mosin9130");
  bool upright = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool aiming = IsInIronsights() || IsInOptics();
  bool target = MLADSLeanSettings.Enabled && IsAlive() && !IsUnconscious() && mosin && upright && state.m_iMovement == 0 && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE && IsRaised() && IsWeaponRaiseCompleted() && (aiming || MLADSLeanSettings.Inspection);
  float targetValue = 0;
  if (target)
   targetValue = 1;
  float step = Math.Clamp(pDt, 0, 0.25) / 0.18;
  if (m_MLADSLeanGate < targetValue)
   m_MLADSLeanGate = Math.Min(targetValue, m_MLADSLeanGate + step);
  else
   m_MLADSLeanGate = Math.Max(targetValue, m_MLADSLeanGate - step);
  // Animation graph writes are deliberately inside CommandHandler.
  AnimSetFloat(m_MLADSLeanGateVar, m_MLADSLeanGate);
  if (target != m_MLADSLeanLastTarget)
  {
   m_MLADSLeanLastTarget = target;
   Print("[MLADSLEAN1] target=" + target + " mosin=" + mosin + " upright=" + upright + " movement=" + state.m_iMovement + " ADS=" + aiming + " inspection=" + MLADSLeanSettings.Inspection);
  }
 }
};
