// Offline Mosin lean test. Player and designated demo use the same graph/pose.
class MLADSLeanSettings
{
 static bool ElbowReadyNoticeShown;
 static int AutomaticPoseCaptureBudget = 0;
 static bool DetailedDiagnostics = false;
 static bool ArmDropTest = true;
 static bool ArmDropControlBound;
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
 static PlayerBase WalkingActor;
 // Last moving ADS gait of the selected player; start at walk until measured.
};
modded class PlayerBase
{
 // Legacy name retained for existing graph compatibility: now ANY actor's
 // upright walking/running bank, never a blue-NPC designation.
 protected bool m_ML173Walking;
 protected ref ML173EditorScope m_ML173Scope;
 protected int m_ML173PreviewVar = -1;
 protected bool m_ML183UnarmedPreview;
 protected bool m_ML190HeldPreview;
 protected bool m_ML193OtherHeldPreview;
 protected bool m_ML200OneHandPreview;
 protected bool m_ML202HeavyPreview;
 protected bool m_ML204PolearmPreview;
 protected bool m_ML206Lineup;
 protected int m_ML216PreviewGait;
 protected bool m_ML216JogEditor;
 protected bool m_ML224PlayerJogBank;
 protected ref ML216EditorScope m_ML216Scope;
 void ML216StartAimGaitPreview(int gait)
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() == this)
   return;
  m_ML216PreviewGait = gait;
  m_ML216JogEditor = gait == 2;
  if (m_ML216JogEditor)
   ML216Preset.Init();
  ML213StartRaisedLineup(false, true);
 }

 protected bool m_ML213WalkingPreview = true;
 protected bool m_ML213RaisedExample;
 protected bool m_ML213RaisedCrouch;
 bool ML213UsesWalkingPreview()
 {
  return m_ML213WalkingPreview;
 }
 void ML213StartLoweredLineup(bool walking)
 {
  m_ML213WalkingPreview = walking;
  ML206StartLineup();
 }
 void ML213StartRaisedLineup(bool crouch, bool walking)
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() == this)
   return;
  m_ML206Lineup = true;
  m_ML206Anchor = GetPosition();
  m_ML213WalkingPreview = walking;
  m_ML213RaisedExample = true;
  m_ML213RaisedCrouch = crouch;
  m_ML183UnarmedPreview = false;
  m_ML181CrouchDemo = true;
  m_ML181RaisedDemo = true;
  m_ML181CrouchForced = false;
  m_ML182NativeReference = false;
  MLADSLeanStartDemo();
 }

 protected bool m_ML207SmgEditor;
 protected bool m_ML209SledgeEditor;
 protected bool m_ML211FlashEditor;
 protected bool m_ML214CanEditor;
 void ML214EnableCanEditor()
 {
  m_ML214CanEditor = true;
  ML214Preset.Init();
 }
 bool ML214UsesCanEditor()
 {
  return m_ML214CanEditor;
 }

 void ML211EnableFlashEditor()
 {
  m_ML211FlashEditor = true;
  ML211Preset.Init();
 }
 bool ML211UsesFlashEditor()
 {
  return m_ML211FlashEditor;
 }

 void ML209EnableSledgeEditor()
 {
  m_ML209SledgeEditor = true;
  ML209Preset.Init();
 }
 bool ML209UsesSledgeEditor()
 {
  return m_ML209SledgeEditor;
 }

 void ML207EnableSmgEditor()
 {
  m_ML207SmgEditor = true;
  ML207Preset.Init();
 }
 bool ML207UsesSmgEditor()
 {
  return m_ML207SmgEditor;
 }

 protected vector m_ML206Anchor;
 void ML206StartLineup()
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() == this)
   return;
  m_ML206Lineup = true;
  m_ML206Anchor = GetPosition();
  // Presets are selected by the actual native held-item behavior.
  m_ML190HeldPreview = MLHeldCategory192.UsesRifleHolding(this);
  m_ML193OtherHeldPreview = MLHeldCategory192.UsesTwoHandedHolding(this);
  m_ML200OneHandPreview = MLHeldCategory192.UsesOneHandedHolding(this);
  m_ML202HeavyPreview = MLHeldCategory192.UsesHeavyHolding(this);
  m_ML204PolearmPreview = MLHeldCategory192.UsesPolearmHolding(this);
  ML183StartUnarmedComparison(false);
 }

 protected bool m_ML187SharedActive;
 protected ref ML183UnarmedPose m_ML183UnarmedPose;
 void ML204StartPolearmComparison()
 {
  ML204Preset.Init();
  m_ML204PolearmPreview = true;
  ML183StartUnarmedComparison(false);
 }
 void ML202StartHeavyComparison()
 {
  ML202Preset.Init();
  m_ML202HeavyPreview = true;
  ML183StartUnarmedComparison(false);
 }
 void ML200StartOneHandComparison()
 {
  ML200Preset.Init();
  m_ML200OneHandPreview = true;
  ML183StartUnarmedComparison(false);
 }
 void ML193StartOtherHeldComparison()
 {
  ML193Preset.Init();
  m_ML193OtherHeldPreview = true;
  ML183StartUnarmedComparison(false);
 }
 void ML190StartHeldComparison()
 {
  ML190Preset.Init();
  m_ML190HeldPreview = true;
  ML183StartUnarmedComparison(false);
 }
 void ML183StartUnarmedComparison(bool nativeReference)
 {
  m_ML183UnarmedPreview = true;
  m_ML182NativeReference = nativeReference;
  m_ML181CrouchDemo = true; // Existing demo lifecycle / stance-lock release.
  m_ML181RaisedDemo = false;
  m_ML181CrouchForced = false;
  ML183Preset.Init();
  MLADSLeanStartDemo();
 }
 protected bool m_ML182NativeReference;
 protected bool m_ML182EditableCrouch;
 protected ref ML182EditorScope m_ML182Scope;
 protected ref ML182CrouchHold m_ML182Hold;
 void ML182StartCrouchComparison(bool nativeReference)
 {
  m_ML182NativeReference = nativeReference;
  m_ML182EditableCrouch = !nativeReference;
  if (m_ML182EditableCrouch)
   ML182Preset.Init();
  ML181StartCrouchDemo(true);
 }
 protected bool ML182BodyReady()
 {
  return m_ML182Hold && m_ML182Hold.ReadyNow && ML144State.ArmsReady;
 }
 protected void ML182UpdateCrouchHold(float dt, HumanMovementState state)
 {
  if (!m_ML182EditableCrouch || !m_ML147Bound)
   return;
  if (!m_ML182Hold)
   m_ML182Hold = new ML182CrouchHold;
  if (m_ML87ViewAmount > 0.5)
   return;
  m_ML182Hold.Update(this, state, dt, m_MLADSLeanGate, m_MLADSLeanAmount);
 }
 protected bool m_ML181CrouchDemo;
 protected bool m_ML181RaisedDemo;
 protected bool m_ML181CrouchForced;
 protected bool m_ML181ReleaseCrouch;
 protected int m_ML181ArmKey = -1;
 protected int m_ML181HoldRevision[4];
 protected int m_ML181BodyRevision[4];
 void ML181StartCrouchDemo(bool raised)
 {
  m_ML181CrouchDemo = true;
  m_ML181RaisedDemo = raised;
  m_ML181CrouchForced = false;
  MLADSLeanStartDemo();
 }
 protected void ML181RefreshBankWrites()
 {
  for (int i = 0; i < 55; i++)
   m_ML154EditorWritten[i] = false;
  for (int part = 0; part < m_ML149Last.Count(); part++)
   m_ML149Last[part] = 1000;
 }
 protected int m_ML179Vars[6];
 protected bool m_ML179Tried;
 protected bool m_ML179Bound;
 protected vector m_ML179LegacyFore;
 protected vector m_ML179EditorFore;
 protected void ML179BindArmControls()
 {
  if (m_ML179Tried || !m_MLADSLeanBound)
   return;
  m_ML179Tried = true;
  m_ML179Bound = true;
  TStringArray names = {"ML179PoleForeX", "ML179PoleForeY", "ML179PoleForeZ", "ML179EditForeX", "ML179EditForeY", "ML179EditForeZ"};
  for (int i = 0; i < 6; i++)
  {
   m_ML179Vars[i] = GetAnimInterface().BindVariableFloat(names[i]);
   if (m_ML179Vars[i] < 0)
    m_ML179Bound = false;
   for (int previous = 0; previous < i; previous++)
   {
    if (m_ML179Vars[i] == m_ML179Vars[previous])
     m_ML179Bound = false;
   }
  }
  Print("[MLARM179] minimum_twist_controls=" + m_ML179Bound);
 }
 protected ref ML172WalkUpper m_ML172Upper;
 protected void ML172UpdateWalkingUpper(float dt, HumanMovementState state)
 {
  if (m_MLADSLeanDemo || !m_ML149Bound)
   return;
  if (!m_ML172Upper)
   m_ML172Upper = new ML172WalkUpper;
  m_ML172Upper.Update(this, state, dt, m_MLADSLeanGate, m_MLADSLeanAmount, m_MLADSLeanMoveBlend, m_ML106Profile, m_ML104PoleReady);
 }
 protected int m_ML169NativeVar = -1;
 protected bool m_ML169NativeTried;
 protected float m_ML169LastMode = -1;
 protected int m_ML118ContactVar = -1;
 protected bool m_ML118ContactTried;
 protected bool m_ML118ContactBound;
 protected int m_ML106ProfileVar = -1;
 protected bool m_ML106ProfileBound;
 protected EntityAI m_ML106ProfileWeapon;
 protected int m_ML106Profile;
 protected int m_ML106NativeWeaponState = -1;
 protected int m_ML104PoleVars[10];
 protected bool m_ML104PoleBound;
 protected bool m_ML104PoleReady;
 protected bool m_ML104AfterRecorded;
 protected EntityAI m_ML104PoleWeapon;
 protected vector m_ML104LeftAngles;
 protected vector m_ML104LeftHandAngles;
 protected vector m_ML104RightAngles;
 protected float m_ML104AfterTime;
 protected float m_ML104LeftStable;
 protected float m_ML104CalibCooldown;
 protected int m_ML104CalibAttempts;
 protected bool m_ML104FailureRecorded;
 protected bool m_ML101CaptureDone[4];
 protected int m_ML93DropVar = -1;
 protected bool m_ML93DropBound;
 protected float m_ML93DropLastMode = -1;
 protected float m_ML93DropStable;
 protected float m_ML93DropElapsed;
 protected int m_ML87ViewVar = -1;
 protected bool m_ML87ViewBound;
 protected float m_ML87ViewAmount;
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
 protected float m_MLADSLeanDemoWarmup;
 protected bool m_MLADSLeanDemoGraphNeedsReset;
 protected bool m_MLADSLeanDemoReady;
 protected bool m_MLADSLeanDemoWasRaised;
 protected int m_MLADSLeanDemoRaiseTransitions;
 protected float m_MLADSLeanDemoSign = -1;
 protected float m_MLADSLeanDemoAmount;
 protected int m_MLADSLeanDemoArmIK = -1;
 protected int m_MLADSLeanDemoADS = -1;
 protected int m_MLADSLeanDemoRaised = -1;
 protected int m_MLADSLeanDemoAim = -1;
 protected int m_MLADSLeanDemoAimIK = -1;
 protected int m_MLADSLeanDemoAimUD = -1;
 protected bool m_MLADSLeanDemoNativeBound;

 protected int m_ML144Vars[18];
 protected bool m_ML144Tried;
 protected bool m_ML144Bound;
 // Cached head-only alignment: sample uncorrected settled poses once, never
 // chase the corrected output. NPC reference is shared; offsets stay per actor.
 protected void ML163ReportHeight(HumanMovementState state, vector headMS, vector pelvisMS)
 {
  int leftFootBone = GetBoneIndexByName("LeftFoot");
  int rightFootBone = GetBoneIndexByName("RightFoot");
  if (leftFootBone == -1 || rightFootBone == -1)
   return;
  vector leftFootMS = GetBonePositionMS(leftFootBone);
  vector rightFootMS = GetBonePositionMS(rightFootBone);
  float feetY = leftFootMS[1] + rightFootMS[1];
  feetY = feetY * 0.5;
  float headAboveFeet = headMS[1] - feetY;
  float pelvisAboveFeet = pelvisMS[1] - feetY;
  float actorScale = GetScale();
  vector originWS = GetPosition();
  float groundY = GetGame().SurfaceY(originWS[0], originWS[2]);
  float originAboveGround = originWS[1] - groundY;
  string heightReport = "[MLHEIGHT163] demo=" + m_MLADSLeanDemo;
  heightReport += " type=" + GetType();
  heightReport += " scale=" + actorScale;
  heightReport += " native_raised=" + IsRaised();
  heightReport += " raise_complete=" + IsWeaponRaiseCompleted();
  heightReport += " stance=" + state.m_iStanceIdx;
  heightReport += " player_ads=" + IsInIronsights();
  heightReport += " head_above_feet_m=" + headAboveFeet;
  heightReport += " pelvis_above_feet_m=" + pelvisAboveFeet;
  heightReport += " origin_above_ground_m=" + originAboveGround;
  Print(heightReport);
 }
 protected bool m_ML160NeutralCaptured;
 protected bool m_ML160RightReported;
 protected float m_ML160NeutralX;
 protected float m_ML160ProbeTime;
 protected void ML160ReportPosition(float dt, HumanMovementState state)
 {
  bool reportStanding = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool reportReady = reportStanding && state.m_iMovement == 0 && m_MLADSLeanMoveBlend < 0.01;
  reportReady = reportReady && m_ML87ViewAmount < 0.01 && m_ML106Profile == 1 && m_MLADSLeanGate > 0.98;
  reportReady = reportReady && (m_MLADSLeanDemo || ML69AimCentered());
  bool reportNeutral = Math.AbsFloat(m_MLADSLeanAmount) < 0.001;
  bool reportRight = m_MLADSLeanAmount > 0.999;
  if (!reportReady || (!reportNeutral && !reportRight))
  {
   m_ML160ProbeTime = 0;
   return;
  }
  if (reportNeutral && m_ML160NeutralCaptured)
   return;
  if (reportRight && m_ML160RightReported)
   return;
  if (reportRight && !m_ML160NeutralCaptured)
   return;
  m_ML160ProbeTime += Math.Clamp(dt, 0, 0.05);
  if (m_ML160ProbeTime < 0.8)
   return;
  int reportHead = GetBoneIndexByName("Head");
  int reportPelvis = GetBoneIndexByName("Pelvis");
  if (reportHead == -1 || reportPelvis == -1)
   return;
  vector reportHeadPosition = GetBonePositionMS(reportHead);
  vector reportPelvisPosition = GetBonePositionMS(reportPelvis);
  ML163ReportHeight(state, reportHeadPosition, reportPelvisPosition);
  if (reportNeutral)
  {
   m_ML160NeutralX = reportHeadPosition[0];
   m_ML160NeutralCaptured = true;
   Print("[MLPOSITION160] neutral_head_ms=" + reportHeadPosition + " pelvis_ms=" + reportPelvisPosition + " demo=" + m_MLADSLeanDemo);
  }
  else if (m_ML160NeutralCaptured)
  {
   float reportTravel = reportHeadPosition[0] - m_ML160NeutralX;
   Print("[MLPOSITION160] right_head_ms=" + reportHeadPosition + " pelvis_ms=" + reportPelvisPosition + " travel_m=" + reportTravel + " demo=" + m_MLADSLeanDemo);
   m_ML160RightReported = true;
  }
 }
 protected int m_ML157Vars[3];
 protected bool m_ML157Bound;
 protected bool m_ML157Tried;
 protected int m_ML157Revision = -1;
 protected int m_ML157BodyRevision = -1;
 protected EntityAI m_ML157Weapon;
 protected int m_ML157Key = -1;
 protected float m_ML157Settled;
 protected float m_ML157Fade;
 protected bool m_ML157Ready[4];
 protected vector m_ML157Correction[4];
 // Authored head test: no sampled NPC-to-player automatic head offsets.
 // F6 head and F7 neck/head values continue through their existing graph nodes.
 protected void ML157UpdateHead(float dt, HumanMovementState state)
 {
  if (!m_ML157Tried && m_ML149Bound)
  {
   m_ML157Tried = true;
   m_ML157Vars[0] = GetAnimInterface().BindVariableFloat("ML157HeadX");
   m_ML157Vars[1] = GetAnimInterface().BindVariableFloat("ML157HeadY");
   m_ML157Vars[2] = GetAnimInterface().BindVariableFloat("ML157HeadZ");
   m_ML157Bound = m_ML157Vars[0] >= 0 && m_ML157Vars[1] >= 0 && m_ML157Vars[2] >= 0;
  }
  if (!m_ML157Bound)
   return;
  for (int headAxis = 0; headAxis < 3; headAxis++)
   AnimSetFloat(m_ML157Vars[headAxis], 0.0);
 }
 protected ref array<int> m_ML149Vars = new array<int>;
 protected ref array<float> m_ML149Last = new array<float>;
 protected bool m_ML149Tried;
 protected bool m_ML149Bound;
 protected float m_ML149ArmFade;
 protected bool ML149AffectsWeapon(int part)
 {
  return part <= 4 || (part >= 8 && part <= 15);
 }
 protected void ML149Set(int index, float value)
 {
  if (Math.AbsFloat(m_ML149Last[index] - value) < 0.000001)
   return;
  m_ML149Last[index] = value;
  AnimSetFloat(m_ML149Vars[index], value);
 }
 protected void ML149UpdateBody(HumanMovementState state)
 {
  ML149State.Init();
  if (!m_ML149Tried && m_ML147Bound && m_ML146Bound)
  {
   m_ML149Tried = true;
   m_ML149Bound = true;
   TStringArray names = new TStringArray;
   TStringArray axes = {"TX", "TY", "TZ", "RX", "RY", "RZ"};
   foreach (string bone : ML149State.Bones)
   {
    foreach (string axisName : axes)
     names.Insert("ML149" + bone + axisName);
   }
   names.Insert("ML149WeaponFollow");
   foreach (string activeBone : ML149State.Bones)
    names.Insert("ML154" + activeBone + "Active");
   for (int index = 0; index < names.Count(); index++)
   {
    int id = GetAnimInterface().BindVariableFloat(names[index]);
    m_ML149Bound = m_ML149Bound && id >= 0;
    for (int previous = 0; previous < m_ML149Vars.Count(); previous++)
     m_ML149Bound = m_ML149Bound && id != m_ML149Vars[previous];
    m_ML149Bound = m_ML149Bound && id != m_MLADSLeanGateVar && id != m_MLADSLeanAmountVar;
    m_ML149Vars.Insert(id);
    m_ML149Last.Insert(1000);
   }
   Print("[MLBODY149] bound=" + m_ML149Bound + " count=" + m_ML149Vars.Count());
   if (m_ML149Bound)
    ML149State.Bound = true;
  }
  if (!m_ML149Bound || m_ML149Vars.Count() != 169)
   return;
  bool standing = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  float scope = 0;
  if ((standing || m_ML182EditableCrouch) && (state.m_iMovement == 0 || m_ML173Walking) && m_ML87ViewAmount < 0.01 && m_ML106Profile == 1 && IsAlive() && !IsUnconscious())
  {
   scope = m_MLADSLeanGate * (1.0 - m_MLADSLeanMoveBlend);
   if (m_ML173Walking)
    scope = m_MLADSLeanGate;
   if (m_ML182EditableCrouch && !ML182BodyReady())
    scope = 0;
   if (!MLADSLeanSettings.ArmDropTest)
    scope = 0;
  }
  float leftWeight = Math.Clamp(-m_MLADSLeanAmount, 0, 1) * scope;
  float rightWeight = Math.Clamp(m_MLADSLeanAmount, 0, 1) * scope;
  float weaponWeight = 0;
  int slot = 0;
  for (int partIndex = 0; partIndex < 24; partIndex++)
  {
   ML149Part left = ML149State.Left.Parts[partIndex];
   ML149Part right = ML149State.Right.Parts[partIndex];
   float activePart = 0;
   for (int component = 0; component < 6; component++)
   {
    float value = left.ComponentValue(component) * leftWeight;
    value = value + right.ComponentValue(component) * rightWeight;
    if (Math.AbsFloat(value) > 0.0001)
     activePart = 1;
    if (ML149AffectsWeapon(partIndex) && Math.AbsFloat(value) > 0.0001)
     weaponWeight = 1;
    if (component < 3)
     value = value * 0.01;
    else
     value = -value * Math.DEG2RAD;
    ML149Set(slot, value);
    slot++;
   }
   int activeSlot = 145 + partIndex;
   ML149Set(activeSlot, activePart);
  }
  ML149Set(144, weaponWeight);
 }
 protected float m_ML154EditorLast[55];
 protected bool m_ML154EditorWritten[55];
 protected void ML154EditorFloat(int cacheSlot, int variableId, float value)
 {
  if (m_ML154EditorWritten[cacheSlot] && m_ML154EditorLast[cacheSlot] == value)
   return;
  m_ML154EditorWritten[cacheSlot] = true;
  m_ML154EditorLast[cacheSlot] = value;
  AnimSetFloat(variableId, value);
 }
 protected int m_ML147Vars[22];
 protected bool m_ML147Tried;
 protected bool m_ML147Bound;
 protected int m_ML147ArmSide = -1;
 protected void ML147UpdateBothSides()
 {
  if (!m_ML147Tried && m_ML144Bound)
  {
   m_ML147Tried = true;
   m_ML147Bound = true;
   TStringArray names = new TStringArray;
   names.Insert("ML147LeftHoldLeftArmX");
   names.Insert("ML147LeftHoldLeftArmY");
   names.Insert("ML147LeftHoldLeftArmZ");
   names.Insert("ML147LeftHoldLeftForeArmX");
   names.Insert("ML147LeftHoldLeftForeArmY");
   names.Insert("ML147LeftHoldLeftForeArmZ");
   names.Insert("ML147LeftHoldLeftHandX");
   names.Insert("ML147LeftHoldLeftHandY");
   names.Insert("ML147LeftHoldLeftHandZ");
   names.Insert("ML147LeftHoldRightArmX");
   names.Insert("ML147LeftHoldRightArmY");
   names.Insert("ML147LeftHoldRightArmZ");
   names.Insert("ML147LeftHoldRightForeArmX");
   names.Insert("ML147LeftHoldRightForeArmY");
   names.Insert("ML147LeftHoldRightForeArmZ");
   names.Insert("ML147LeftHoldRightHandX");
   names.Insert("ML147LeftHoldRightHandY");
   names.Insert("ML147LeftHoldRightHandZ");
   names.Insert("ML147LeftMuzzleYaw");
   names.Insert("ML147LeftMuzzlePitch");
   names.Insert("ML147RightMuzzleYaw");
   names.Insert("ML147RightMuzzlePitch");
   for (int index = 0; index < 22; index++)
   {
    m_ML147Vars[index] = GetAnimInterface().BindVariableFloat(names[index]);
    m_ML147Bound = m_ML147Bound && m_ML147Vars[index] >= 0;
    for (int previous = 0; previous < index; previous++)
     m_ML147Bound = m_ML147Bound && m_ML147Vars[index] != m_ML147Vars[previous];
    for (int old = 0; old < 18; old++)
     m_ML147Bound = m_ML147Bound && m_ML147Vars[index] != m_ML144Vars[old];
    m_ML147Bound = m_ML147Bound && m_ML147Vars[index] != m_MLADSLeanGateVar;
    m_ML147Bound = m_ML147Bound && m_ML147Vars[index] != m_MLADSLeanAmountVar;
   }
   Print("[MLPOSEEDITOR147] left_muzzle_bound=" + m_ML147Bound);
  }
  if (!m_ML147Bound || !ML144State.LeftCoefficients || ML144State.LeftCoefficients.Count() != 18)
   return;
  for (int coefficient = 0; coefficient < 18; coefficient++)
   ML154EditorFloat(18 + coefficient, m_ML147Vars[coefficient], ML144State.LeftCoefficients[coefficient]);
  ML144Values left = ML144State.LeftValues;
  ML144Values right = ML144State.RightValues;
  if (left && right)
  {
   ML154EditorFloat(36, m_ML147Vars[18], left.MuzzleYaw);
   ML154EditorFloat(37, m_ML147Vars[19], left.MuzzlePitch);
   ML154EditorFloat(38, m_ML147Vars[20], right.MuzzleYaw);
   ML154EditorFloat(39, m_ML147Vars[21], right.MuzzlePitch);
  }
 }
 protected int m_ML146Vars[15];
 protected bool m_ML146Tried;
 protected bool m_ML146Bound;
 protected bool m_ML146Ready;
 protected EntityAI m_ML146Weapon;
 protected int m_ML146HoldRevision = -1;
 protected float m_ML146Settled;
 protected int m_ML146ValuesRevision = -1;
 protected int m_ML154BodyRevision = -1;
 protected bool m_ML154ReferenceReady[8];
 protected vector m_ML146Root[16];
 protected vector m_ML146Elbow[16];
 protected vector m_ML146Wrist[16];
 protected vector m_ML146Arm[2];
 protected vector m_ML146Hand[2];
 protected bool ML146CaptureSide(int side, string prefix)
 {
  int armBone = GetBoneIndexByName(prefix + "Arm");
  int elbowBone = GetBoneIndexByName(prefix + "ForeArm");
  int handBone = GetBoneIndexByName(prefix + "Hand");
  if (armBone == -1 || elbowBone == -1 || handBone == -1)
   return false;
  int snapshot = m_ML181ArmKey * 2 + side;
  m_ML146Root[snapshot] = GetBonePositionMS(armBone);
  m_ML146Elbow[snapshot] = GetBonePositionMS(elbowBone);
  m_ML146Wrist[snapshot] = GetBonePositionMS(handBone);
  vector upper = m_ML146Elbow[snapshot] - m_ML146Root[snapshot];
  vector lower = m_ML146Wrist[snapshot] - m_ML146Elbow[snapshot];
  return upper.Length() > 0.1 && lower.Length() > 0.1;
 }
 protected void ML146UpdateArmsHead(float dt, HumanMovementState state)
 {
  if (!m_ML146Tried && m_ML144Bound)
  {
   m_ML146Tried = true;
   m_ML146Bound = true;
   TStringArray names = new TStringArray;
   names.Insert("ML146LeftArmX");
   names.Insert("ML146LeftArmY");
   names.Insert("ML146LeftArmZ");
   names.Insert("ML146LeftHandX");
   names.Insert("ML146LeftHandY");
   names.Insert("ML146LeftHandZ");
   names.Insert("ML146RightArmX");
   names.Insert("ML146RightArmY");
   names.Insert("ML146RightArmZ");
   names.Insert("ML146RightHandX");
   names.Insert("ML146RightHandY");
   names.Insert("ML146RightHandZ");
   names.Insert("ML146HeadX");
   names.Insert("ML146HeadY");
   names.Insert("ML146HeadZ");
   for (int index = 0; index < 15; index++)
   {
    m_ML146Vars[index] = GetAnimInterface().BindVariableFloat(names[index]);
    m_ML146Bound = m_ML146Bound && m_ML146Vars[index] >= 0;
    for (int previous = 0; previous < index; previous++)
     m_ML146Bound = m_ML146Bound && m_ML146Vars[index] != m_ML146Vars[previous];
    for (int oldControl = 0; oldControl < 18; oldControl++)
     m_ML146Bound = m_ML146Bound && m_ML146Vars[index] != m_ML144Vars[oldControl];
    m_ML146Bound = m_ML146Bound && m_ML146Vars[index] != m_MLADSLeanGateVar;
    m_ML146Bound = m_ML146Bound && m_ML146Vars[index] != m_MLADSLeanAmountVar;
   }
   Print("[MLPOSEEDITOR146] arms_head_bound=" + m_ML146Bound);
  }
  if (!m_ML146Bound || !ML144State.Values)
   return;
  int leanSide = 0;
  if (m_MLADSLeanAmount > 0)
   leanSide = 1;
  int bank = 0;
  if (m_ML173Walking)
   bank = 1;
  if (m_ML182EditableCrouch)
   bank = 2;
  if ((m_ML216JogEditor || m_ML224PlayerJogBank) && m_ML173Walking)
   bank = 3;
  int referenceSide = bank * 2 + leanSide;
  if (referenceSide != m_ML181ArmKey)
  {
   m_ML181ArmKey = referenceSide;
   m_ML147ArmSide = leanSide;
   m_ML146Ready = m_ML154ReferenceReady[referenceSide];
   m_ML149ArmFade = 0;
   m_ML146Settled = 0;
   m_ML146ValuesRevision = -1;
  }
  EntityAI weapon = GetHumanInventory().GetEntityInHands();
  bool weaponChanged = weapon != m_ML146Weapon;
  bool bankChanged = m_ML181HoldRevision[bank] != ML144State.HoldRevision;
  if (!m_ML182EditableCrouch)
   bankChanged = bankChanged || m_ML181BodyRevision[bank] != ML149State.GeometryRevision;
  if (weaponChanged)
  {
   m_ML146Weapon = weapon;
   for (int clearBank = 0; clearBank < 8; clearBank++)
    m_ML154ReferenceReady[clearBank] = false;
  }
  if (weaponChanged || bankChanged)
  {
   m_ML181HoldRevision[bank] = ML144State.HoldRevision;
   m_ML181BodyRevision[bank] = ML149State.GeometryRevision;
   int firstSide = bank * 2;
   m_ML154ReferenceReady[firstSide] = false;
   m_ML154ReferenceReady[firstSide + 1] = false;
   m_ML146Ready = false;
   m_ML146ValuesRevision = -1;
   m_ML146Settled = 0;
  }
  ML144Values armSettings = ML144State.SideValues(leanSide == 0);
  bool armsNeeded = false;
  if (armSettings)
  {
   armsNeeded = armSettings.LeftPitch != 0 || armSettings.LeftYaw != 0 || armSettings.LeftRoll != 0;
   armsNeeded = armsNeeded || armSettings.RightPitch != 0 || armSettings.RightYaw != 0 || armSettings.RightRoll != 0;
  }
  if (!armsNeeded)
   ML144State.ArmsReady = true;
  else if (!m_ML146Ready)
   ML144State.ArmsReady = false;
  bool standing = state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  bool stable = (standing || m_ML182EditableCrouch) && state.m_iMovement == 0 && m_MLADSLeanMoveBlend < 0.01;
  if (m_ML173Walking)
   stable = standing && state.m_iMovement == 1 && m_MLADSLeanMoveBlend > 0.98;
  if ((m_ML216JogEditor || m_ML224PlayerJogBank) && m_ML173Walking)
   stable = standing && state.m_iMovement == 2 && m_MLADSLeanMoveBlend > 0.98;
  stable = stable && Math.AbsFloat(m_MLADSLeanAmount) > 0.98 && m_MLADSLeanGate > 0.98;
  stable = stable && m_ML87ViewAmount < 0.01 && m_ML106Profile == 1 && ML69AimCentered();
  stable = stable && MLADSLeanSettings.ArmDropTest && IsAlive() && !IsUnconscious() && armsNeeded;
  if (m_ML173Walking && leanSide == 0 && !m_ML104PoleReady && m_ML104CalibAttempts < 3)
   stable = false;
  if (m_ML182EditableCrouch && (!m_ML182Hold || !m_ML182Hold.ReadyNow))
   stable = false;
  if (!m_ML146Ready)
  {
   if (stable)
    m_ML146Settled += Math.Clamp(dt, 0, 0.05);
   else
    m_ML146Settled = 0;
   if (m_ML146Settled > 0.2)
   {
    bool leftValid = ML146CaptureSide(0, "Left");
    bool rightValid = ML146CaptureSide(1, "Right");
    m_ML146Ready = leftValid && rightValid;
    m_ML154ReferenceReady[referenceSide] = m_ML146Ready;
    if (MLADSLeanSettings.DetailedDiagnostics)
     Print("[MLPOSEEDITOR146] arm_reference_ready=" + m_ML146Ready + " demo=" + m_MLADSLeanDemo);
    if (m_ML146Ready)
     ML144State.ArmsReady = true;
   }
  }
  if (m_ML146Ready)
   m_ML149ArmFade = Math.Min(1.0, m_ML149ArmFade + Math.Clamp(dt, 0, 0.05) / 0.08);
  else
   m_ML149ArmFade = 0;
  ML144Values value = ML144State.SideValues(leanSide == 0);
  if (!value)
   return;
  vector leftAngles = Vector(value.LeftPitch, value.LeftYaw, value.LeftRoll);
  vector rightAngles = Vector(value.RightPitch, value.RightYaw, value.RightRoll);
  if (!m_ML146Ready)
  {
   m_ML146Arm[0] = vector.Zero;
   m_ML179EditorFore = vector.Zero;
   m_ML146Arm[1] = vector.Zero;
   m_ML146Hand[0] = vector.Zero;
   m_ML146Hand[1] = vector.Zero;
  }
  else if (m_ML146ValuesRevision != ML144State.ValuesRevision)
  {
   m_ML146ValuesRevision = ML144State.ValuesRevision;
   vector leftArm;
   vector leftHand;
   vector rightArm;
   vector rightHand;
   int leftSnapshot = referenceSide * 2;
   int rightSnapshot = leftSnapshot + 1;
   bool leftSolved;
   vector newFore;
   if ((m_ML173Walking || m_ML182EditableCrouch) && m_ML179Bound)
    leftSolved = ML179ArmSwing.Editor(m_ML146Root[leftSnapshot], m_ML146Elbow[leftSnapshot], m_ML146Wrist[leftSnapshot], leftAngles, leftArm, newFore, leftHand);
   else
    leftSolved = ML146ArmMath.Swivel(m_ML146Root[leftSnapshot], m_ML146Elbow[leftSnapshot], m_ML146Wrist[leftSnapshot], leftAngles, leftArm, leftHand);
   bool rightSolved = ML146ArmMath.Swivel(m_ML146Root[rightSnapshot], m_ML146Elbow[rightSnapshot], m_ML146Wrist[rightSnapshot], rightAngles, rightArm, rightHand);
   if (leftSolved)
   {
    m_ML146Arm[0] = leftArm;
    m_ML179EditorFore = newFore;
    m_ML146Hand[0] = leftHand;
   }
   if (rightSolved)
   {
    m_ML146Arm[1] = rightArm;
    m_ML146Hand[1] = rightHand;
   }
   if (!leftSolved || !rightSolved)
    ML144State.Status = "Elbow direction is singular; previous arm rotation retained.";
  }
  if ((m_ML173Walking || m_ML182EditableCrouch) && m_ML179Bound)
  {
   for (int editorAxis = 0; editorAxis < 3; editorAxis++)
   {
    float foreValue = m_ML179EditorFore[editorAxis] * m_ML149ArmFade;
    AnimSetFloat(m_ML179Vars[editorAxis + 3], foreValue);
   }
  }
  int slot = 0;
  for (int side = 0; side < 2; side++)
  {
   vector upperAngles = m_ML146Arm[side];
   vector wristAngles = m_ML146Hand[side];
   for (int axis = 0; axis < 3; axis++)
   {
    ML154EditorFloat(40 + slot, m_ML146Vars[slot], upperAngles[axis] * m_ML149ArmFade);
    slot++;
   }
   for (int handAxis = 0; handAxis < 3; handAxis++)
   {
    ML154EditorFloat(40 + slot, m_ML146Vars[slot], wristAngles[handAxis] * m_ML149ArmFade);
    slot++;
   }
  }
  ML154EditorFloat(52, m_ML146Vars[12], -value.HeadPitch * Math.DEG2RAD);
  ML154EditorFloat(53, m_ML146Vars[13], -value.HeadYaw * Math.DEG2RAD);
  ML154EditorFloat(54, m_ML146Vars[14], -value.HeadRoll * Math.DEG2RAD);
 }
 protected float m_ML136Cycle;
 protected int m_ML158PoseIndex;
 void MLADSLeanStartDemo()
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() == this)
   return;
  m_MLADSLeanDemo = true;
  m_MLADSLeanDemoWarmup = 0;
  m_MLADSLeanDemoReady = false;
  m_ML136Cycle = 0;
  m_ML158PoseIndex = 0;
  m_MLADSLeanDemoSign = -1;
  m_MLADSLeanDemoAmount = -1;
 }
 void MLADSLeanStopDemo()
 {
  m_MLADSLeanDemo = false;
  m_ML206Lineup = false;
  m_MLADSLeanDemoReady = false;
  m_MLADSLeanDemoGraphNeedsReset = true;
  m_ML181ReleaseCrouch = m_ML181CrouchDemo;
  m_ML181CrouchForced = false;
  HumanInputController input = GetInputController();
  if (input)
  {
   input.OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
   input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
   input.OverrideRaise(HumanInputControllerOverrideType.DISABLED, false);
  }
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
  HumanCommandMove move = GetCommand_Move();
  if (!move)
  {
   StartCommand_Move();
   move = GetCommand_Move();
   m_ML181CrouchForced = false;
  }
  if (move && m_ML181CrouchDemo && !m_ML181CrouchForced)
  {
   if (m_ML213RaisedExample)
   {
    if (m_ML213RaisedCrouch)
     move.ForceStance(DayZPlayerConstants.STANCEIDX_CROUCH);
    else
     move.ForceStance(DayZPlayerConstants.STANCEIDX_ERECT);
   }
   else if (m_ML183UnarmedPreview)
    move.ForceStance(DayZPlayerConstants.STANCEIDX_ERECT);
   else
    move.ForceStance(DayZPlayerConstants.STANCEIDX_CROUCH);
   m_ML181CrouchForced = true;
  }
  float previewSpeed = 0;
  float previewAngle = 0;
  m_MLADSLeanDemoSign = ML181CrouchCycle.Target(GetGame().GetTime());
  if (m_ML206Lineup)
  {
   m_MLADSLeanDemoSign = ML206LineupClock.Target(GetGame().GetTime());
   if (m_ML213WalkingPreview && ML206LineupClock.Walking(GetGame().GetTime()))
   {
    previewSpeed = 1;
    previewAngle = 90;
    if (m_MLADSLeanDemoSign < 0)
     previewAngle = -90;
   }
  }
  if (m_ML216PreviewGait > 0)
  {
   m_MLADSLeanDemoSign = ML216AimGaitCycle.Target(GetGame().GetTime());
   previewSpeed = 0;
   previewAngle = 0;
   if (ML216AimGaitCycle.Moving(GetGame().GetTime()))
   {
    previewSpeed = m_ML216PreviewGait;
    previewAngle = 90;
    if (m_MLADSLeanDemoSign < 0)
     previewAngle = -90;
   }
  }
  input.OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, previewSpeed);
  input.OverrideMovementAngle(HumanInputControllerOverrideType.ENABLED, previewAngle);
  input.OverrideRaise(HumanInputControllerOverrideType.ENABLED, m_ML181RaisedDemo);
  float step = 4.5 * Math.Clamp(dt, 0, 0.25);
  if (m_MLADSLeanDemoAmount < m_MLADSLeanDemoSign)
   m_MLADSLeanDemoAmount = Math.Min(m_MLADSLeanDemoSign, m_MLADSLeanDemoAmount + step);
  else
   m_MLADSLeanDemoAmount = Math.Max(m_MLADSLeanDemoSign, m_MLADSLeanDemoAmount - step);
 }
 protected void ML144UpdateEditor()
 {
  ML153Preset.Init();
  if (!m_ML144Tried && m_MLADSLeanBound && m_ML106ProfileBound)
  {
   m_ML144Tried = true;
   m_ML144Bound = true;
   TStringArray names = new TStringArray;
   names.Insert("ML144LeftArmX");
   names.Insert("ML144LeftArmY");
   names.Insert("ML144LeftArmZ");
   names.Insert("ML144LeftForeArmX");
   names.Insert("ML144LeftForeArmY");
   names.Insert("ML144LeftForeArmZ");
   names.Insert("ML144LeftHandX");
   names.Insert("ML144LeftHandY");
   names.Insert("ML144LeftHandZ");
   names.Insert("ML144RightArmX");
   names.Insert("ML144RightArmY");
   names.Insert("ML144RightArmZ");
   names.Insert("ML144RightForeArmX");
   names.Insert("ML144RightForeArmY");
   names.Insert("ML144RightForeArmZ");
   names.Insert("ML144RightHandX");
   names.Insert("ML144RightHandY");
   names.Insert("ML144RightHandZ");
   for (int i = 0; i < 18; i++)
   {
    m_ML144Vars[i] = GetAnimInterface().BindVariableFloat(names[i]);
    m_ML144Bound = m_ML144Bound && m_ML144Vars[i] >= 0;
    for (int previous = 0; previous < i; previous++)
     m_ML144Bound = m_ML144Bound && m_ML144Vars[i] != m_ML144Vars[previous];
    m_ML144Bound = m_ML144Bound && m_ML144Vars[i] != m_MLADSLeanGateVar;
    m_ML144Bound = m_ML144Bound && m_ML144Vars[i] != m_MLADSLeanAmountVar;
    m_ML144Bound = m_ML144Bound && m_ML144Vars[i] != m_MLADSLeanCanaryVar;
    m_ML144Bound = m_ML144Bound && m_ML144Vars[i] != m_ML106ProfileVar;
    m_ML144Bound = m_ML144Bound && m_ML144Vars[i] != m_ML118ContactVar;
    m_ML144Bound = m_ML144Bound && m_ML144Vars[i] != m_ML93DropVar;
    m_ML144Bound = m_ML144Bound && m_ML144Vars[i] != m_ML87ViewVar;
   }
   Print("[MLPOSEEDITOR144] bound=" + m_ML144Bound + " demo=" + m_MLADSLeanDemo);
   if (m_ML144Bound)
    ML144State.Bound = true;
  }
  if (!m_ML144Bound || !ML144State.RightCoefficients || ML144State.RightCoefficients.Count() != 18)
   return;
  for (int coefficient = 0; coefficient < 18; coefficient++)
   ML154EditorFloat(coefficient, m_ML144Vars[coefficient], ML144State.RightCoefficients[coefficient]);
 }
 override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
 {
  if (GetIsSimulationDisabled())
   return;
  if (m_ML181ReleaseCrouch)
  {
   HumanCommandMove releaseMove = GetCommand_Move();
   if (releaseMove)
    releaseMove.ForceStance(-1);
   m_ML181ReleaseCrouch = false;
  }
  MLADSLeanCalibrateStandingHeight();
  MLADSLeanUpdateDemoInput(pDt);
  super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);
  if (GetIsSimulationDisabled() || GetGame().IsDedicatedServer() || !GetAnimInterface())
   return;
  // Pin every preview mode, including the legacy raised/crouched examples.
  if (m_ML206Lineup && GetGame().GetPlayer() != this && IsAlive())
   SetPosition(m_ML206Anchor);
  if (m_ML183UnarmedPreview)
  {
   if (!m_ML183UnarmedPose)
    m_ML183UnarmedPose = new ML183UnarmedPose;
   if (m_ML206Lineup)
   {
    if (!m_ML183UnarmedPose.ConfigureLineup(this))
    {
     SetPosition(m_ML206Anchor);
     return;
    }
   }
   else
   {
   m_ML183UnarmedPose.HeldEditor = m_ML190HeldPreview;
   m_ML183UnarmedPose.OtherHeldEditor = m_ML193OtherHeldPreview;
   m_ML183UnarmedPose.OneHandEditor = m_ML200OneHandPreview;
   m_ML183UnarmedPose.HeavyEditor = m_ML202HeavyPreview;
   m_ML183UnarmedPose.PolearmEditor = m_ML204PolearmPreview;
   }
   m_ML183UnarmedPose.Update(this, pDt, m_MLADSLeanDemoAmount, m_ML182NativeReference);
   // Offline preview-only root-motion pin; animation still receives WALK input.
   if (m_ML206Lineup && m_MLADSLeanDemo && GetGame().GetPlayer() != this && IsAlive())
    SetPosition(m_ML206Anchor);
   return;
  }
  ML153Preset.Init();
  ML173Preset.Init();
  HumanMovementState routingState = new HumanMovementState();
  GetMovementState(routingState);
  EntityAI crouchHeld = GetHumanInventory().GetEntityInHands();
  bool crouchedPose = routingState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH || routingState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDCROUCH;
  bool crouchMoveCommand = pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE && IsAlive() && !IsUnconscious();
  bool useCrouch = crouchMoveCommand && crouchedPose && routingState.m_iMovement == 0 && MLADSLeanWeaponSupport106.Profile(crouchHeld) == 1;
  if (useCrouch != m_ML182EditableCrouch)
  {
   if (!useCrouch && m_ML182Hold)
    m_ML182Hold.Write(this, null, false);
   m_ML182EditableCrouch = useCrouch;
   ML181RefreshBankWrites();
   m_ML181ArmKey = -1;
  }
  bool sharedStanding = routingState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT;
  bool itemAction = GetWeaponManager() && GetWeaponManager().IsRunning();
  bool smgWalking = routingState.m_iMovement == 1 && MLHeldCategory192.IsSMG(crouchHeld);
  bool toolWalking = routingState.m_iMovement == 1 && MLHeldCategory192.IsWalkingTool(crouchHeld);
  bool oneHandWalking = routingState.m_iMovement == 1 && MLHeldCategory192.UsesOneHandedHolding(this);
  bool canWalking = oneHandWalking && MLHeldCategory192.UsesCanBandageHolding(this);
  bool sharedLean = pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE && IsAlive() && !IsUnconscious() && sharedStanding && (routingState.m_iMovement == 0 || smgWalking || toolWalking || oneHandWalking) && !IsRaised() && !itemAction && MLADSLeanSettings.Enabled;
  // First-person leaning uses the native crouch branch, including lowered hands.
  // Third-person helper routing is unchanged.
  DayZPlayerCamera routeCamera = GetCurrentCamera();
  bool fpRoute = false;
  if (GetGame().GetPlayer() == this && !m_MLADSLeanDemo && routeCamera)
  {
   string routeName = routeCamera.GetCameraName();
   fpRoute = routeName == "DayZPlayerCamera1stPerson";
   fpRoute = fpRoute || routeName == "DayZPlayerCameraIronsights";
   fpRoute = fpRoute || routeName == "DayZPlayerCameraOptics";
  }
  if (m_ML87ViewBound && !fpRoute)
  {
   m_ML87ViewAmount = 0;
   AnimSetFloat(m_ML87ViewVar, 0.0);
  }
  if (fpRoute)
   sharedLean = false;
  if (sharedLean)
  {
   m_ML187SharedActive = true;
   m_MLADSLeanGate = 0;
   m_ML56GatePhase = 0;
   if (m_MLADSLeanBound)
    AnimSetFloat(m_MLADSLeanGateVar, 0);
   if (!m_ML183UnarmedPose)
    m_ML183UnarmedPose = new ML183UnarmedPose;
   m_ML183UnarmedPose.HeldEditor = MLHeldCategory192.UsesRifleHolding(this) && !smgWalking;
   m_ML183UnarmedPose.SmgWalkingEditor = smgWalking;
   m_ML183UnarmedPose.PistolBank = MLHeldCategory192.UsesPistolHolding(this);
   m_ML183UnarmedPose.OtherHeldEditor = MLHeldCategory192.UsesTwoHandedHolding(this) && !toolWalking;
   m_ML183UnarmedPose.SledgeWalkingEditor = toolWalking;
   m_ML183UnarmedPose.OneHandEditor = MLHeldCategory192.UsesOneHandedHolding(this) && !oneHandWalking;
   m_ML183UnarmedPose.OneHandWalkingEditor = oneHandWalking && !canWalking;
   m_ML183UnarmedPose.CanWalkingEditor = canWalking;
   m_ML183UnarmedPose.HeavyEditor = MLHeldCategory192.UsesHeavyHolding(this);
   m_ML183UnarmedPose.PolearmEditor = MLHeldCategory192.UsesPolearmHolding(this) && !toolWalking;
   m_ML183UnarmedPose.UpdatePlayer(this, pDt, routingState.m_fLeaning);
   return;
  }
  if (m_ML187SharedActive)
  {
   m_ML187SharedActive = false;
   if (m_ML183UnarmedPose)
    m_ML183UnarmedPose.ReleasePlayer(this);
   ML181RefreshBankWrites();
  }
  // Each client renders remote actors through custom third-person banks.
  // Only this client's controlled first-person actor selects the native FP branch.
  bool playerJogBank = !m_MLADSLeanDemo && !useCrouch;
  playerJogBank = playerJogBank && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE;
  playerJogBank = playerJogBank && ML181PoseRouting.WalkingBank(routingState.m_iStanceIdx, routingState.m_iMovement);
  playerJogBank = playerJogBank && routingState.m_iMovement == 2;
  playerJogBank = playerJogBank && IsAlive() && !IsUnconscious() && IsRaised();
  playerJogBank = playerJogBank && MLADSLeanWeaponSupport106.Profile(crouchHeld) == 1;
  if (playerJogBank != m_ML224PlayerJogBank)
  {
   m_ML224PlayerJogBank = playerJogBank;
   ML181RefreshBankWrites();
   m_ML181ArmKey = -1;
  }
  bool useWalking = ML181PoseRouting.WalkingBank(routingState.m_iStanceIdx, routingState.m_iMovement);
  if (useWalking != m_ML173Walking)
   ML181RefreshBankWrites();
  m_ML173Walking = useWalking;
  if (m_ML182EditableCrouch)
  {
   ML182Preset.Init();
   if (!m_ML182Scope)
    m_ML182Scope = new ML182EditorScope;
   m_ML182Scope.Enter();
  }
  else if (m_ML216JogEditor || m_ML224PlayerJogBank)
  {
   ML216Preset.Init();
   if (!m_ML216Scope)
    m_ML216Scope = new ML216EditorScope;
   m_ML216Scope.Enter();
  }
  else if (useWalking)
  {
   if (!m_ML173Scope)
    m_ML173Scope = new ML173EditorScope;
   m_ML173Scope.Enter();
  }
  ML173UpdateGraph(pDt, pCurrentCommandID, pCurrentCommandFinished);
  if (m_ML182EditableCrouch)
   m_ML182Scope.Leave();
  else if (m_ML216JogEditor || m_ML224PlayerJogBank)
   m_ML216Scope.Leave();
  else if (useWalking)
   m_ML173Scope.Leave();
 }
 protected void ML173UpdateGraph(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
 {
  // Stop may be requested outside CommandHandler; clear graph state here only.
  if (m_MLADSLeanDemoGraphNeedsReset && m_MLADSLeanBound && m_MLADSLeanDemoNativeBound)
  {
   AnimSetFloat(m_MLADSLeanCanaryVar, 0.731);
   AnimSetFloat(m_MLADSLeanGateVar, 0);
   AnimSetFloat(m_MLADSLeanAmountVar, 0);
   m_MLADSLeanDemoGraphNeedsReset = false;
  }
  bool localPlayer = GetGame().GetPlayer() == this;
  if (GetGame().IsDedicatedServer() || !GetAnimInterface())
   return;
  if (!m_ML169NativeTried || (m_ML169NativeVar < 0 && m_MLADSLeanBound))
  {
   m_ML169NativeTried = true;
   m_ML169NativeVar = GetAnimInterface().BindVariableFloat("ML169UseNative");
   if (m_ML169NativeVar == m_MLADSLeanGateVar || m_ML169NativeVar == m_MLADSLeanAmountVar || m_ML169NativeVar == m_MLADSLeanCanaryVar)
    m_ML169NativeVar = -1;
   Print("[MLCOMPARE169] bound=" + m_ML169NativeVar);
  }
  if (m_ML169NativeVar >= 0)
  {
   float compareMode = 0;
   if (!MLADSLeanSettings.Enabled || m_ML182NativeReference)
    compareMode = 1;
   if (compareMode != m_ML169LastMode)
   {
    AnimSetFloat(m_ML169NativeVar, compareMode);
    m_ML169LastMode = compareMode;
   }
  }
  if (m_MLADSLeanBound && m_ML173PreviewVar < 0)
   m_ML173PreviewVar = GetAnimInterface().BindVariableFloat("ML173WalkingPreview");
  if (m_ML173PreviewVar >= 0)
  {
   float walkingPreview = 0;
   if (m_ML173Walking)
    walkingPreview = 1;
   AnimSetFloat(m_ML173PreviewVar, walkingPreview);
  }
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
   m_ML87ViewVar = GetAnimInterface().BindVariableFloat("ML87FirstPersonCrouchLean");
   m_ML87ViewBound = m_ML87ViewVar >= 0;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_MLADSLeanGateVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_MLADSLeanCanaryVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_MLADSLeanAmountVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_MLADSLeanNativeLeanVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_MLADSLeanNativeMoveVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_MLADSLeanWeaponShiftVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_MLADSLeanHeightVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_MLADSLeanMoveBlendVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_ML50ReachVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_ML56LowSmoothVar;
   m_ML87ViewBound = m_ML87ViewBound && m_ML87ViewVar != m_ML71SupportVar;
   m_ML93DropVar = GetAnimInterface().BindVariableFloat("ML93ArmDrop");
   m_ML93DropBound = m_ML93DropVar >= 0;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_ML87ViewVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_MLADSLeanGateVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_MLADSLeanCanaryVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_MLADSLeanAmountVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_MLADSLeanNativeLeanVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_MLADSLeanNativeMoveVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_MLADSLeanWeaponShiftVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_MLADSLeanHeightVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_MLADSLeanMoveBlendVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_ML50ReachVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_ML56LowSmoothVar;
   m_ML93DropBound = m_ML93DropBound && m_ML93DropVar != m_ML71SupportVar;
   if (localPlayer)
    MLADSLeanSettings.ArmDropControlBound = m_ML93DropBound;
   m_ML106ProfileVar = GetAnimInterface().BindVariableFloat("ML106ShoulderedGrip");
   m_ML106ProfileBound = m_ML106ProfileVar >= 0;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_ML93DropVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_ML87ViewVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_MLADSLeanGateVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_MLADSLeanCanaryVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_MLADSLeanAmountVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_MLADSLeanNativeLeanVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_MLADSLeanNativeMoveVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_MLADSLeanWeaponShiftVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_MLADSLeanHeightVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_MLADSLeanMoveBlendVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_ML50ReachVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_ML56LowSmoothVar;
   m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_ML71SupportVar;
   TStringArray poleNames = new TStringArray;
   poleNames.Insert("ML104ElbowEnabled");
   poleNames.Insert("ML104LeftX");
   poleNames.Insert("ML104LeftY");
   poleNames.Insert("ML104LeftZ");
   poleNames.Insert("ML104RightX");
   poleNames.Insert("ML104RightY");
   poleNames.Insert("ML104RightZ");
   poleNames.Insert("ML104LeftHandX");
   poleNames.Insert("ML104LeftHandY");
   poleNames.Insert("ML104LeftHandZ");
   m_ML104PoleBound = m_ML93DropBound && m_ML87ViewBound;
   for (int poleIndex = 0; poleIndex < 10; poleIndex++)
   {
    m_ML104PoleVars[poleIndex] = GetAnimInterface().BindVariableFloat(poleNames[poleIndex]);
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] >= 0;
    m_ML106ProfileBound = m_ML106ProfileBound && m_ML106ProfileVar != m_ML104PoleVars[poleIndex];
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_ML93DropVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_ML87ViewVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_MLADSLeanGateVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_MLADSLeanCanaryVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_MLADSLeanAmountVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_MLADSLeanNativeLeanVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_MLADSLeanNativeMoveVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_MLADSLeanWeaponShiftVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_MLADSLeanHeightVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_MLADSLeanMoveBlendVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_ML50ReachVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_ML56LowSmoothVar;
    m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_ML71SupportVar;
    for (int priorPole = 0; priorPole < poleIndex; priorPole++)
     m_ML104PoleBound = m_ML104PoleBound && m_ML104PoleVars[poleIndex] != m_ML104PoleVars[priorPole];
   }
   Print("[MELBOW104] bind=" + m_ML104PoleBound + " demo=" + m_MLADSLeanDemo);
   if (localPlayer)
    MLADSLeanSettings.HasGraph = m_MLADSLeanBound;
   Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " bind_valid=" + m_MLADSLeanBound + " gate=" + m_MLADSLeanGateVar + " amount=" + m_MLADSLeanAmountVar + " canary=" + m_MLADSLeanCanaryVar + " nativeLean=" + m_MLADSLeanNativeLeanVar + " nativeMove=" + m_MLADSLeanNativeMoveVar);
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
  if (held != m_ML106ProfileWeapon)
  {
   m_ML106ProfileWeapon = held;
   m_ML106Profile = MLADSLeanWeaponSupport106.Profile(held);
   // A new handling pose needs a new standing-height/reach reference.
   m_MLADSLeanStandingHeadY = 0;
   m_ML50ReachTrim = 0;
   m_ML50ReachStable = 0;
   string heldType = "empty";
   if (held)
    heldType = held.GetType();
   string profileReport = "[MLWEAPON106] demo=" + m_MLADSLeanDemo;
   profileReport += " held=" + heldType;
   profileReport += " profile=" + m_ML106Profile;
   profileReport += " class_bound=" + m_ML106ProfileBound;
   Print(profileReport);
  }
  float shouldered = 0;
  if (m_ML106Profile == 1)
   shouldered = 1;
  if (m_ML106ProfileBound)
   AnimSetFloat(m_ML106ProfileVar, shouldered);
  bool supportedGun = m_ML106Profile > 0 && m_ML106ProfileBound;
  int nativeWeaponState = 0;
  if (GetCommandModifier_Weapons())
   nativeWeaponState = 1;
  if (nativeWeaponState != m_ML106NativeWeaponState)
  {
   m_ML106NativeWeaponState = nativeWeaponState;
   string nativeReport = "[MLWEAPON106] native_weapon_command=" + nativeWeaponState;
   nativeReport += " held_profile=" + m_ML106Profile;
   nativeReport += " raised=" + IsRaised();
   Print(nativeReport);
  }

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
  // First-person-only native crouch presentation. Gameplay stance/input stay native.
  // The binary graph selector bypasses the entire custom locomotion pose path.
  bool firstPersonView = cameraName == "DayZPlayerCamera1stPerson";
  firstPersonView = firstPersonView || cameraName == "DayZPlayerCameraIronsights";
  firstPersonView = firstPersonView || cameraName == "DayZPlayerCameraOptics";
  bool fpCrouch = localPlayer && !m_MLADSLeanDemo && firstPersonView;
  fpCrouch = fpCrouch && MLADSLeanSettings.Enabled && supportedStance;
  fpCrouch = fpCrouch && IsAlive() && !IsUnconscious();
  fpCrouch = fpCrouch && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE;
  fpCrouch = fpCrouch && state.m_iMovement <= 2 && Math.AbsFloat(state.m_fLeaning) > 0.001;
  m_ML87ViewAmount = 0;
  if (fpCrouch)
   m_ML87ViewAmount = 1;
  if (m_ML87ViewBound)
   AnimSetFloat(m_ML87ViewVar, m_ML87ViewAmount);
  bool nativeADS = aiming;
  // Player inputs and camera ADS are not a controller for an offline dummy.
  // The demo has explicit raised/ADS graph routing via its registered canary.
  // Keep native player telemetry separate from requested animation state.
  bool demoControllerActive = false;
  if (m_MLADSLeanDemo)
  {
   demoControllerActive = m_MLADSLeanBound && m_MLADSLeanDemoNativeBound && supportedGun;
   demoControllerActive = demoControllerActive && IsAlive() && !IsUnconscious();
   demoControllerActive = demoControllerActive && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE;
   if (demoControllerActive)
    m_MLADSLeanDemoWarmup += Math.Clamp(pDt, 0, 0.25);
   else
    m_MLADSLeanDemoWarmup = 0;
   bool previouslyReady = m_MLADSLeanDemoReady;
   m_MLADSLeanDemoReady = demoControllerActive && m_MLADSLeanDemoWarmup >= 0.4;
   if (m_MLADSLeanDemoReady && !previouslyReady)
    Print("[MLADSLEAN104] demo_graph_warmup_complete stationary_lean_ready");
   if (raised != m_MLADSLeanDemoWasRaised)
   {
    m_MLADSLeanDemoRaiseTransitions++;
    m_MLADSLeanDemoWasRaised = raised;
   }
   // These are requested demo animation states, not native player ADS claims.
   raised = demoControllerActive && m_ML181RaisedDemo;
   ready = m_MLADSLeanDemoReady;
   aiming = false;
  }
  bool actorReady = !m_MLADSLeanDemo || m_MLADSLeanDemoNativeBound;
  bool customPoseEnabled = MLADSLeanSettings.Enabled && !m_ML182NativeReference;
  bool target = actorReady && m_MLADSLeanBound && customPoseEnabled && IsAlive() && !IsUnconscious() && supportedGun && supportedStance && state.m_iMovement <= 2 && pCurrentCommandID == DayZPlayerConstants.COMMANDID_MOVE && raised && (!m_MLADSLeanDemo || ready) && (aiming || inspectionAllowed);
  float targetValue = 0;
  if (target)
   targetValue = 1;
  // Blend throughout raising/lowering rather than waiting for raise completion.
  // Smoothstep gives zero velocity at both ends and identical left/right timing.
  if (!customPoseEnabled)
  {
   m_ML56GatePhase = 0;
   m_ML50ReachTrim = 0;
   m_MLADSLeanHeightLift = 0;
  }
  float stepGate = Math.Clamp(pDt, 0, 0.05) / 0.08;
  if (m_ML56GatePhase < targetValue)
   m_ML56GatePhase = Math.Min(targetValue, m_ML56GatePhase + stepGate);
  else
   m_ML56GatePhase = Math.Max(targetValue, m_ML56GatePhase - stepGate);
  m_MLADSLeanGate = m_ML56GatePhase * m_ML56GatePhase * (3.0 - 2.0 * m_ML56GatePhase);
  m_MLADSLeanLeanRequested = Math.Clamp(state.m_fLeaning, -1, 1);
  if (m_MLADSLeanDemo)
   m_MLADSLeanLeanRequested = m_MLADSLeanDemoAmount;
  // Stock DayZ human movement settings: m_fLeaningSpeed = 4.5.
  // Cap custom progression at the same native rate instead of instant sign jumps.
  // If native leaning is already interpolated at this rate, follow it directly.
  float nativeLeanStep = 4.5 * Math.Clamp(pDt, 0, 0.25);
  float leanDelta = m_MLADSLeanLeanRequested - m_MLADSLeanAmount;
  leanDelta = Math.Clamp(leanDelta, -nativeLeanStep, nativeLeanStep);
  m_MLADSLeanAmount = m_MLADSLeanAmount + leanDelta;
  if (m_MLADSLeanBound && m_ML56LowSmoothVar >= 0)
  {
   float smoothLow = 0;
   if (supportedGun && supportedStance && customPoseEnabled && IsAlive() && !IsUnconscious())
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
   string transition = "[MLADSLEAN104] visual_transition demo=" + m_MLADSLeanDemo;
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
   if (demoControllerActive && m_ML181RaisedDemo)
    demoGraphValue = 1;
   AnimSetFloat(m_MLADSLeanCanaryVar, demoGraphValue);
   bool demoADS = false;
    AnimSetBool(m_MLADSLeanDemoADS, demoADS);
   AnimSetBool(m_MLADSLeanDemoRaised, raised);
   if (m_MLADSLeanDemoReady)
   {
    // Aim bit 0 and both hand chains; shared graph routing holds them active.
    if (m_ML181RaisedDemo)
     AnimSetInt(m_MLADSLeanDemoArmIK, 7);
    float demoNativeLean = m_MLADSLeanDemoAmount;
    if (!MLADSLeanSettings.Enabled || m_ML182NativeReference)
     demoNativeLean = m_MLADSLeanAmount;
    AnimSetFloat(m_MLADSLeanNativeLeanVar, demoNativeLean);
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
  ML179BindArmControls();
  ML93UpdateArmProbe(pDt, state);
  ML104UpdateElbowDirections(pDt, state);
  ML118UpdateContactGate();
  ML144UpdateEditor();
  ML147UpdateBothSides();
  ML182UpdateCrouchHold(pDt, state);
  ML146UpdateArmsHead(pDt, state);
  ML149UpdateBody(state);
  ML160ReportPosition(pDt, state);
  // ML181: shared saved head values, no NPC-only target correction.
  ML50UpdateStandingReach(pDt, state);
  // ML181: saved walking bank replaces old ML172 learned retarget.
  ML67ReadAimCoherence(pDt);
  if (m_MLADSLeanBound && m_ML50ReachBound)
   AnimSetFloat(m_ML50ReachVar, m_ML50ReachTrim);
  // HumanCommandWeapons.SetADS controls the native head tilt to optics.
  // Native player HandleADS may enable it in super; apply this afterward.
  bool suppressHeadTilt = MLADSLeanSettings.HeadCorrection && MLADSLeanSettings.Enabled;
  suppressHeadTilt = suppressHeadTilt && m_MLADSLeanBound && m_MLADSLeanGate > 0.01;
  suppressHeadTilt = suppressHeadTilt && Math.AbsFloat(m_MLADSLeanAmount) > 0.01;
  // FP default crouch keeps native ADS/head behavior.
  suppressHeadTilt = suppressHeadTilt && m_ML87ViewAmount < 0.5;
  bool requestedHeadADS = nativeADS;
  if (m_MLADSLeanDemo)
   requestedHeadADS = false;
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
  if (MLADSLeanSettings.DetailedDiagnostics && m_MLADSLeanShoulderStableTime > 0.35 && now >= m_MLADSLeanNextShoulderSample)
  {
   m_MLADSLeanNextShoulderSample = now + 1000;
   MLADSLeanReportShoulderPose(state.m_iMovement);
  }
  // Build the long diagnostic string at most once per reporting interval.
  bool reportDue = now >= m_MLADSLeanNextReport;
  if (localPlayer && target != m_MLADSLeanLastTarget)
   reportDue = true;
  if (!reportDue)
   return;
  // Keep each diagnostic expression small for the Enforce compiler.
  string status = "view=" + viewState;
  status += " camera=" + cameraName;
  status += " fp_crouch_lean=" + m_ML87ViewAmount;
  status += " fp_crouch_bound=" + m_ML87ViewBound;
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
   status += " demo_graph_active=" + demoControllerActive;
   status += " crouch_demo=" + m_ML181CrouchDemo;
   status += " native_reference=" + m_ML182NativeReference;
   status += " editable_crouch=" + m_ML182EditableCrouch;
   status += " raised_demo=" + m_ML181RaisedDemo;
   status += " native_stance=" + state.m_iStanceIdx;
   status += " requested_ads=false";
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
   Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " " + status + " supported_rifle=" + supportedGun + " custom=" + MLADSLeanSettings.Enabled + " demo_native_controls=" + m_MLADSLeanDemoNativeBound);
  }
 }
 // Shared neutral-standing head-height reference; never rescale the mesh/actor.
 protected void MLADSLeanCalibrateStandingHeight()
 {
  if (m_MLADSLeanStandingHeadY > 0 || GetGame().IsMultiplayer())
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
  string referenceMessage = "[MLADSLEAN104] standing_height_reference demo=" + m_MLADSLeanDemo;
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
  string sample = "[MLADSLEAN104] shoulder_observed demo=" + m_MLADSLeanDemo;
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
  Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " measured_native_lean=" + measuredState.m_fLeaning + " custom_amount=" + m_MLADSLeanAmount);
  int headIndex = GetBoneIndexByName("Head");
  int chestIndex = GetBoneIndexByName("Spine3");
  if (headIndex >= 0 && chestIndex >= 0)
  {
   vector headBasis[4];
   GetBoneTransformMS(headIndex, headBasis);
   Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " head_basis_x_ms=" + headBasis[0]);
   Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " head_basis_y_ms=" + headBasis[1]);
   Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " head_basis_z_ms=" + headBasis[2]);
   vector head = GetBonePositionMS(headIndex);
   vector chest = GetBonePositionMS(chestIndex);
   if (!m_MLADSLeanDemo && Math.AbsFloat(m_MLADSLeanAmount) < 0.02 && measuredState.m_iMovement == 0 && (measuredState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_ERECT || measuredState.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDERECT))
   {
    m_MLADSLeanNeutralHeadX = head[0];
    m_MLADSLeanNeutralChestX = chest[0];
    m_MLADSLeanNeutralMeasured = true;
   }
   Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " head_ms=" + head + " chest_ms=" + chest + " neutral_measured=" + m_MLADSLeanNeutralMeasured);
   if (m_MLADSLeanNeutralMeasured)
    Print("[MLADSLEAN104] exposure head_dx_m=" + (head[0] - m_MLADSLeanNeutralHeadX) + " chest_dx_m=" + (chest[0] - m_MLADSLeanNeutralChestX));
  }
  EntityAI held = GetHumanInventory().GetEntityInHands();
  if (held)
  {
   Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " weapon_orientation_ws=" + held.GetOrientation());
   vector weaponPositionMS = WorldToModel(held.GetPosition());
   Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " weapon_position_ms=" + weaponPositionMS);
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
  // First-person crouch-style upper body deliberately has a different reach.
  // Preserve the last third-person calibration; do not chase this view pose.
  if (m_ML87ViewAmount > 0)
  {
   m_ML50ReachStable = 0;
   return;
  }
  // The direct right-pose displacement must not compete with old head feedback.
  bool directRightPosition = m_MLADSLeanAmount > 0.01 && m_ML106Profile == 1;
  directRightPosition = directRightPosition && MLADSLeanSettings.ArmDropTest && state.m_iMovement == 0;
  if (directRightPosition)
  {
   m_ML50ReachTrim = 0;
   m_ML50ReachStable = 0;
   return;
  }
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
  if (!MLADSLeanWeaponSupport106.Supported(measuredGun))
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
  if (!MLADSLeanSettings.DetailedDiagnostics)
   return;
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
  string readback = "[MLAIM104] demo=" + m_MLADSLeanDemo;
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

 // Called only in CommandHandler after super. Compare a known existing
 // rotation chain, not another late translation or scripted wrist feedback.
 protected void ML93UpdateArmProbe(float dt, HumanMovementState state)
 {
  float mode = 0;
  if (MLADSLeanSettings.ArmDropTest)
   mode = 1;
  if (m_ML93DropBound)
   AnimSetFloat(m_ML93DropVar, mode);
  if (mode != m_ML93DropLastMode)
  {
   m_ML93DropLastMode = mode;
   m_ML93DropStable = 0;
   m_ML93DropElapsed = 0;
  }
  float sampleStep = Math.Clamp(dt, 0, 0.05);
  m_ML93DropStable += sampleStep;
  m_ML93DropElapsed += sampleStep;
  if (m_ML93DropStable < 0.4 || m_ML93DropElapsed < 0.25)
   return;
  if (m_MLADSLeanGate < 0.98 || Math.AbsFloat(m_MLADSLeanAmount) < 0.98 || m_MLADSLeanMoveBlend < 0.98)
   return;
  if (m_ML87ViewAmount > 0 || state.m_iMovement == 0)
   return;
  m_ML93DropElapsed = 0;
  if (!MLADSLeanSettings.DetailedDiagnostics)
   return;
  int leftHandIndex = GetBoneIndexByName("LeftHand");
  int rightHandIndex = GetBoneIndexByName("RightHand");
  int rightElbowIndex = GetBoneIndexByName("RightForeArm");
  int rightShoulderIndex = GetBoneIndexByName("RightShoulder");
  int chestIndex = GetBoneIndexByName("Spine3");
  if (leftHandIndex == -1 || rightHandIndex == -1 || rightElbowIndex == -1 || rightShoulderIndex == -1 || chestIndex == -1)
   return;
  vector leftHand = GetBonePositionMS(leftHandIndex);
  vector rightHand = GetBonePositionMS(rightHandIndex);
  vector rightElbow = GetBonePositionMS(rightElbowIndex);
  vector rightShoulder = GetBonePositionMS(rightShoulderIndex);
  vector chest = GetBonePositionMS(chestIndex);
  string sample = "[MLDROP104] demo=" + m_MLADSLeanDemo;
  sample += " control_bound=" + m_ML93DropBound;
  sample += " mode=" + mode;
  sample += " gait=" + state.m_iMovement;
  sample += " lean=" + m_MLADSLeanAmount;
  sample += " left_wrist_from_chest=" + (leftHand - chest);
  sample += " right_wrist_from_shoulder=" + (rightHand - rightShoulder);
  sample += " right_elbow_from_shoulder=" + (rightElbow - rightShoulder);
  Print(sample);
  // Capture one stable native full pose per side and comparison mode, so
  // shoulder/weapon placement can be evaluated from actual game matrices.
  int stockCaptureSlot = 0;
  if (MLADSLeanSettings.ArmDropTest)
   stockCaptureSlot = 2;
  if (m_MLADSLeanAmount > 0)
   stockCaptureSlot++;
  if (!m_ML101CaptureDone[stockCaptureSlot])
  {
   m_ML101CaptureDone[stockCaptureSlot] = true;
   string stockCapture = "[MLSTOCK104] capture_slot=" + stockCaptureSlot;
   stockCapture += " demo=" + m_MLADSLeanDemo;
   stockCapture += " mode=" + mode;
   stockCapture += " lean=" + m_MLADSLeanAmount;
   Print(stockCapture);
   ML104CapturePoseLimited("stock_side_mode");
  }
 }

 protected void ML104CapturePoseLimited(string reason)
 {
  if (MLADSLeanSettings.AutomaticPoseCaptureBudget <= 0)
   return;
  MLADSLeanSettings.AutomaticPoseCaptureBudget--;
  Print("[MELBOW104] automatic_capture=" + reason);
  MLADSLeanCapturePose();
 }

 // One-time calibration from a native pose with this new overlay OFF.
 // Once ready, angles are fixed; no per-frame output-to-input correction loop.
 protected void ML104UpdateElbowDirections(float dt, HumanMovementState state)
 {
  if (!m_ML104PoleBound)
   return;
  if (m_ML106Profile != 1)
  {
   m_ML104PoleReady = false;
   m_ML104PoleWeapon = null;
   m_ML104LeftStable = 0;
   AnimSetFloat(m_ML104PoleVars[0], 0);
   return;
  }
  m_ML104CalibCooldown = Math.Max(0, m_ML104CalibCooldown - Math.Clamp(dt, 0, 0.05));
  EntityAI currentWeapon = GetHumanInventory().GetEntityInHands();
  if (currentWeapon != m_ML104PoleWeapon || !MLADSLeanSettings.ArmDropTest)
  {
   m_ML104PoleWeapon = currentWeapon;
   m_ML104PoleReady = false;
   m_ML104AfterRecorded = false;
   m_ML104AfterTime = 0;
   m_ML104LeftStable = 0;
   m_ML104CalibCooldown = 0;
   m_ML104CalibAttempts = 0;
   m_ML104FailureRecorded = false;
  }
  float enabled = 0;
  if (m_ML104PoleReady && MLADSLeanSettings.ArmDropTest)
   enabled = 1;
  // Only sample a stable, level, moving left pose in the third-person path.
  bool canSample = m_MLADSLeanGate > 0.98 && m_MLADSLeanAmount < -0.98;
  canSample = canSample && m_MLADSLeanMoveBlend > 0.98 && state.m_iMovement > 0;
  canSample = canSample && m_ML87ViewAmount < 0.01 && m_ML93DropStable > 0.4;
  canSample = canSample && MLADSLeanSettings.ArmDropTest && ML69AimCentered();
  if (canSample)
   m_ML104LeftStable += Math.Clamp(dt, 0, 0.05);
  else
   m_ML104LeftStable = 0;
  if (!m_ML104PoleReady && canSample && m_ML104LeftStable > 0.25 && m_ML104CalibCooldown <= 0 && m_ML104CalibAttempts < 3)
  {
   m_ML104CalibAttempts++;
   m_ML104CalibCooldown = 1.0;
   int leftRootIndex = GetBoneIndexByName("LeftArm");
   int leftElbowIndex = GetBoneIndexByName("LeftForeArm");
   int leftWristIndex = GetBoneIndexByName("LeftHand");
   int rightRootIndex = GetBoneIndexByName("RightArm");
   int rightElbowIndex = GetBoneIndexByName("RightForeArm");
   int rightWristIndex = GetBoneIndexByName("RightHand");
   int torsoIndex = GetBoneIndexByName("Spine3");
   bool bonesValid = leftRootIndex != -1 && leftElbowIndex != -1 && leftWristIndex != -1;
   bonesValid = bonesValid && rightRootIndex != -1 && rightElbowIndex != -1 && rightWristIndex != -1 && torsoIndex != -1;
   if (bonesValid)
   {
    vector leftRoot = GetBonePositionMS(leftRootIndex);
    vector leftElbow = GetBonePositionMS(leftElbowIndex);
    vector leftWrist = GetBonePositionMS(leftWristIndex);
    vector rightRoot = GetBonePositionMS(rightRootIndex);
    vector rightElbow = GetBonePositionMS(rightElbowIndex);
    vector rightWrist = GetBonePositionMS(rightWristIndex);
    vector torso = GetBonePositionMS(torsoIndex);
    // Left: 20 degrees from straight down, outward from the torso.
    float leftOutward = -0.34202014;
    if (torso[0] < leftRoot[0])
     leftOutward = 0.34202014;
    // Right: 45 degrees from straight down, outward from the torso.
    float outward = 0.70710678;
    if (rightRoot[0] < torso[0])
     outward = -0.70710678;
    vector leftGoal;
    vector rightGoal;
    bool leftOK;
    if (m_ML173Walking && m_ML179Bound)
     leftOK = ML179ArmSwing.Pole(leftRoot, leftElbow, leftWrist, Vector(leftOutward, -0.93969262, 0.0), m_ML104LeftAngles, m_ML179LegacyFore, m_ML104LeftHandAngles, leftGoal);
    else
     leftOK = MLArmPoleMath104.Swivel(leftRoot, leftElbow, leftWrist, Vector(leftOutward, -0.93969262, 0.0), m_ML104LeftAngles, leftGoal, m_ML104LeftHandAngles);
    bool rightOK = MLArmPoleMath104.Solve(rightRoot, rightElbow, rightWrist, Vector(outward, -0.70710678, 0.0), m_ML104RightAngles, rightGoal);
    m_ML104PoleReady = leftOK && rightOK;
    string report = "[MELBOW104] calibrated=" + m_ML104PoleReady;
    report += " demo=" + m_MLADSLeanDemo;
    report += " left_before=" + leftElbow;
    report += " left_goal=" + leftGoal;
    report += " right_before=" + rightElbow;
    report += " right_goal=" + rightGoal;
    report += " left_angles=" + m_ML104LeftAngles;
    report += " right_angles=" + m_ML104RightAngles;
    Print(report);
    if (m_ML104PoleReady || !m_ML104FailureRecorded)
    {
     m_ML104FailureRecorded = true;
     Print("[MELBOW104] BASELINE_NATIVE_POSE");
     ML104CapturePoseLimited("elbow_baseline");
    }
    if (m_ML104PoleReady)
    {
     enabled = 1;
     if (m_MLADSLeanDemo && !MLADSLeanSettings.ElbowReadyNoticeShown)
     {
      MLADSLeanSettings.ElbowReadyNoticeShown = true;
     }
    }
   }
  }
  if (m_ML173Walking && m_ML179Bound)
  {
   for (int foreAxis = 0; foreAxis < 3; foreAxis++)
    AnimSetFloat(m_ML179Vars[foreAxis], m_ML179LegacyFore[foreAxis]);
  }
  AnimSetFloat(m_ML104PoleVars[0], enabled);
  for (int poleAxis = 0; poleAxis < 3; poleAxis++)
  {
   AnimSetFloat(m_ML104PoleVars[poleAxis + 1], m_ML104LeftAngles[poleAxis]);
   AnimSetFloat(m_ML104PoleVars[poleAxis + 4], m_ML104RightAngles[poleAxis]);
   AnimSetFloat(m_ML104PoleVars[poleAxis + 7], m_ML104LeftHandAngles[poleAxis]);
  }
  if (enabled > 0 && canSample && !m_ML104AfterRecorded)
  {
   m_ML104AfterTime += Math.Clamp(dt, 0, 0.05);
   if (m_ML104AfterTime > 0.35)
   {
    m_ML104AfterRecorded = true;
    Print("[MELBOW104] AFTER_NATIVE_POSE");
    ML104CapturePoseLimited("elbow_after");
   }
  }
 }

 protected void ML118UpdateContactGate()
 {
  if (!m_ML118ContactTried && m_MLADSLeanBound && m_ML106ProfileBound && m_ML104PoleBound)
  {
   m_ML118ContactTried = true;
   m_ML118ContactVar = GetAnimInterface().BindVariableFloat("ML118ContactReady");
   m_ML118ContactBound = m_ML118ContactVar >= 0;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_ML106ProfileVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_MLADSLeanGateVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_MLADSLeanAmountVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_ML93DropVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_ML87ViewVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_MLADSLeanCanaryVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_MLADSLeanNativeLeanVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_MLADSLeanNativeMoveVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_MLADSLeanWeaponShiftVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_MLADSLeanHeightVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_MLADSLeanMoveBlendVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_ML50ReachVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_ML56LowSmoothVar;
   m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_ML71SupportVar;
   for (int index = 0; index < 10; index++)
    m_ML118ContactBound = m_ML118ContactBound && m_ML118ContactVar != m_ML104PoleVars[index];
   Print("[MLCONTACT118] bound=" + m_ML118ContactBound);
  }
  if (!m_ML118ContactBound)
   return;
  float ready = 0;
  if (m_ML104PoleReady)
   ready = 1;
  AnimSetFloat(m_ML118ContactVar, ready);
 }

 // Read-only camera weight, shared transition controls; no pose writes.
 float ML58RaisedViewWeight()
 {
  if (!MLADSLeanSettings.Enabled || !m_MLADSLeanBound || !IsAlive() || IsUnconscious())
   return 0;
  return Math.Clamp(m_MLADSLeanGate * Math.AbsFloat(m_MLADSLeanAmount), 0, 1);
 }

 // Position-only raised-view weight. The rifle pose has already been
 // interpolated by the native lean amount. Do not interpolate eye following
 // by that amount a second time on the left, which causes relative sinking.
 bool ML85LeftRaisedViewActive()
 {
  return m_MLADSLeanAmount < 0 && ML58RaisedViewWeight() > 0;
 }
 float ML85RaisedPositionWeight()
 {
  float ordinaryWeight = ML58RaisedViewWeight();
  if (ordinaryWeight <= 0)
   return 0;
  if (m_MLADSLeanAmount < 0)
   return Math.Clamp(m_MLADSLeanGate, 0, 1);
  return ordinaryWeight;
 }

 // Camera-only readback. Never writes animation controls or player input.
 float MLADSLeanFirstPersonRollTarget(bool sightCamera)
 {
  if (!MLADSLeanSettings.Enabled || !m_MLADSLeanBound || !IsAlive() || IsUnconscious())
   return 0;
  if (!IsRaised() || m_MLADSLeanGate < 0.001)
   return 0;
  EntityAI rollWeapon = GetHumanInventory().GetEntityInHands();
  if (!MLADSLeanWeaponSupport106.Supported(rollWeapon))
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
  Print("[MLPOSE104] STATIC_LEFT_FRAME15_REFERENCE_BEGIN");
  MLADSLeanCapturePose();
  Print("[MLPOSE104] STATIC_LEFT_FRAME15_REFERENCE_COMPLETE");
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
  Print("[MLPOSE104] STATIC_RIGHT_REFERENCE_BEGIN");
  MLADSLeanCapturePose();
  Print("[MLPOSE104] STATIC_RIGHT_REFERENCE_COMPLETE");
 }

 // Read-only F9 snapshot of the currently evaluated skeleton; no graph or input writes.
 protected void MLADSLeanCapturePose()
 {
  if (!MLADSLeanSettings.DetailedDiagnostics)
   return;
  string captureId = GetGame().GetTime().ToString();
  captureId += "_" + m_MLADSLeanDemo;
  string header = "[MLPOSE104] BEGIN id=" + captureId;
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
   string actorLine = "[MLPOSE104] ACTOR id=" + captureId;
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
    string boneLine = "[MLPOSE104] BONE id=" + captureId;
    boneLine += " name=" + captureBone;
    boneLine += " row=" + boneRow;
    boneLine += " value=" + boneTM[boneRow];
    Print(boneLine);
   }
  }
  EntityAI capturedWeapon = GetHumanInventory().GetEntityInHands();
  if (capturedWeapon)
  {
   Print("[MLPOSE104] WEAPON_TYPE id=" + captureId + " name=" + capturedWeapon.GetType());
   vector weaponTM[4];
   capturedWeapon.GetTransform(weaponTM);
   for (int weaponRow = 0; weaponRow < 4; weaponRow++)
   {
    string weaponLine = "[MLPOSE104] WEAPON id=" + captureId;
    weaponLine += " row=" + weaponRow;
    weaponLine += " value=" + weaponTM[weaponRow];
    Print(weaponLine);
   }
  }
  string captureEnd = "[MLPOSE104] END id=" + captureId;
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
  Print("[MLADSLEAN104] demo=" + m_MLADSLeanDemo + " joints=" + label + " interior_deg=" + angle + " first_ms=" + a + " middle_ms=" + b + " last_ms=" + c);
 }


};
