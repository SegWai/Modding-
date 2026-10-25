// Offline Mosin lean test. Player and designated demo use the same graph/pose.
class MLADSLeanSettings
{
 static bool Enabled = true;
 static bool Inspection = false;
 static bool HeadCorrection = true;
 static bool WeaponShoulderOffset = true;
 static bool HasGraph = false;
 static string Status = "Waiting for graph validation";
 static PlayerBase DemoActor;
 static ref ScriptInvoker DemoKilled = new ScriptInvoker();
 // Last moving ADS gait of the selected player; start at walk until measured.
 static int DemoGait = 1;
};
modded class PlayerBase
{
 protected int m_MLADSLeanWeaponShiftVar = -1;
 protected bool m_MLADSLeanWeaponShiftBound;
 protected int m_MLADSLeanNextShoulderSample;
 protected float m_MLADSLeanShoulderStableTime;
 protected bool m_MLADSLeanShoulderLastEnabled;
 protected float m_MLADSLeanShoulderLastSign;
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
 protected float m_MLADSLeanDemoWarmup;
 protected bool m_MLADSLeanDemoGraphNeedsReset;
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
  m_MLADSLeanDemoWarmup = 0;
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
  Print("[MLADSLEAN27] demo_started center=" + m_MLADSLeanDemoCenter + " half_span_m=2 native_locomotion=true");
 }
 void MLADSLeanToggleDemoPause()
 {
  m_MLADSLeanDemoPaused = !m_MLADSLeanDemoPaused;
  Print("[MLADSLEAN27] demo_paused=" + m_MLADSLeanDemoPaused);
 }
 void MLADSLeanStopDemo()
 {
  if (!m_MLADSLeanDemo)
   return;
  m_MLADSLeanDemo = false;
  m_MLADSLeanDemoGraphNeedsReset = true;
  m_MLADSLeanDemoWarmup = 0;
  m_MLADSLeanDemoReady = false;
  HumanInputController input = GetInputController();
  if (input)
  {
   input.OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
   input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
   input.OverrideRaise(HumanInputControllerOverrideType.DISABLED, false);
  }
  // The demo uses a private graph input, not a native player stance lock.
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
   m_MLADSLeanDemoWarmup = 0;
   m_MLADSLeanDemoReady = false;
   StartCommand_Move();
  }
  vector offset = GetPosition() - m_MLADSLeanDemoCenter;
  float lateral = vector.Dot(offset, m_MLADSLeanDemoRight);
  float oldSign = m_MLADSLeanDemoSign;
  if (m_MLADSLeanDemoSign < 0 && lateral <= -2)
   m_MLADSLeanDemoSign = 1;
  else if (m_MLADSLeanDemoSign > 0 && lateral >= 2)
   m_MLADSLeanDemoSign = -1;
  if (oldSign != m_MLADSLeanDemoSign)
   Print("[MLADSLEAN27] demo_reverse lateral_m=" + lateral + " direction=" + m_MLADSLeanDemoSign);
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
  // Native player raise input is not used to drive this demo.
 }
 override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
 {
  // Input overrides are set before native processing, only on the designated NPC.
  MLADSLeanRangeSampleMotion();
  MLADSLeanUpdateDemoInput(pDt);
  super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
  // Stop may be requested outside CommandHandler; clear graph state here only.
  if (m_MLADSLeanDemoGraphNeedsReset && m_MLADSLeanBound && m_MLADSLeanDemoNativeBound)
  {
   AnimSetFloat(m_MLADSLeanCanaryVar, 0.731);
   AnimSetFloat(m_MLADSLeanGateVar, 0);
   AnimSetFloat(m_MLADSLeanAmountVar, 0);
   m_MLADSLeanDemoGraphNeedsReset = false;
  }
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
   // Reuse the registered TestFloat (0..1), unused by the normal native graph.
   m_MLADSLeanWeaponShiftVar = GetAnimInterface().BindVariableFloat("TestFloat");
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftVar >= 0;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanGateVar;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanCanaryVar;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanAmountVar;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanNativeLeanVar;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanNativeMoveVar;
   if (localPlayer)
    MLADSLeanSettings.HasGraph = m_MLADSLeanBound;
   Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " bind_valid=" + m_MLADSLeanBound + " gate=" + m_MLADSLeanGateVar + " amount=" + m_MLADSLeanAmountVar + " canary=" + m_MLADSLeanCanaryVar + " nativeLean=" + m_MLADSLeanNativeLeanVar + " nativeMove=" + m_MLADSLeanNativeMoveVar);
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
  bool mosin = held && (held.IsKindOf("Mosin9130") || held.IsKindOf("AK74"));
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
  // Player inputs and camera ADS are not a controller for an offline dummy.
  // The demo has explicit raised/ADS graph routing via its registered canary.
  // Keep native player telemetry separate from requested animation state.
  bool demoControllerActive = false;
  if (m_MLADSLeanDemo)
  {
   demoControllerActive = m_MLADSLeanBound && m_MLADSLeanDemoNativeBound && mosin;
   demoControllerActive = demoControllerActive && IsAlive() && !IsUnconscious();
   demoControllerActive = demoControllerActive && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE;
   if (demoControllerActive)
    m_MLADSLeanDemoWarmup += Math.Clamp(pDt, 0, 0.25);
   else
    m_MLADSLeanDemoWarmup = 0;
   bool previouslyReady = m_MLADSLeanDemoReady;
   m_MLADSLeanDemoReady = demoControllerActive && m_MLADSLeanDemoWarmup >= 0.4;
   if (m_MLADSLeanDemoReady && !previouslyReady)
    Print("[MLADSLEAN27] demo_graph_warmup_complete patrol_start_allowed");
   if (raised != m_MLADSLeanDemoWasRaised)
   {
    m_MLADSLeanDemoRaiseTransitions++;
    m_MLADSLeanDemoWasRaised = raised;
   }
   // These are requested demo animation states, not native player ADS claims.
   raised = demoControllerActive;
   ready = m_MLADSLeanDemoReady;
   aiming = m_MLADSLeanDemoReady;
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
  // F5 comparison affects the same pre-weapon-IK pose on both actors.
  if (m_MLADSLeanBound && m_MLADSLeanWeaponShiftBound)
  {
   float shoulderShiftScale = 0;
   if (MLADSLeanSettings.WeaponShoulderOffset)
    shoulderShiftScale = 1;
   AnimSetFloat(m_MLADSLeanWeaponShiftVar, shoulderShiftScale);
  }
  // All graph writes stay inside CommandHandler, after native processing.
  if (m_MLADSLeanBound)
  {
   AnimSetFloat(m_MLADSLeanGateVar, m_MLADSLeanGate);
   AnimSetFloat(m_MLADSLeanAmountVar, m_MLADSLeanAmount);
  }
  if (m_MLADSLeanDemo && m_MLADSLeanDemoNativeBound)
  {
   // Reuse the already registered canary: 0.731=normal actor, 1=demo.
   float demoGraphValue = 0.731;
   if (demoControllerActive)
    demoGraphValue = 1;
   AnimSetFloat(m_MLADSLeanCanaryVar, demoGraphValue);
   AnimSetBool(m_MLADSLeanDemoADS, m_MLADSLeanDemoReady);
   AnimSetBool(m_MLADSLeanDemoRaised, raised);
   if (m_MLADSLeanDemoReady)
   {
    // Aim bit 0 and both hand chains; shared graph routing holds them active.
    AnimSetInt(m_MLADSLeanDemoArmIK, 7);
    AnimSetFloat(m_MLADSLeanNativeLeanVar, m_MLADSLeanDemoAmount);
    AnimSetFloat(m_MLADSLeanDemoAim, 0);
    AnimSetFloat(m_MLADSLeanDemoAimIK, 0);
    AnimSetFloat(m_MLADSLeanDemoAimUD, 0);
   }
  }
  // HumanCommandWeapons.SetADS controls the native head tilt to optics.
  // Native player HandleADS may enable it in super; apply this afterward.
  bool suppressHeadTilt = MLADSLeanSettings.HeadCorrection && MLADSLeanSettings.Enabled;
  suppressHeadTilt = suppressHeadTilt && m_MLADSLeanBound && m_MLADSLeanGate > 0.01;
  suppressHeadTilt = suppressHeadTilt && Math.AbsFloat(m_MLADSLeanAmount) > 0.01;
  bool requestedHeadADS = nativeADS;
  if (m_MLADSLeanDemo)
   requestedHeadADS = m_MLADSLeanDemoReady;
  HumanCommandWeapons weapons = GetCommandModifier_Weapons();
  if (weapons)
   weapons.SetADS(requestedHeadADS && !suppressHeadTilt);
  // Read-only, matched-direction sampling. Binding validity is not graph validity.
  bool shoulderEnabled = MLADSLeanSettings.WeaponShoulderOffset;
  float shoulderSign = 0;
  if (m_MLADSLeanAmount > 0.98)
   shoulderSign = 1;
  else if (m_MLADSLeanAmount < -0.98)
   shoulderSign = -1;
  bool stableShoulderSample = m_MLADSLeanGate > 0.98 && state.m_iMovement > 0;
  stableShoulderSample = stableShoulderSample && shoulderSign != 0;
  if (!stableShoulderSample || shoulderEnabled != m_MLADSLeanShoulderLastEnabled || shoulderSign != m_MLADSLeanShoulderLastSign)
   m_MLADSLeanShoulderStableTime = 0;
  else
   m_MLADSLeanShoulderStableTime += pDt;
  m_MLADSLeanShoulderLastEnabled = shoulderEnabled;
  m_MLADSLeanShoulderLastSign = shoulderSign;
  if (m_MLADSLeanShoulderStableTime > 0.35 && now >= m_MLADSLeanNextShoulderSample)
  {
   m_MLADSLeanNextShoulderSample = now + 1000;
   MLADSLeanReportShoulderPose(state.m_iMovement);
  }
  // Keep each diagnostic expression small for the Enforce compiler.
  string status = "bindings=" + m_MLADSLeanBound;
  status += " gate=" + m_MLADSLeanGate;
  status += " lean=" + m_MLADSLeanAmount;
  status += " ADS_requested=" + aiming;
  status += " native_ADS=" + nativeADS;
  status += " head_tilt_suppressed=" + suppressHeadTilt;
  status += " shoulder_offset=" + MLADSLeanSettings.WeaponShoulderOffset;
  status += " shoulder_control=" + m_MLADSLeanWeaponShiftBound;
  // bindings= records binding success only; consult RPT for compilation errors.
  status += " native_raised=" + IsRaised();
  status += " raise_complete=" + IsWeaponRaiseCompleted();
  status += " moving=" + state.m_iMovement;
  status += " stance=" + state.m_iStanceIdx;
  if (m_MLADSLeanDemo)
  {
   status += " requested_gait=" + MLADSLeanSettings.DemoGait;
   status += " demo_graph_active=" + demoControllerActive;
   status += " graph_warmup_s=" + m_MLADSLeanDemoWarmup;
   status += " patrol_ready=" + m_MLADSLeanDemoReady;
   HumanInputController demoInput = GetInputController();
   if (demoInput)
    status += " native_raise_input=" + demoInput.IsWeaponRaised();
   HumanCommandMove demoMove = GetCommand_Move();
   if (demoMove)
    status += " changing_stance=" + demoMove.IsChangingStance();
   status += " raise_transitions=" + m_MLADSLeanDemoRaiseTransitions;
   status += " position=" + GetPosition();
  }
  if (localPlayer)
   MLADSLeanSettings.Status = status;
  if (now >= m_MLADSLeanNextReport || (localPlayer && target != m_MLADSLeanLastTarget))
  {
   m_MLADSLeanNextReport = now + 2000;
   m_MLADSLeanLastTarget = target;
   Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " " + status + " supported_rifle=" + mosin + " custom=" + MLADSLeanSettings.Enabled + " demo_native_controls=" + m_MLADSLeanDemoNativeBound);
  }
 }
 // These are observed transforms, not a claim that the graph compiled.
 protected void MLADSLeanReportShoulderPose(int gait)
 {
  int chestIndex = GetBoneIndexByName("Spine3");
  int rightIndex = GetBoneIndexByName("RightHand");
  int leftIndex = GetBoneIndexByName("LeftHand");
  EntityAI held = GetHumanInventory().GetEntityInHands();
  if (chestIndex < 0 || rightIndex < 0 || leftIndex < 0 || !held)
   return;
  vector chest = GetBonePositionMS(chestIndex);
  vector right = GetBonePositionMS(rightIndex);
  vector left = GetBonePositionMS(leftIndex);
  vector weapon = WorldToModel(held.GetPosition());
  string sample = "[MLADSLEAN27] shoulder_observed demo=" + m_MLADSLeanDemo;
  sample += " enabled=" + MLADSLeanSettings.WeaponShoulderOffset;
  sample += " bound=" + m_MLADSLeanWeaponShiftBound;
  sample += " lean=" + m_MLADSLeanAmount;
  sample += " gait=" + gait;
  sample += " chest_ms=" + chest;
  sample += " right_hand_ms=" + right;
  sample += " left_hand_ms=" + left;
  sample += " weapon_ms=" + weapon;
  float weaponChestX = weapon[0] - chest[0];
  sample += " weapon_chest_x_m=" + weaponChestX;
  Print(sample);
 }
 // Read-only measurements for in-game calibration, on F9 only.
 void MLADSLeanReportJoints()
 {
  if (GetGame().IsMultiplayer() || (GetGame().GetPlayer() != this && !m_MLADSLeanDemo))
   return;
  HumanMovementState measuredState = new HumanMovementState();
  GetMovementState(measuredState);
  Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " measured_native_lean=" + measuredState.m_fLeaning + " custom_amount=" + m_MLADSLeanAmount);
  int headIndex = GetBoneIndexByName("Head");
  int chestIndex = GetBoneIndexByName("Spine3");
  if (headIndex >= 0 && chestIndex >= 0)
  {
   vector headBasis[4];
   GetBoneTransformMS(headIndex, headBasis);
   Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " head_basis_x_ms=" + headBasis[0]);
   Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " head_basis_y_ms=" + headBasis[1]);
   Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " head_basis_z_ms=" + headBasis[2]);
   vector head = GetBonePositionMS(headIndex);
   vector chest = GetBonePositionMS(chestIndex);
   if (!m_MLADSLeanDemo && Math.AbsFloat(m_MLADSLeanAmount) < 0.02 && measuredState.m_iMovement == 0 && (measuredState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || measuredState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT))
   {
    m_MLADSLeanNeutralHeadX = head[0];
    m_MLADSLeanNeutralChestX = chest[0];
    m_MLADSLeanNeutralMeasured = true;
   }
   Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " head_ms=" + head + " chest_ms=" + chest + " neutral_measured=" + m_MLADSLeanNeutralMeasured);
   if (m_MLADSLeanNeutralMeasured)
    Print("[MLADSLEAN27] exposure head_dx_m=" + (head[0] - m_MLADSLeanNeutralHeadX) + " chest_dx_m=" + (chest[0] - m_MLADSLeanNeutralChestX));
  }
  EntityAI held = GetHumanInventory().GetEntityInHands();
  if (held)
  {
   Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " weapon_orientation_ws=" + held.GetOrientation());
   vector weaponPositionMS = WorldToModel(held.GetPosition());
   Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " weapon_position_ms=" + weaponPositionMS);
  }
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
  Print("[MLADSLEAN27] demo=" + m_MLADSLeanDemo + " joints=" + label + " interior_deg=" + angle + " first_ms=" + a + " middle_ms=" + b + " last_ms=" + c);
 }

 // Range methods share this same PlayerBase layer; no upward patch calls.

 protected bool m_MLADSLeanRangeTarget;
 protected EntityAI m_MLADSLeanRangeRifle;
 protected bool m_MLADSLeanRangeRagdoll;
 protected bool m_MLADSLeanRangeImpulseApplied;
 protected vector m_MLADSLeanRangeLastPosition;
 protected vector m_MLADSLeanRangeVelocity;
 protected vector m_MLADSLeanRangeDeathVelocity;
 protected int m_MLADSLeanRangeLastSample;
 protected bool m_MLADSLeanRangeMotionValid;

 void MLADSLeanEnableRangeTarget()
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() == this)
   return;
  m_MLADSLeanRangeTarget = true;
  m_MLADSLeanRangeRifle = GetHumanInventory().GetEntityInHands();
  m_MLADSLeanRangeLastPosition = GetPosition();
  m_MLADSLeanRangeLastSample = GetGame().GetTime();
  PhysicsSetRagdoll(false);
 }
 void MLADSLeanRangeSampleMotion()
 {
  if (!m_MLADSLeanRangeTarget || GetGame().IsMultiplayer() || !IsAlive())
   return;
  int now = GetGame().GetTime();
  int elapsed = now - m_MLADSLeanRangeLastSample;
  if (elapsed < 80)
   return;
  // Enforce supports vector * scalar; do not divide a vector by a scalar.
  float elapsedMilliseconds = elapsed;
  float inverseSeconds = 1000.0 / elapsedMilliseconds;
  vector displacement = GetPosition() - m_MLADSLeanRangeLastPosition;
  vector velocity = displacement * inverseSeconds;
  m_MLADSLeanRangeMotionValid = elapsed <= 200 && velocity.Length() <= 8;
  if (m_MLADSLeanRangeMotionValid)
   m_MLADSLeanRangeVelocity = velocity;
  m_MLADSLeanRangeLastPosition = GetPosition();
  m_MLADSLeanRangeLastSample = now;
 }
 override void EEKilled(Object killer)
 {
  bool rangeDeath = m_MLADSLeanRangeTarget && !GetGame().IsMultiplayer();
  if (rangeDeath)
  {
   // Capture before native death can zero the movement controller.
   m_MLADSLeanRangeDeathVelocity = GetVelocity(this);
   if (m_MLADSLeanRangeMotionValid && GetGame().GetTime() - m_MLADSLeanRangeLastSample <= 200)
    m_MLADSLeanRangeDeathVelocity = m_MLADSLeanRangeVelocity;
   if (m_MLADSLeanRangeDeathVelocity.Length() > 8)
    m_MLADSLeanRangeDeathVelocity = "0 0 0";
  }
  super.EEKilled(killer);
  if (!rangeDeath)
   return;
  MLADSLeanStopDemo();
  DisableSimulation(false);
  PhysicsSetRagdoll(true);
  m_MLADSLeanRangeRagdoll = PhysicsIsRagdoll();
  if (m_MLADSLeanRangeRagdoll)
   MLADSLeanRangeTransferMomentum();
  else
   GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(MLADSLeanRangeRetryRagdoll, 50, false);
  Print("[MLADSLEAN27] target_killed ragdoll=" + m_MLADSLeanRangeRagdoll);
  MLADSLeanSettings.DemoKilled.Invoke(this);
 }
 void MLADSLeanRangeRetryRagdoll()
 {
  if (!m_MLADSLeanRangeTarget || GetGame().IsMultiplayer() || IsAlive())
   return;
  PhysicsSetRagdoll(true);
  m_MLADSLeanRangeRagdoll = PhysicsIsRagdoll();
  if (m_MLADSLeanRangeRagdoll)
   MLADSLeanRangeTransferMomentum();
  Print("[MLADSLEAN27] target_ragdoll_retry active=" + m_MLADSLeanRangeRagdoll);
 }
 protected void MLADSLeanRangeTransferMomentum()
 {
  if (m_MLADSLeanRangeImpulseApplied || !PhysicsIsRagdoll())
   return;
  m_MLADSLeanRangeImpulseApplied = true;
  float mass = dBodyGetMass(this);
  if (mass <= 0)
   return;
  vector delta = m_MLADSLeanRangeDeathVelocity - GetVelocity(this);
  // Preserve gravity/settling: transfer horizontal travel, never an upward kick.
  delta[1] = 0;
  float speed = delta.Length();
  if (speed > 8)
   delta = delta * (8 / speed);
  dBodyActive(this, ActiveState.ACTIVE);
  dBodyApplyImpulse(this, delta * mass);
  Print("[MLADSLEAN27] target_ragdoll_momentum velocity=" + m_MLADSLeanRangeDeathVelocity);
 }
 override bool HandleDeath(int pCurrentCommandID)
 {
  if (m_MLADSLeanRangeTarget && m_MLADSLeanRangeRagdoll && !GetGame().IsMultiplayer() && !IsAlive())
   return true;
  // Fall back to native death if articulated physics fails to activate.
  return super.HandleDeath(pCurrentCommandID);
 }
 void MLADSLeanRangeCleanup()
 {
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(MLADSLeanRangeRetryRagdoll);
  // Native death may drop the rifle outside the corpse hierarchy.
  // Clean up ground drops, but preserve any rifle the player picked up.
  if (m_MLADSLeanRangeRifle && !m_MLADSLeanRangeRifle.GetHierarchyParent())
   GetGame().ObjectDelete(m_MLADSLeanRangeRifle);
  m_MLADSLeanRangeRifle = null;
 }

};
