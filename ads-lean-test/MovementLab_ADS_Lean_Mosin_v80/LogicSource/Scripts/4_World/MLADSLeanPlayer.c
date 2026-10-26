// Offline Mosin lean test. Player and designated demo use the same graph/pose.
class MLADSLeanSettings
{
 static bool DistanceNativeReference = false;
 static bool Enabled = true;
 static bool Inspection = true; // Custom raised pose in both views, including non-ADS.
 static bool HeadCorrection = true;
 static bool WeaponShoulderOffset = true;
 static bool HasGraph = false;
 static bool PostPoseSupportGrip = true;
 static float FirstPersonRoll;
 static string FirstPersonRollCamera = "none";
 static string Status = "Waiting for graph validation";
 static PlayerBase DemoActor;
 static ref ScriptInvoker DemoKilled = new ScriptInvoker();
 // Last moving ADS gait of the selected player; start at walk until measured.
 static int DemoGait = 1;
};
modded class PlayerBase
{
 protected int m_ML50ReachVar = -1;
 protected int m_ML71SupportVar = -1;
 protected bool m_ML71SupportBound;
 protected float m_ML71SupportBlend = 1;
 protected bool m_ML50ReachBound;
 protected float m_ML50ReachTrim;
 protected float m_ML50ReachStable;
 protected bool m_ML69ReachHeldForLook;
 protected float m_ML50ObservedHeadX;
 protected float m_ML55NeutralHeadX = 0.118624;
 protected int m_MLADSLeanMoveBlendVar = -1;
 protected bool m_MLADSLeanMoveBlendBound;
 protected float m_MLADSLeanMoveBlend;
 protected float m_MLADSLeanLeanRequested;
 protected int m_MLADSLeanLastVisualGait = -1;
 protected int m_MLADSLeanLastVisualLeanSign;
 protected int m_MLADSLeanHeightVar = -1;
 protected bool m_MLADSLeanHeightBound;
 protected float m_MLADSLeanStandingHeadY;
 protected float m_MLADSLeanCurrentHeadY;
 protected float m_MLADSLeanHeightLift;
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
 protected float m_ML56GatePhase;
 protected int m_ML56LowSmoothVar = -1;
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
  Print("[MLADSLEAN80] demo_started center=" + m_MLADSLeanDemoCenter + " half_span_m=2 native_locomotion=true");
 }
 void MLADSLeanToggleDemoPause()
 {
  m_MLADSLeanDemoPaused = !m_MLADSLeanDemoPaused;
  Print("[MLADSLEAN80] demo_paused=" + m_MLADSLeanDemoPaused);
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
   Print("[MLADSLEAN80] demo_reverse lateral_m=" + lateral + " direction=" + m_MLADSLeanDemoSign);
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
  MLADSLeanCalibrateStandingHeight();
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
   m_ML56LowSmoothVar = GetAnimInterface().BindVariableFloat("MLADSLeanSmoothLow");
   m_MLADSLeanGateVar = GetAnimInterface().BindVariableFloat("MLADSLeanGate");
   m_MLADSLeanCanaryVar = GetAnimInterface().BindVariableFloat("MLADSLeanCanary");
   m_MLADSLeanAmountVar = GetAnimInterface().BindVariableFloat("MLADSLeanAmount");
   m_MLADSLeanNativeLeanVar = GetAnimInterface().BindVariableFloat("Lean");
   m_MLADSLeanNativeMoveVar = GetAnimInterface().BindVariableFloat("MovementSpeed");
   // Valid zero is allowed; all five float bindings must be distinct.
   m_MLADSLeanBound = m_MLADSLeanGateVar >= 0 && m_MLADSLeanCanaryVar >= 0 && m_MLADSLeanAmountVar >= 0 && m_MLADSLeanNativeLeanVar >= 0 && m_MLADSLeanNativeMoveVar >= 0 && m_MLADSLeanGateVar != m_MLADSLeanCanaryVar && m_MLADSLeanGateVar != m_MLADSLeanAmountVar && m_MLADSLeanGateVar != m_MLADSLeanNativeLeanVar && m_MLADSLeanGateVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanCanaryVar != m_MLADSLeanAmountVar && m_MLADSLeanCanaryVar != m_MLADSLeanNativeLeanVar && m_MLADSLeanCanaryVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanAmountVar != m_MLADSLeanNativeLeanVar && m_MLADSLeanAmountVar != m_MLADSLeanNativeMoveVar && m_MLADSLeanNativeLeanVar != m_MLADSLeanNativeMoveVar;
   // Dedicated default-on control; do not depend on native TestFloat.
   m_MLADSLeanWeaponShiftVar = GetAnimInterface().BindVariableFloat("MLADSLeanWeaponShift");
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftVar >= 0;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanGateVar;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanCanaryVar;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanAmountVar;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanNativeLeanVar;
   m_MLADSLeanWeaponShiftBound = m_MLADSLeanWeaponShiftBound && m_MLADSLeanWeaponShiftVar != m_MLADSLeanNativeMoveVar;
   m_MLADSLeanHeightVar = GetAnimInterface().BindVariableFloat("MLADSLeanHeightLift");
   m_MLADSLeanHeightBound = m_MLADSLeanHeightVar >= 0;
   m_MLADSLeanHeightBound = m_MLADSLeanHeightBound && m_MLADSLeanHeightVar != m_MLADSLeanGateVar;
   m_MLADSLeanHeightBound = m_MLADSLeanHeightBound && m_MLADSLeanHeightVar != m_MLADSLeanCanaryVar;
   m_MLADSLeanHeightBound = m_MLADSLeanHeightBound && m_MLADSLeanHeightVar != m_MLADSLeanAmountVar;
   m_MLADSLeanHeightBound = m_MLADSLeanHeightBound && m_MLADSLeanHeightVar != m_MLADSLeanNativeLeanVar;
   m_MLADSLeanHeightBound = m_MLADSLeanHeightBound && m_MLADSLeanHeightVar != m_MLADSLeanNativeMoveVar;
   m_MLADSLeanHeightBound = m_MLADSLeanHeightBound && m_MLADSLeanHeightVar != m_MLADSLeanWeaponShiftVar;
   m_MLADSLeanMoveBlendVar = GetAnimInterface().BindVariableFloat("MLADSLeanMoveBlend");
   m_MLADSLeanMoveBlendBound = m_MLADSLeanMoveBlendVar >= 0;
   m_MLADSLeanMoveBlendBound = m_MLADSLeanMoveBlendBound && m_MLADSLeanMoveBlendVar != m_MLADSLeanGateVar;
   m_MLADSLeanMoveBlendBound = m_MLADSLeanMoveBlendBound && m_MLADSLeanMoveBlendVar != m_MLADSLeanCanaryVar;
   m_MLADSLeanMoveBlendBound = m_MLADSLeanMoveBlendBound && m_MLADSLeanMoveBlendVar != m_MLADSLeanAmountVar;
   m_MLADSLeanMoveBlendBound = m_MLADSLeanMoveBlendBound && m_MLADSLeanMoveBlendVar != m_MLADSLeanNativeLeanVar;
   m_MLADSLeanMoveBlendBound = m_MLADSLeanMoveBlendBound && m_MLADSLeanMoveBlendVar != m_MLADSLeanNativeMoveVar;
   m_MLADSLeanMoveBlendBound = m_MLADSLeanMoveBlendBound && m_MLADSLeanMoveBlendVar != m_MLADSLeanWeaponShiftVar;
   m_MLADSLeanMoveBlendBound = m_MLADSLeanMoveBlendBound && m_MLADSLeanMoveBlendVar != m_MLADSLeanHeightVar;
   m_ML50ReachVar = GetAnimInterface().BindVariableFloat("MLADSLeanStandReachTrim");
   m_ML50ReachBound = m_ML50ReachVar >= 0;
   m_ML50ReachBound = m_ML50ReachBound && m_ML50ReachVar != m_MLADSLeanGateVar;
   m_ML50ReachBound = m_ML50ReachBound && m_ML50ReachVar != m_MLADSLeanCanaryVar;
   m_ML50ReachBound = m_ML50ReachBound && m_ML50ReachVar != m_MLADSLeanAmountVar;
   m_ML50ReachBound = m_ML50ReachBound && m_ML50ReachVar != m_MLADSLeanNativeLeanVar;
   m_ML50ReachBound = m_ML50ReachBound && m_ML50ReachVar != m_MLADSLeanNativeMoveVar;
   m_ML50ReachBound = m_ML50ReachBound && m_ML50ReachVar != m_MLADSLeanWeaponShiftVar;
   m_ML50ReachBound = m_ML50ReachBound && m_ML50ReachVar != m_MLADSLeanHeightVar;
   m_ML50ReachBound = m_ML50ReachBound && m_ML50ReachVar != m_MLADSLeanMoveBlendVar;
   bool lowSmoothValid = m_ML56LowSmoothVar >= 0;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_MLADSLeanGateVar;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_MLADSLeanCanaryVar;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_MLADSLeanAmountVar;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_MLADSLeanNativeLeanVar;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_MLADSLeanNativeMoveVar;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_MLADSLeanWeaponShiftVar;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_MLADSLeanHeightVar;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_MLADSLeanMoveBlendVar;
   lowSmoothValid = lowSmoothValid && m_ML56LowSmoothVar != m_ML50ReachVar;
   if (!lowSmoothValid)
    m_ML56LowSmoothVar = -1;
   m_ML71SupportVar = GetAnimInterface().BindVariableFloat("ML71SupportGrip");
   m_ML71SupportBound = m_ML71SupportVar >= 0;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_MLADSLeanGateVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_MLADSLeanCanaryVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_MLADSLeanAmountVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_MLADSLeanNativeLeanVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_MLADSLeanNativeMoveVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_MLADSLeanWeaponShiftVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_MLADSLeanHeightVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_MLADSLeanMoveBlendVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_ML50ReachVar;
   m_ML71SupportBound = m_ML71SupportBound && m_ML71SupportVar != m_ML56LowSmoothVar;
   if (localPlayer)
    MLADSLeanSettings.HasGraph = m_MLADSLeanBound;
   Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " bind_valid=" + m_MLADSLeanBound + " gate=" + m_MLADSLeanGateVar + " amount=" + m_MLADSLeanAmountVar + " canary=" + m_MLADSLeanCanaryVar + " nativeLean=" + m_MLADSLeanNativeLeanVar + " nativeMove=" + m_MLADSLeanNativeMoveVar);
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
  // Raised custom pose is camera-independent; ADS input remains native.
  string cameraName = "none";
  bool inspectionAllowed = MLADSLeanSettings.Inspection;
  string viewState = "npc_pose";
  if (localPlayer)
  {
   DayZPlayerCamera activeCamera = GetCurrentCamera();
   if (activeCamera)
    cameraName = activeCamera.GetCameraName();
   viewState = "lowered";
   if (raised)
    viewState = "raised_only";
   if (aiming)
    viewState = "ads_requested";
   if (cameraName == "DayZPlayerCameraIronsights" || cameraName == "DayZPlayerCameraOptics")
    viewState = "ads_camera";
  }
  // Match the player's actual native gait; never change the player's input.
  if (localPlayer && mosin && raised && (aiming || inspectionAllowed))
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
    Print("[MLADSLEAN80] demo_graph_warmup_complete patrol_start_allowed");
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
  bool target = actorReady && m_MLADSLeanBound && MLADSLeanSettings.Enabled && IsAlive() && !IsUnconscious() && mosin && supportedStance && state.m_iMovement <= 2 && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE && raised && (!m_MLADSLeanDemo || ready) && (aiming || inspectionAllowed);
  float targetValue = 0;
  if (target)
   targetValue = 1;
  // Blend throughout raising/lowering rather than waiting for raise completion.
  // Smoothstep gives zero velocity at both ends and identical left/right timing.
  float stepGate = Math.Clamp(pDt, 0, 0.05) / 0.08;
  if (m_ML56GatePhase < targetValue)
   m_ML56GatePhase = Math.Min(targetValue, m_ML56GatePhase + stepGate);
  else
   m_ML56GatePhase = Math.Max(targetValue, m_ML56GatePhase - stepGate);
  m_MLADSLeanGate = m_ML56GatePhase * m_ML56GatePhase * (3.0 - 2.0 * m_ML56GatePhase);
  m_MLADSLeanLeanRequested = Math.Clamp(state.m_fLeaning, -1, 1);
  if (m_MLADSLeanDemo)
   m_MLADSLeanLeanRequested = m_MLADSLeanDemoAmount;
  // Native movement state already interpolates the lean. Follow that value
  // directly instead of applying a second low-pass filter that delays both
  // neutral-to-lean and left-to-right reversals. Demo uses its existing ramp.
  m_MLADSLeanAmount = m_MLADSLeanLeanRequested;
  if (m_MLADSLeanBound && m_ML56LowSmoothVar >= 0)
  {
   float smoothLow = 0;
   if (mosin && supportedStance && MLADSLeanSettings.Enabled && IsAlive() && !IsUnconscious())
    smoothLow = 1;
   AnimSetFloat(m_ML56LowSmoothVar, smoothLow);
  }
  float movementRequest = 0;
  vector movementDirection;
  HumanInputController movementInput = GetInputController();
  if (movementInput)
   movementInput.GetMovement(movementRequest, movementDirection);
  // Some controller paths report no raw input while native gait is still active.
  if (movementRequest <= 0 && state.m_iMovement > 0)
   movementRequest = state.m_iMovement;
  float moveVisualTarget = Math.Clamp(movementRequest, 0, 1);
  float moveVisualStep = Math.Clamp(pDt, 0, 0.05) / 0.08;
  if (m_MLADSLeanMoveBlend < moveVisualTarget)
   m_MLADSLeanMoveBlend = Math.Min(moveVisualTarget, m_MLADSLeanMoveBlend + moveVisualStep);
  else
   m_MLADSLeanMoveBlend = Math.Max(moveVisualTarget, m_MLADSLeanMoveBlend - moveVisualStep);
  if (m_MLADSLeanBound && m_MLADSLeanMoveBlendBound)
   AnimSetFloat(m_MLADSLeanMoveBlendVar, m_MLADSLeanMoveBlend);
  int leanVisualSign = 0;
  if (m_MLADSLeanLeanRequested > 0.02)
   leanVisualSign = 1;
  else if (m_MLADSLeanLeanRequested < -0.02)
   leanVisualSign = -1;
  if (state.m_iMovement != m_MLADSLeanLastVisualGait || leanVisualSign != m_MLADSLeanLastVisualLeanSign)
  {
   m_MLADSLeanLastVisualGait = state.m_iMovement;
   m_MLADSLeanLastVisualLeanSign = leanVisualSign;
   string transition = "[MLADSLEAN80] visual_transition demo=" + m_MLADSLeanDemo;
   transition += " gait=" + state.m_iMovement;
   transition += " lean_requested=" + m_MLADSLeanLeanRequested;
   transition += " lean=" + m_MLADSLeanAmount;
   transition += " move_blend=" + m_MLADSLeanMoveBlend;
   transition += " gate=" + m_MLADSLeanGate;
   transition += " raise_complete=" + ready;
   transition += " camera=" + cameraName;
   Print(transition);
  }
  // F5 comparison affects the final solved arm pose on both actors.
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
  // Height correction is part of this shared actor graph, before native foot IK.
  bool heightStanding = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
  heightStanding = heightStanding || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool heightWalking = heightStanding && state.m_iMovement > 0 && state.m_iMovement <= 2;
  heightWalking = heightWalking && m_MLADSLeanGate > 0.98 && IsAlive() && !IsUnconscious();
  heightWalking = heightWalking && m_MLADSLeanStandingHeadY > 0;
  bool heightActive = heightWalking && Math.AbsFloat(m_MLADSLeanAmount) > 0.98;
  int heightHeadIndex = GetBoneIndexByName("Head");
  if (heightHeadIndex >= 0)
  {
   vector heightHead = GetBonePositionMS(heightHeadIndex);
   m_MLADSLeanCurrentHeadY = heightHead[1];
  }
  else
  {
   heightActive = false;
   heightWalking = false;
  }
  float heightStep = Math.Clamp(pDt, 0, 0.05);
  if (heightActive && m_MLADSLeanBound && m_MLADSLeanHeightBound)
  {
   float heightTarget = m_MLADSLeanStandingHeadY * 0.95;
   float heightError = heightTarget - m_MLADSLeanCurrentHeadY;
   // Slow enough to retain gait bob; rate-limit the pelvis adjustment.
   float heightGain = Math.Clamp(heightStep / 0.45, 0, 1);
   float heightChange = Math.Clamp(heightError * heightGain, -0.12 * heightStep, 0.12 * heightStep);
   m_MLADSLeanHeightLift = Math.Clamp(m_MLADSLeanHeightLift + heightChange, -0.06, 0.15);
  }
  else if (!heightWalking || !m_MLADSLeanBound || !m_MLADSLeanHeightBound)
  {
   float heightFade = Math.Clamp(heightStep / 0.18, 0, 1);
   m_MLADSLeanHeightLift = m_MLADSLeanHeightLift * (1.0 - heightFade);
  }
  if (m_MLADSLeanBound && m_MLADSLeanHeightBound)
   AnimSetFloat(m_MLADSLeanHeightVar, m_MLADSLeanHeightLift);
  // In-game comparison changes only the additional support solver. All graph
  // writes remain inside CommandHandler after native processing.
  if (m_MLADSLeanBound && m_ML71SupportBound)
  {
   float supportTarget = 0;
   if (MLADSLeanSettings.PostPoseSupportGrip)
    supportTarget = 1;
   float supportStep = Math.Clamp(pDt, 0, 0.05) / 0.18;
   if (m_ML71SupportBlend < supportTarget)
    m_ML71SupportBlend = Math.Min(supportTarget, m_ML71SupportBlend + supportStep);
   else
    m_ML71SupportBlend = Math.Max(supportTarget, m_ML71SupportBlend - supportStep);
   AnimSetFloat(m_ML71SupportVar, m_ML71SupportBlend);
  }
  ML50UpdateStandingReach(pDt, state);
  ML67ReadAimCoherence(pDt);
  if (m_MLADSLeanBound && m_ML50ReachBound)
   AnimSetFloat(m_ML50ReachVar, m_ML50ReachTrim);
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
  string status = "view=" + viewState;
  status += " camera=" + cameraName;
  status += " inspection_requested=" + MLADSLeanSettings.Inspection;
  status += " inspection_applied=" + inspectionAllowed;
  status += " bindings=" + m_MLADSLeanBound;
  status += " gate=" + m_MLADSLeanGate;
  bool reachActive = m_ML50ReachStable >= 0.2;
  status += " reach_active=" + reachActive;
  status += " reach_held_for_look=" + m_ML69ReachHeldForLook;
  status += " reach_bound=" + m_ML50ReachBound;
  status += " reach_head_x_m=" + m_ML50ObservedHeadX;
  status += " reach_trim_m=" + m_ML50ReachTrim;
  status += " lean=" + m_MLADSLeanAmount;
  status += " lean_requested=" + m_MLADSLeanLeanRequested;
  status += " move_blend=" + m_MLADSLeanMoveBlend;
  status += " move_blend_bound=" + m_MLADSLeanMoveBlendBound;
  status += " ADS_requested=" + aiming;
  status += " native_ADS=" + nativeADS;
  status += " head_tilt_suppressed=" + suppressHeadTilt;
  status += " shoulder_offset=" + MLADSLeanSettings.WeaponShoulderOffset;
  status += " shoulder_control=" + m_MLADSLeanWeaponShiftBound;
  status += " shoulder_id=" + m_MLADSLeanWeaponShiftVar;
  status += " height_bound=" + m_MLADSLeanHeightBound;
  status += " standing_head_y=" + m_MLADSLeanStandingHeadY;
  status += " current_head_y=" + m_MLADSLeanCurrentHeadY;
  status += " height_lift_m=" + m_MLADSLeanHeightLift;
  float observedHeightRatio = 0;
  if (m_MLADSLeanStandingHeadY > 0)
   observedHeightRatio = m_MLADSLeanCurrentHeadY / m_MLADSLeanStandingHeadY;
  status += " observed_head_height_ratio=" + observedHeightRatio;
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
   Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " " + status + " supported_rifle=" + mosin + " custom=" + MLADSLeanSettings.Enabled + " demo_native_controls=" + m_MLADSLeanDemoNativeBound);
  }
 }
 // Shared neutral-standing head-height reference; never rescale the mesh/actor.
 protected void MLADSLeanCalibrateStandingHeight()
 {
  if (m_MLADSLeanStandingHeadY > 0 || GetGame().IsMultiplayer())
   return;
  if (GetGame().GetPlayer() != this && !m_MLADSLeanDemo)
   return;
  if (!IsAlive() || IsUnconscious() || m_MLADSLeanGate > 0.01)
   return;
  HumanMovementState neutralHeightState = new HumanMovementState();
  GetMovementState(neutralHeightState);
  bool erectHeight = neutralHeightState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
  erectHeight = erectHeight || neutralHeightState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  if (!erectHeight || neutralHeightState.m_iMovement != 0 || Math.AbsFloat(neutralHeightState.m_fLeaning) > 0.02)
   return;
  int referenceIndex = GetBoneIndexByName("Head");
  if (referenceIndex < 0)
   return;
  vector referenceHead = GetBonePositionMS(referenceIndex);
  if (referenceHead[1] < 1.25 || referenceHead[1] > 2.1)
   return;
  m_MLADSLeanStandingHeadY = referenceHead[1];
  string referenceMessage = "[MLADSLEAN80] standing_height_reference demo=" + m_MLADSLeanDemo;
  referenceMessage += " head_y=" + m_MLADSLeanStandingHeadY;
  Print(referenceMessage);
 }
 // These are observed transforms, not a claim that the graph compiled.
 protected void MLADSLeanReportShoulderPose(int gait)
 {
  int chestIndex = GetBoneIndexByName("Spine3");
  int rightIndex = GetBoneIndexByName("RightHand_Dummy");
  int leftIndex = GetBoneIndexByName("LeftHand_Dummy");
  EntityAI held = GetHumanInventory().GetEntityInHands();
  if (chestIndex < 0 || !held)
   return;
  vector chest = GetBonePositionMS(chestIndex);
  vector right = "0 0 0";
  vector left = "0 0 0";
  if (rightIndex != -1)
   right = GetBonePositionMS(rightIndex);
  if (leftIndex != -1)
   left = GetBonePositionMS(leftIndex);
  vector weapon = WorldToModel(held.GetPosition());
  string sample = "[MLADSLEAN80] shoulder_observed demo=" + m_MLADSLeanDemo;
  sample += " enabled=" + MLADSLeanSettings.WeaponShoulderOffset;
  sample += " bound=" + m_MLADSLeanWeaponShiftBound;
  sample += " lean=" + m_MLADSLeanAmount;
  sample += " gait=" + gait;
  sample += " chest_ms=" + chest;
  sample += " right_hand_index=" + rightIndex;
  sample += " right_hand_ms=" + right;
  sample += " left_hand_index=" + leftIndex;
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
  Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " measured_native_lean=" + measuredState.m_fLeaning + " custom_amount=" + m_MLADSLeanAmount);
  int headIndex = GetBoneIndexByName("Head");
  int chestIndex = GetBoneIndexByName("Spine3");
  if (headIndex >= 0 && chestIndex >= 0)
  {
   vector headBasis[4];
   GetBoneTransformMS(headIndex, headBasis);
   Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " head_basis_x_ms=" + headBasis[0]);
   Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " head_basis_y_ms=" + headBasis[1]);
   Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " head_basis_z_ms=" + headBasis[2]);
   vector head = GetBonePositionMS(headIndex);
   vector chest = GetBonePositionMS(chestIndex);
   if (!m_MLADSLeanDemo && Math.AbsFloat(m_MLADSLeanAmount) < 0.02 && measuredState.m_iMovement == 0 && (measuredState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || measuredState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT))
   {
    m_MLADSLeanNeutralHeadX = head[0];
    m_MLADSLeanNeutralChestX = chest[0];
    m_MLADSLeanNeutralMeasured = true;
   }
   Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " head_ms=" + head + " chest_ms=" + chest + " neutral_measured=" + m_MLADSLeanNeutralMeasured);
   if (m_MLADSLeanNeutralMeasured)
    Print("[MLADSLEAN80] exposure head_dx_m=" + (head[0] - m_MLADSLeanNeutralHeadX) + " chest_dx_m=" + (chest[0] - m_MLADSLeanNeutralChestX));
  }
  EntityAI held = GetHumanInventory().GetEntityInHands();
  if (held)
  {
   Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " weapon_orientation_ws=" + held.GetOrientation());
   vector weaponPositionMS = WorldToModel(held.GetPosition());
   Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " weapon_position_ms=" + weaponPositionMS);
  }
  MLADSLeanCapturePose();
  MLADSLeanMeasureChain("RightUpLeg", "RightLeg", "RightFoot", "right_leg");
  MLADSLeanMeasureChain("LeftUpLeg", "LeftLeg", "LeftFoot", "left_leg");
  MLADSLeanMeasureChain("RightArm", "RightForeArm", "RightHand", "right_elbow");
 }
 // Shared player/NPC steady-standing idle correction. Only the small residual
 // X drift is trimmed; the authored body/leg solve does the actual repositioning.
 float ML55NeutralAimingHeadX()
 {
  return m_ML55NeutralHeadX;
 }

 // Read only native aim state. Head travel is calibrated while looking
 // forward/level; looking around must not trigger a second torso controller.
 protected bool ML69AimCentered()
 {
  HumanCommandWeapons reachAim = GetCommandModifier_Weapons();
  if (!reachAim)
   return false;
  if (Math.AbsFloat(reachAim.GetBaseAimingAngleLR()) > 5.0)
   return false;
  return Math.AbsFloat(reachAim.GetBaseAimingAngleUD()) <= 5.0;
 }

 protected void ML50UpdateStandingReach(float dt, HumanMovementState state)
 {
  float step = Math.Clamp(dt, 0, 0.05);
  bool centered = ML69AimCentered();
  m_ML69ReachHeldForLook = false;
  bool standing = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
  standing = standing || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool active = m_MLADSLeanBound && m_ML50ReachBound && standing;
  active = active && MLADSLeanSettings.Enabled && !MLADSLeanSettings.DistanceNativeReference;
  active = active && IsAlive() && !IsUnconscious();
  bool neutral = active && m_MLADSLeanGate > 0.98;
  neutral = neutral && Math.AbsFloat(m_MLADSLeanAmount) < 0.02;
  neutral = neutral && state.m_iMovement == 0 && m_MLADSLeanMoveBlend < 0.02;
  neutral = neutral && centered;
  if (neutral)
  {
   int neutralHead = GetBoneIndexByName("Head");
   if (neutralHead != -1)
   {
    vector neutralPosition = GetBonePositionMS(neutralHead);
    float neutralGain = step / (0.35 + step);
    m_ML55NeutralHeadX += (neutralPosition[0] - m_ML55NeutralHeadX) * neutralGain;
   }
  }
  active = active && m_MLADSLeanGate > 0.98 && Math.AbsFloat(m_MLADSLeanAmount) > 0.98;
  active = active && state.m_iMovement == 0 && m_MLADSLeanMoveBlend < 0.02;
  if (active && !centered)
  {
   // Keep the last settled trim. Do not chase head X as the shared upper
   // body yaws/pitches, and do not fade it (which would add more body motion).
   m_ML50ReachStable = 0;
   m_ML69ReachHeldForLook = true;
   return;
  }
  if (active)
  {
   m_ML50ReachStable += step;
   if (m_ML50ReachStable < 0.2)
    return;
   int head = GetBoneIndexByName("Head");
   if (head == -1)
    return;
   vector headPosition = GetBonePositionMS(head);
   m_ML50ObservedHeadX = headPosition[0];
   float targetX = m_ML55NeutralHeadX + 0.219;
   if (m_MLADSLeanAmount < 0)
    targetX = m_ML55NeutralHeadX - 0.42;
   float error = targetX - m_ML50ObservedHeadX;
   float gain = Math.Clamp(step / 0.25, 0, 1);
   m_ML50ReachTrim = Math.Clamp(m_ML50ReachTrim + error * gain, -0.02, 0.02);
  }
  else
  {
   m_ML50ReachStable = 0;
   m_ML50ReachTrim *= 1.0 - Math.Clamp(step / 0.18, 0, 1);
  }
 }

 // Standing exposure calibration: read-only model-space measurements.
 int ML49DistanceState()
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
   return 9;
  if (!IsRaised() || !IsWeaponRaiseCompleted())
   return 9;
  if (!ML69AimCentered())
   return 9;
  EntityAI measuredGun = GetHumanInventory().GetEntityInHands();
  if (!measuredGun || (!measuredGun.IsKindOf("AK74") && !measuredGun.IsKindOf("Mosin9130")))
   return 9;
  if (MLADSLeanSettings.DistanceNativeReference)
  {
   // A clean native-reference process must NOT have private graph bindings.
   if (m_MLADSLeanBound || m_MLADSLeanGate > 0.02 || MLADSLeanSettings.Enabled)
    return 9;
  }
  else if (!m_MLADSLeanBound || m_MLADSLeanGate < 0.98 || !MLADSLeanSettings.Enabled)
   return 9;
  HumanMovementState distanceState = new HumanMovementState();
  GetMovementState(distanceState);
  if (distanceState.m_iMovement != 0)
   return 9;
  if (distanceState.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT && distanceState.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_RAISEDERECT)
   return 9;
  float lean = distanceState.m_fLeaning;
  if (Math.AbsFloat(lean) < 0.02 && Math.AbsFloat(m_MLADSLeanAmount) < 0.02)
   return 0;
  if (lean < -0.98 && m_MLADSLeanAmount < -0.98)
   return -1;
  if (lean > 0.98 && m_MLADSLeanAmount > 0.98)
   return 1;
  return 9;
 }
 string ML49DistanceSetup()
 {
  EntityAI gun = GetHumanInventory().GetEntityInHands();
  if (!gun)
   return "none";
  string view = "raised";
  if (IsInIronsights())
   view = "ironsights";
  if (IsInOptics())
   view = "optics";
  return gun.GetType() + "_" + view;
 }
 bool ML49DistancePoints(out vector points[7])
 {
  array<string> names = {"Head", "Spine3", "Pelvis", "LeftFoot", "RightFoot", "EyeLeft", "EyeRight"};
  for (int i = 0; i < 7; i++)
  {
   int bone = GetBoneIndexByName(names[i]);
   if (bone == -1)
    return false;
   points[i] = GetBonePositionMS(bone);
  }
  return true;
 }
 void ML49DistanceFullPose()
 {
  if (ML49DistanceState() != 9)
   MLADSLeanCapturePose();
 }

 protected float m_ML67AimLogTime;
 protected int m_ML70GripLastSlot = -1;
 protected float m_ML70GripSlotStable;
 protected EntityAI m_ML67DiagnosticsWeapon;
 protected vector m_ML67GripLocalReference[3];
 protected vector m_ML68GripPrimaryReference[3];
 protected vector m_ML68PrimaryWeaponReference[3];
 protected bool m_ML67GripHasReference[3];

 // Readback only: never writes pose, weapon or camera state.
 protected void ML67ReadAimCoherence(float dt)
 {
  m_ML67AimLogTime += Math.Clamp(dt, 0, 0.05);
  if (m_ML67AimLogTime < 0.5 || m_MLADSLeanGate < 0.98)
   return;
  m_ML67AimLogTime = 0;
  Weapon_Base rifle = Weapon_Base.Cast(GetHumanInventory().GetEntityInHands());
  HumanCommandWeapons aimCommand = GetCommandModifier_Weapons();
  if (!rifle || !aimCommand || !IsAlive() || IsUnconscious())
   return;
  if (rifle != m_ML67DiagnosticsWeapon)
  {
   m_ML67DiagnosticsWeapon = rifle;
   m_ML70GripLastSlot = -1;
   m_ML70GripSlotStable = 0;
   for (int resetSlot = 0; resetSlot < 3; resetSlot++)
    m_ML67GripHasReference[resetSlot] = false;
  }
  int hand = GetBoneIndexByName("LeftHand");
  int primaryHand = GetBoneIndexByName("RightHand");
  if (hand == -1 || primaryHand == -1)
   return;
  vector handPosition = GetBonePositionMS(hand);
  vector handWeaponLocal = rifle.WorldToModel(ModelToWorld(handPosition));
  float aimPitch = aimCommand.GetBaseAimingAngleUD();
  float aimYaw = aimCommand.GetBaseAimingAngleLR();
  vector primaryPose[4];
  GetBoneTransformMS(primaryHand, primaryPose);
  vector supportInPrimary = handPosition.InvMultiply4(primaryPose);
  vector primaryInWeapon = rifle.WorldToModel(ModelToWorld(primaryPose[3]));
  int slot = 1;
  if (m_MLADSLeanAmount < -0.98)
   slot = 0;
  else if (m_MLADSLeanAmount > 0.98)
   slot = 2;
  else if (Math.AbsFloat(m_MLADSLeanAmount) > 0.02)
  {
   m_ML70GripLastSlot = -1;
   m_ML70GripSlotStable = 0;
   return;
  }
  if (slot != m_ML70GripLastSlot)
  {
   m_ML70GripLastSlot = slot;
   m_ML70GripSlotStable = 0;
  }
  else
   m_ML70GripSlotStable += 0.5;
  if (!m_ML67GripHasReference[slot] && m_ML70GripSlotStable >= 0.5)
  {
   m_ML67GripLocalReference[slot] = handWeaponLocal;
   m_ML68GripPrimaryReference[slot] = supportInPrimary;
   m_ML68PrimaryWeaponReference[slot] = primaryInWeapon;
   m_ML67GripHasReference[slot] = true;
  }
  float drift = -1;
  if (m_ML67GripHasReference[slot])
   drift = vector.Distance(handWeaponLocal, m_ML67GripLocalReference[slot]);
  float handToHandDrift = -1;
  float weaponAttachmentDrift = -1;
  if (m_ML67GripHasReference[slot])
  {
   handToHandDrift = vector.Distance(supportInPrimary, m_ML68GripPrimaryReference[slot]);
   weaponAttachmentDrift = vector.Distance(primaryInWeapon, m_ML68PrimaryWeaponReference[slot]);
  }
  vector sightPoint;
  vector sightDirection;
  rifle.GetCameraPoint(rifle.GetCurrentMuzzle(), sightPoint, sightDirection);
  vector pointMS = WorldToModel(rifle.ModelToWorld(sightPoint));
  vector directionMS = WorldToModel(rifle.ModelToWorld(sightPoint + sightDirection)) - pointMS;
  vector poseCamera[4];
  HumanItemAccessor aimAccessor = GetItemAccessor();
  bool poseCameraValid = aimAccessor.WeaponGetCameraPointMSTransform(rifle, sightPoint, sightDirection, poseCamera);
  float poseItemDifference = -1;
  if (poseCameraValid)
   poseItemDifference = vector.Distance(poseCamera[3], pointMS);
  float horizontal = Math.Sqrt(directionMS[0] * directionMS[0] + directionMS[2] * directionMS[2]);
  float borePitch = Math.Atan2(directionMS[1], horizontal) * Math.RAD2DEG;
  string readback = "[MLAIM80] demo=" + m_MLADSLeanDemo;
  readback += " sign_slot=" + slot;
  readback += " move_blend=" + m_MLADSLeanMoveBlend;
  readback += " native_pitch_deg=" + aimPitch;
  readback += " native_yaw_deg=" + aimYaw;
  readback += " bore_pitch_deg=" + borePitch;
  readback += " baseline=" + m_ML67GripHasReference[slot];
  readback += " post_pose_support=" + m_ML71SupportBlend;
  readback += " support_control_bound=" + m_ML71SupportBound;
  readback += " weapon_local_hand=" + handWeaponLocal;
  readback += " grip_drift_m=" + drift;
  readback += " hand_to_hand_drift_m=" + handToHandDrift;
  readback += " weapon_attachment_drift_m=" + weaponAttachmentDrift;
  readback += " pose_vs_world_item_m=" + poseItemDifference;
  Print(readback);
 }

 // Read-only camera weight, shared transition controls; no pose writes.
 float ML58RaisedViewWeight()
 {
  if (!MLADSLeanSettings.Enabled || !m_MLADSLeanBound || !IsAlive() || IsUnconscious())
   return 0;
  return Math.Clamp(m_MLADSLeanGate * Math.AbsFloat(m_MLADSLeanAmount), 0, 1);
 }

 // Camera-only readback. Never writes animation controls or player input.
 float MLADSLeanFirstPersonRollTarget(bool sightCamera)
 {
  if (!MLADSLeanSettings.Enabled || !m_MLADSLeanBound || !IsAlive() || IsUnconscious())
   return 0;
  if (!IsRaised() || m_MLADSLeanGate < 0.001)
   return 0;
  EntityAI rollWeapon = GetHumanInventory().GetEntityInHands();
  if (!rollWeapon || (!rollWeapon.IsKindOf("AK74") && !rollWeapon.IsKindOf("Mosin9130")))
   return 0;
  vector rollUp;
  // Left raised first-person view must follow rifle roll, not head roll.
  // Camera readback only: no weapon/bone/graph transform is changed.
  if (sightCamera || m_MLADSLeanAmount < 0)
  {
   vector weaponWorld[4];
   rollWeapon.GetTransform(weaponWorld);
   vector weaponBase = WorldToModel(weaponWorld[3]);
   rollUp = WorldToModel(weaponWorld[3] + weaponWorld[1]) - weaponBase;
  }
  else
  {
   // Native Head local +X points up (verified from captured Head->Face_Hub).
   int rollHead = GetBoneIndexByName("Head");
   if (rollHead == -1)
    return 0;
   vector rollHeadTM[4];
   GetBoneTransformMS(rollHead, rollHeadTM);
   rollUp = rollHeadTM[0];
  }
  if (rollUp.LengthSq() < 0.000001)
   return 0;
  float tilt = Math.Atan2(rollUp[0], rollUp[1]) * Math.RAD2DEG;
  float weight = Math.Clamp(m_MLADSLeanGate * Math.AbsFloat(m_MLADSLeanAmount), 0, 1);
  return Math.Clamp(tilt, -35, 35) * weight;
 }

 bool MLADSLeanLeftWalkCaptureReady()
 {
  if (!m_MLADSLeanDemo || !m_MLADSLeanDemoReady || !IsAlive())
   return false;
  if (m_MLADSLeanDemoSign >= 0 || m_MLADSLeanDemoPaused)
   return false;
  if (m_MLADSLeanGate < 0.98 || m_MLADSLeanAmount > -0.98 || m_MLADSLeanMoveBlend < 0.98)
   return false;
  HumanMovementState clipState = new HumanMovementState();
  GetMovementState(clipState);
  if (clipState.m_iMovement != 1)
   return false;
  return clipState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || clipState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
 }
 void MLADSLeanExportLeftWalkFrame(string session, int frame)
 {
  if (GetGame().IsMultiplayer() || !MLADSLeanLeftWalkCaptureReady())
   return;
  string marker = "[MLWALK80] FRAME session=" + session;
  marker += " frame=" + frame;
  marker += " time_ms=" + GetGame().GetTime();
  Print(marker);
  MLADSLeanCapturePose();
 }

 // Read-only native baseline required for the approved frame-15 left pose.
 bool MLADSLeanLeftStandingReferenceReady()
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() != this || !IsAlive() || IsUnconscious())
   return false;
  if (!IsRaised() || m_MLADSLeanGate < 0.98 || m_MLADSLeanAmount > -0.98 || m_MLADSLeanMoveBlend > 0.02)
   return false;
  HumanMovementState leftReferenceState = new HumanMovementState();
  GetMovementState(leftReferenceState);
  if (leftReferenceState.m_iMovement != 0)
   return false;
  return leftReferenceState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || leftReferenceState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
 }
 void MLADSLeanExportLeftStandingReference()
 {
  if (!MLADSLeanLeftStandingReferenceReady())
   return;
  Print("[MLPOSE80] STATIC_LEFT_FRAME15_REFERENCE_BEGIN");
  MLADSLeanCapturePose();
  Print("[MLPOSE80] STATIC_LEFT_FRAME15_REFERENCE_COMPLETE");
 }

 // Read-only calibration for the requested stationary, anatomical-right pose.
 bool MLADSLeanStaticReferenceReady()
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() != this || !IsAlive())
   return false;
  if (m_MLADSLeanGate < 0.98 || m_MLADSLeanAmount < 0.98 || m_MLADSLeanMoveBlend > 0.02)
   return false;
  if (!IsRaised())
   return false;
  HumanMovementState exportState = new HumanMovementState();
  GetMovementState(exportState);
  if (exportState.m_iMovement != 0)
   return false;
  if (exportState.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT && exportState.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_RAISEDERECT)
   return false;
  return true;
 }
 void MLADSLeanExportStaticReference()
 {
  if (!MLADSLeanStaticReferenceReady())
   return;
  Print("[MLPOSE80] STATIC_RIGHT_REFERENCE_BEGIN");
  MLADSLeanCapturePose();
  Print("[MLPOSE80] STATIC_RIGHT_REFERENCE_COMPLETE");
 }

 // Read-only F9 snapshot of the currently evaluated skeleton; no graph or input writes.
 protected void MLADSLeanCapturePose()
 {
  string captureId = GetGame().GetTime().ToString();
  captureId += "_" + m_MLADSLeanDemo;
  string header = "[MLPOSE80] BEGIN id=" + captureId;
  header += " demo=" + m_MLADSLeanDemo;
  header += " lean=" + m_MLADSLeanAmount;
  header += " move_blend=" + m_MLADSLeanMoveBlend;
  header += " gate=" + m_MLADSLeanGate;
  header += " raised=" + IsRaised();
  Print(header);
  vector actorTM[4];
  GetTransform(actorTM);
  for (int actorRow = 0; actorRow < 4; actorRow++)
  {
   string actorLine = "[MLPOSE80] ACTOR id=" + captureId;
   actorLine += " row=" + actorRow;
   actorLine += " value=" + actorTM[actorRow];
   Print(actorLine);
  }
  array<string> captureBones = {
   "Pelvis",
   "RightUpLeg",
   "RightUpLegRoll",
   "RightKneeExtra",
   "RightLeg",
   "RightLegRoll",
   "RightFoot",
   "RightToeBase",
   "RightHipExtra",
   "LeftHipExtra",
   "Spine",
   "Spine1",
   "Spine2",
   "Spine3",
   "Neck",
   "Neck1",
   "Head",
   "Face_Hub",
   "Face_EyelidUpperLeft",
   "Face_EyelidUpperRight",
   "Face_Jawbone",
   "Face_Chin",
   "Face_ChopLeft",
   "Face_ChopRight",
   "Face_Jowl",
   "Face_LipLowerLeft",
   "Face_LipLowerMiddle",
   "Face_LipLowerRight",
   "Face_Tongue",
   "EyeRight",
   "EyeLeft",
   "Face_CheekFrontLeft",
   "Face_CheekFrontRight",
   "Face_CheekUpperLeft",
   "Face_CheekUpperRight",
   "Face_CornerLeft",
   "Face_CheekSideLeft",
   "Face_CornerRight",
   "Face_CheekSideRight",
   "Face_EyelidLowerLeft",
   "Face_EyelidLowerRight",
   "Face_Eyelids",
   "Face_Forehead",
   "Face_BrowFrontLeft",
   "Face_BrowFrontRight",
   "Face_BrowMiddle",
   "Face_BrowSideLeft",
   "Face_BrowSideRight",
   "Face_LipUpperLeft",
   "Face_LipUpperMiddle",
   "Face_LipUpperRight",
   "Face_NostrilLeft",
   "Face_NostrilRight",
   "LeftShoulder",
   "LeftArm",
   "LeftArmRoll",
   "LeftForeArm",
   "LeftForeArmRoll",
   "LeftHand",
   "LeftHandRing",
   "LeftHandRing1",
   "LeftHandRing2",
   "LeftHandRing3",
   "LeftHandMiddle1",
   "LeftHandMiddle2",
   "LeftHandMiddle3",
   "LeftHandIndex1",
   "LeftHandIndex2",
   "LeftHandIndex3",
   "LeftHandThumb1",
   "LeftHandThumb2",
   "LeftHandThumb3",
   "LeftHandPinky",
   "LeftHandPinky1",
   "LeftHandPinky2",
   "LeftHandPinky3",
   "LeftWristExtra",
   "LeftForeArmExtra",
   "LeftElbowExtra",
   "LeftArmExtra",
   "RightShoulder",
   "RightArm",
   "RightArmRoll",
   "RightForeArm",
   "RightForeArmRoll",
   "RightHand",
   "RightHandRing",
   "RightHandRing1",
   "RightHandRing2",
   "RightHandRing3",
   "RightHandThumb1",
   "RightHandThumb2",
   "RightHandThumb3",
   "RightHandMiddle1",
   "RightHandMiddle2",
   "RightHandMiddle3",
   "RightHandIndex1",
   "RightHandIndex2",
   "RightHandIndex3",
   "RightHandPinky",
   "RightHandPinky1",
   "RightHandPinky2",
   "RightHandPinky3",
   "RightWristExtra",
   "RightForeArmExtra",
   "RightElbowExtra",
   "RightArmExtra",
   "LeftUpLeg",
   "LeftUpLegRoll",
   "LeftKneeExtra",
   "LeftLeg",
   "LeftLegRoll",
   "LeftFoot",
   "LeftToeBase"
  };
  int capturedCount = 0;
  foreach (string captureBone : captureBones)
  {
   int captureIndex = GetBoneIndexByName(captureBone);
   // Human bone IDs are signed identifiers, not nonnegative array indices.
   // Every name in this list belongs to the supplied DayZ skeleton.
   // Do not discard a valid bone merely because its ID is negative.
   vector boneTM[4];
   GetBoneTransformMS(captureIndex, boneTM);
   capturedCount++;
   for (int boneRow = 0; boneRow < 4; boneRow++)
   {
    string boneLine = "[MLPOSE80] BONE id=" + captureId;
    boneLine += " name=" + captureBone;
    boneLine += " row=" + boneRow;
    boneLine += " value=" + boneTM[boneRow];
    Print(boneLine);
   }
  }
  EntityAI capturedWeapon = GetHumanInventory().GetEntityInHands();
  if (capturedWeapon)
  {
   Print("[MLPOSE80] WEAPON_TYPE id=" + captureId + " name=" + capturedWeapon.GetType());
   vector weaponTM[4];
   capturedWeapon.GetTransform(weaponTM);
   for (int weaponRow = 0; weaponRow < 4; weaponRow++)
   {
    string weaponLine = "[MLPOSE80] WEAPON id=" + captureId;
    weaponLine += " row=" + weaponRow;
    weaponLine += " value=" + weaponTM[weaponRow];
    Print(weaponLine);
   }
  }
  string captureEnd = "[MLPOSE80] END id=" + captureId;
  captureEnd += " bones=" + capturedCount;
  Print(captureEnd);
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
  Print("[MLADSLEAN80] demo=" + m_MLADSLeanDemo + " joints=" + label + " interior_deg=" + angle + " first_ms=" + a + " middle_ms=" + b + " last_ms=" + c);
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
  Print("[MLADSLEAN80] target_killed ragdoll=" + m_MLADSLeanRangeRagdoll);
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
  Print("[MLADSLEAN80] target_ragdoll_retry active=" + m_MLADSLeanRangeRagdoll);
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
  Print("[MLADSLEAN80] target_ragdoll_momentum velocity=" + m_MLADSLeanRangeDeathVelocity);
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
