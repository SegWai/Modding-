// Offline Mosin lean test. Player and designated demo use the same graph/pose.
class MLADSLeanSettings
{
 static bool Enabled = true;
 static bool Inspection = false;
 static bool HasGraph = false;
 static string Status = "Waiting for graph validation";
 static PlayerBase DemoActor;
 // Last moving ADS gait of the selected player; start at walk until measured.
 static int DemoGait = 1;
};
modded class PlayerBase
{
 protected int m_MLADSLeanGateVar = -1;
 protected int m_MLADSLeanCanaryVar = -1;
 protected int m_MLADSLeanAmountVar = -1;
 protected int m_MLADSLeanNativeLeanVar = -1;
 protected int m_MLADSLeanNativeMoveVar = -1;
 protected bool m_MLADSLeanBound;
 protected int m_MLADSLeanBindAttempts;
 protected int m_MLADSLeanNextBind;
 protected int m_MLADSLeanNextReport;
 protected float m_MLADSLeanGate;
 protected float m_MLADSLeanAmount;
 protected bool m_MLADSLeanLastTarget;
 protected bool m_MLADSLeanNeutralMeasured;
 protected float m_MLADSLeanNeutralHeadX;
 protected float m_MLADSLeanNeutralChestX;

 protected bool m_MLADSLeanDemo;
 protected bool m_MLADSLeanDemoPaused;
 protected bool m_MLADSLeanDemoStanceRequested;
 protected bool m_MLADSLeanDemoReady;
 protected bool m_MLADSLeanDemoWasRaised;
 protected int m_MLADSLeanDemoRaiseTransitions;
 protected vector m_MLADSLeanDemoCenter;
 protected vector m_MLADSLeanDemoRight;
 protected float m_MLADSLeanDemoSign = -1;
 protected float m_MLADSLeanDemoAmount;
 protected int m_MLADSLeanDemoArmIK = -1;
 protected int m_MLADSLeanDemoADS = -1;
 protected int m_MLADSLeanDemoRaised = -1;
 protected int m_MLADSLeanDemoAim = -1;
 protected int m_MLADSLeanDemoAimIK = -1;
 protected int m_MLADSLeanDemoAimUD = -1;
 protected bool m_MLADSLeanDemoNativeBound;

 void MLADSLeanStartDemo()
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() == this)
   return;
  m_MLADSLeanDemo = true;
  m_MLADSLeanDemoStanceRequested = false;
  m_MLADSLeanDemoReady = false;
  m_MLADSLeanDemoCenter = GetPosition();
  vector facing = GetDirection();
  facing[1] = 0;
  if (facing.Length() < 0.001)
   facing = "0 0 1";
  facing.Normalize();
  m_MLADSLeanDemoRight = Vector(facing[2], 0, -facing[0]);
  m_MLADSLeanDemoSign = -1;
  HumanInputController input = GetInputController();
  if (input)
   input.SetDisabled(false);
  Print("[MLADSLEAN10] demo_started center=" + m_MLADSLeanDemoCenter + " half_span_m=2 native_locomotion=true");
 }
 void MLADSLeanToggleDemoPause()
 {
  m_MLADSLeanDemoPaused = !m_MLADSLeanDemoPaused;
  Print("[MLADSLEAN10] demo_paused=" + m_MLADSLeanDemoPaused);
 }
 void MLADSLeanStopDemo()
 {
  if (!m_MLADSLeanDemo)
   return;
  m_MLADSLeanDemo = false;
  m_MLADSLeanDemoStanceRequested = false;
  m_MLADSLeanDemoReady = false;
  HumanInputController input = GetInputController();
  if (input)
  {
   input.OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
   input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
   input.OverrideRaise(HumanInputControllerOverrideType.DISABLED, false);
  }
  HumanCommandMove move = GetCommand_Move();
  if (move)
   move.ForceStance(-1);
  HumanCommandWeapons weapons = GetCommandModifier_Weapons();
  if (weapons)
   weapons.SetADS(false);
 }
 protected void MLADSLeanUpdateDemoInput(float dt)
 {
  if (!m_MLADSLeanDemo || GetGame().IsMultiplayer())
   return;
  if (!IsAlive() || IsUnconscious())
  {
   MLADSLeanStopDemo();
   return;
  }
  HumanInputController input = GetInputController();
  if (!input)
   return;
  if (!GetCommand_Move())
  {
   m_MLADSLeanDemoStanceRequested = false;
   m_MLADSLeanDemoReady = false;
   StartCommand_Move();
  }
  // ForceStance is a persistent lock, not a per-frame raise input.
  // V9 reissued it every frame and alternated stance 0/3 in the runtime log.
  HumanCommandMove move = GetCommand_Move();
  if (move && !m_MLADSLeanDemoStanceRequested)
  {
   move.ForceStance(DayZPlayerConstants.STANCEIDX_RAISEDERECT);
   m_MLADSLeanDemoStanceRequested = true;
   Print("[MLADSLEAN10] demo_stance_requested_once");
  }
  vector offset = GetPosition() - m_MLADSLeanDemoCenter;
  float lateral = vector.Dot(offset, m_MLADSLeanDemoRight);
  float oldSign = m_MLADSLeanDemoSign;
  if (m_MLADSLeanDemoSign < 0 && lateral <= -2)
   m_MLADSLeanDemoSign = 1;
  else if (m_MLADSLeanDemoSign > 0 && lateral >= 2)
   m_MLADSLeanDemoSign = -1;
  if (oldSign != m_MLADSLeanDemoSign)
   Print("[MLADSLEAN10] demo_reverse lateral_m=" + lateral + " direction=" + m_MLADSLeanDemoSign);
  float step = Math.Clamp(dt, 0, 0.25) / 0.2;
  if (m_MLADSLeanDemoAmount < m_MLADSLeanDemoSign)
   m_MLADSLeanDemoAmount = Math.Min(m_MLADSLeanDemoSign, m_MLADSLeanDemoAmount + step);
  else
   m_MLADSLeanDemoAmount = Math.Max(m_MLADSLeanDemoSign, m_MLADSLeanDemoAmount - step);
  float speed = MLADSLeanSettings.DemoGait;
  if (m_MLADSLeanDemoPaused || !m_MLADSLeanDemoReady)
   speed = 0;
  input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, speed);
  input.OverrideMovementAngle(HumanInputControllerOverrideType.ENABLED, 90 * m_MLADSLeanDemoSign);
  // The stance lock owns raise state; do not compete with a raise override.
 }
 override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
 {
  // Input overrides are set before native processing, only on the designated NPC.
  MLADSLeanUpdateDemoInput(pDt);
  super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
  bool localPlayer = GetGame().GetPlayer() == this;
  if (GetGame().IsMultiplayer() || (!localPlayer && !m_MLADSLeanDemo) || !GetAnimInterface())
   return;
  int now = GetGame().GetTime();
  if (!m_MLADSLeanBound && m_MLADSLeanBindAttempts < 5 && now >= m_MLADSLeanNextBind)
  {
   m_MLADSLeanBindAttempts++;
   m_MLADSLeanNextBind = now + 2000;
   m_MLADSLeanGateVar = GetAnimInterface().BindVariableFloat("MLADSLeanGate");
   m_MLADSLeanCanaryVar = GetAnimInterface().BindVariableFloat("MLADSLeanCanary");
   m_MLADSLeanAmountVar = GetAnimInterface().BindVariableFloat("MLADSLeanAmount");
   m_MLADSLeanNativeLeanVar = GetAnimInterface().BindVariableFloat("Lean");
   m_MLADSLeanNativeMoveVar = GetAnimInterface().BindVariableFloat("MovementSpeed");
   // Valid zero is allowed; all five float bindings must be distinct.
   m_MLADSLeanBound = m_MLADSLeanGateVar >= 0 && m_MLADSLeanCanaryVar >= 0 && m_MLADSLeanAmountVar >= 0 && m_MLADSLeanNativeLeanVar >= 0 && m_MLADSLeanNativeMoveVar >= 0 && m_MLADSLeanGateVar != m_MLADSLeanCanaryVar && m_MLADSLeanGateVar != m_MLADSLeanAmountVar && m_MLADSLeanGateVar != m_MLADSLeanNativeLeanVar && m_MLADSLeanGateVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanCanaryVar != m_MLADSLeanAmountVar && m_MLADSLeanCanaryVar != m_MLADSLeanNativeLeanVar && m_MLADSLeanCanaryVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanAmountVar != m_MLADSLeanNativeLeanVar && m_MLADSLeanAmountVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanNativeLeanVar != m_MLADSLeanNativeMoveVar;
   if (localPlayer)
    MLADSLeanSettings.HasGraph = m_MLADSLeanBound;
   Print("[MLADSLEAN10] demo=" + m_MLADSLeanDemo + " bind_valid=" + m_MLADSLeanBound + " gate=" + m_MLADSLeanGateVar + " amount=" + m_MLADSLeanAmountVar + " canary=" + m_MLADSLeanCanaryVar + " nativeLean=" + m_MLADSLeanNativeLeanVar + " nativeMove=" + m_MLADSLeanNativeMoveVar);
   if (m_MLADSLeanDemo)
   {
    m_MLADSLeanDemoArmIK = GetAnimInterface().BindVariableInt("ArmIK");
    m_MLADSLeanDemoADS = GetAnimInterface().BindVariableBool("ADS");
    m_MLADSLeanDemoRaised = GetAnimInterface().BindVariableBool("Raised");
    m_MLADSLeanDemoAim = GetAnimInterface().BindVariableFloat("AimX");
    m_MLADSLeanDemoAimIK = GetAnimInterface().BindVariableFloat("AimIKX");
    m_MLADSLeanDemoAimUD = GetAnimInterface().BindVariableFloat("AimY");
    m_MLADSLeanDemoNativeBound = m_MLADSLeanDemoArmIK >= 0 && m_MLADSLeanDemoADS >= 0 && m_MLADSLeanDemoRaised >= 0 && m_MLADSLeanDemoADS != m_MLADSLeanDemoRaised && m_MLADSLeanNativeLeanVar >= 0 && m_MLADSLeanNativeMoveVar >= 0 && m_MLADSLeanNativeLeanVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanDemoAim >= 0 && m_MLADSLeanDemoAimIK >= 0 && m_MLADSLeanDemoAimUD >= 0;
   }
  }
  HumanMovementState state = new HumanMovementState();
  GetMovementState(state);
  EntityAI held = GetHumanInventory().GetEntityInHands();
  bool mosin = held && held.IsKindOf("Mosin9130");
  bool supportedStance = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDCROUCH;
  bool aiming = IsInIronsights() || IsInOptics();
  bool raised = IsRaised();
  bool ready = IsWeaponRaiseCompleted();
  // Match the player's actual native gait; never change the player's input.
  if (localPlayer && mosin && raised && (aiming || MLADSLeanSettings.Inspection))
  {
   if (state.m_iMovement == 1 || state.m_iMovement == 2)
    MLADSLeanSettings.DemoGait = state.m_iMovement;
  }
  bool nativeADS = aiming;
  // The camera ADS flags belong to the selected player. The NPC requests
  // weapon ADS below, but must really reach raised stance before activation.
  if (m_MLADSLeanDemo)
  {
   raised = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
   // Use the real weapon-raise completion, not a synthetic ready flag.
   ready = IsWeaponRaiseCompleted();
   aiming = raised && ready;
   m_MLADSLeanDemoReady = raised && ready;
   if (raised != m_MLADSLeanDemoWasRaised)
   {
    m_MLADSLeanDemoRaiseTransitions++;
    m_MLADSLeanDemoWasRaised = raised;
   }
  }
  bool actorReady = !m_MLADSLeanDemo || m_MLADSLeanDemoNativeBound;
  bool target = actorReady && m_MLADSLeanBound && MLADSLeanSettings.Enabled && IsAlive() && !IsUnconscious() && mosin && supportedStance && state.m_iMovement <= 2 && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE && raised && ready && (aiming || MLADSLeanSettings.Inspection);
  float targetValue = 0;
  if (target)
   targetValue = 1;
  float stepGate = Math.Clamp(pDt, 0, 0.25) / 0.18;
  if (m_MLADSLeanGate < targetValue)
   m_MLADSLeanGate = Math.Min(targetValue, m_MLADSLeanGate + stepGate);
  else
   m_MLADSLeanGate = Math.Max(targetValue, m_MLADSLeanGate - stepGate);
  m_MLADSLeanAmount = Math.Clamp(state.m_fLeaning, -1, 1);
  if (m_MLADSLeanDemo)
   m_MLADSLeanAmount = m_MLADSLeanDemoAmount;
  // All graph writes stay inside CommandHandler, after native processing.
  if (m_MLADSLeanBound)
  {
   AnimSetFloat(m_MLADSLeanGateVar, m_MLADSLeanGate);
   AnimSetFloat(m_MLADSLeanAmountVar, m_MLADSLeanAmount);
  }
  if (m_MLADSLeanDemo && m_MLADSLeanDemoNativeBound)
  {
   AnimSetBool(m_MLADSLeanDemoADS, m_MLADSLeanDemoReady);
   AnimSetBool(m_MLADSLeanDemoRaised, raised);
   if (m_MLADSLeanDemoReady)
   {
    // Aim bit 0 and both hand-chain bits, only after the native raise finishes.
    AnimSetInt(m_MLADSLeanDemoArmIK, 7);
    AnimSetFloat(m_MLADSLeanNativeLeanVar, m_MLADSLeanDemoAmount);
    AnimSetFloat(m_MLADSLeanDemoAim, 0);
    AnimSetFloat(m_MLADSLeanDemoAimIK, 0);
    AnimSetFloat(m_MLADSLeanDemoAimUD, 0);
   }
   HumanCommandWeapons weapons = GetCommandModifier_Weapons();
   if (weapons)
    weapons.SetADS(m_MLADSLeanDemoReady);
  }
  // Keep each diagnostic expression small for the Enforce compiler.
  string status = "graph=" + m_MLADSLeanBound;
  status += " gate=" + m_MLADSLeanGate;
  status += " lean=" + m_MLADSLeanAmount;
  status += " ADS_requested=" + aiming;
  status += " native_ADS=" + nativeADS;
  status += " native_raised=" + IsRaised();
  status += " raise_complete=" + IsWeaponRaiseCompleted();
  status += " moving=" + state.m_iMovement;
  status += " stance=" + state.m_iStanceIdx;
  if (m_MLADSLeanDemo)
  {
   status += " requested_gait=" + MLADSLeanSettings.DemoGait;
   status += " patrol_ready=" + m_MLADSLeanDemoReady;
   status += " raise_transitions=" + m_MLADSLeanDemoRaiseTransitions;
   status += " position=" + GetPosition();
  }
  if (localPlayer)
   MLADSLeanSettings.Status = status;
  if (now >= m_MLADSLeanNextReport || (localPlayer && target != m_MLADSLeanLastTarget))
  {
   m_MLADSLeanNextReport = now + 2000;
   m_MLADSLeanLastTarget = target;
   Print("[MLADSLEAN10] demo=" + m_MLADSLeanDemo + " " + status + " mosin=" + mosin + " custom=" + MLADSLeanSettings.Enabled + " demo_native_controls=" + m_MLADSLeanDemoNativeBound);
  }
 }
 // Read-only measurements for in-game calibration, on F9 only.
 void MLADSLeanReportJoints()
 {
  if (GetGame().IsMultiplayer() || (GetGame().GetPlayer() != this && !m_MLADSLeanDemo))
   return;
  HumanMovementState measuredState = new HumanMovementState();
  GetMovementState(measuredState);
  Print("[MLADSLEAN10] demo=" + m_MLADSLeanDemo + " measured_native_lean=" + measuredState.m_fLeaning + " custom_amount=" + m_MLADSLeanAmount);
  int headIndex = GetBoneIndexByName("Head");
  int chestIndex = GetBoneIndexByName("Spine3");
  if (headIndex >= 0 && chestIndex >= 0)
  {
   vector head = GetBonePositionMS(headIndex);
   vector chest = GetBonePositionMS(chestIndex);
   if (!m_MLADSLeanDemo && Math.AbsFloat(m_MLADSLeanAmount) < 0.02 && measuredState.m_iMovement == 0 && (measuredState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || measuredState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT))
   {
    m_MLADSLeanNeutralHeadX = head[0];
    m_MLADSLeanNeutralChestX = chest[0];
    m_MLADSLeanNeutralMeasured = true;
   }
   Print("[MLADSLEAN10] demo=" + m_MLADSLeanDemo + " head_ms=" + head + " chest_ms=" + chest + " neutral_measured=" + m_MLADSLeanNeutralMeasured);
   if (m_MLADSLeanNeutralMeasured)
    Print("[MLADSLEAN10] exposure head_dx_m=" + (head[0] - m_MLADSLeanNeutralHeadX) + " chest_dx_m=" + (chest[0] - m_MLADSLeanNeutralChestX));
  }
  EntityAI held = GetHumanInventory().GetEntityInHands();
  if (held)
   Print("[MLADSLEAN10] demo=" + m_MLADSLeanDemo + " weapon_orientation_ws=" + held.GetOrientation());
  MLADSLeanMeasureChain("RightUpLeg", "RightLeg", "RightFoot", "right_leg");
  MLADSLeanMeasureChain("LeftUpLeg", "LeftLeg", "LeftFoot", "left_leg");
  MLADSLeanMeasureChain("RightArm", "RightForeArm", "RightHand", "right_elbow");
 }
 protected void MLADSLeanMeasureChain(string first, string middle, string last, string label)
 {
  int ai = GetBoneIndexByName(first);
  int bi = GetBoneIndexByName(middle);
  int ci = GetBoneIndexByName(last);
  if (ai < 0 || bi < 0 || ci < 0)
   return;
  vector a = GetBonePositionMS(ai);
  vector b = GetBonePositionMS(bi);
  vector c = GetBonePositionMS(ci);
  vector u = a - b;
  vector v = c - b;
  float denominator = u.Length() * v.Length();
  if (denominator < 0.000001)
   return;
  float angle = Math.Acos(Math.Clamp(vector.Dot(u, v) / denominator, -1, 1)) * Math.RAD2DEG;
  Print("[MLADSLEAN10] demo=" + m_MLADSLeanDemo + " joints=" + label + " interior_deg=" + angle + " first_ms=" + a + " middle_ms=" + b + " last_ms=" + c);
 }
};
