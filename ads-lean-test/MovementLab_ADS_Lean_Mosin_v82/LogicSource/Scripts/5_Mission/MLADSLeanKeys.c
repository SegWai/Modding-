modded class MissionGameplay
{
 protected bool m_ML49Active = true;
 protected bool m_ML49Done[3];
 protected int m_ML49Count;
 protected int m_ML49State = 9;
 protected int m_ML49Samples;
 protected float m_ML49Stable;
 protected float m_ML49Interval;
 protected float m_ML49Elapsed;
 protected float m_ML49HeadMin;
 protected float m_ML49HeadMax;
 protected vector m_ML49Sum[7];
 protected vector m_ML49RootSum;
 protected int m_ML49FirstSampleTime;
 protected string m_ML49Setup;
 protected string m_ML49Session;
 protected bool m_ML71ControlDown;
 protected bool m_MLADSLeanF5Down;
 protected bool m_MLADSLeanF6Down;
 protected bool m_MLADSLeanF7Down;
 protected bool m_MLADSLeanF8Down;
 protected bool m_MLADSLeanF9Down;
 protected bool m_MLADSLeanF10Down;
 override void OnKeyPress(int key)
 {
  super.OnKeyPress(key);
  if (GetGame().IsMultiplayer())
   return;
  if (key == KeyCode.KC_LCONTROL || key == KeyCode.KC_RCONTROL)
   m_ML71ControlDown = true;
  if (key == KeyCode.KC_F9 && m_ML71ControlDown && !m_MLADSLeanF9Down)
  {
   m_MLADSLeanF9Down = true;
   MLADSLeanSettings.PostPoseSupportGrip = !MLADSLeanSettings.PostPoseSupportGrip;
   string comparison = "Post-pose support grip OFF: v70 comparison";
   if (MLADSLeanSettings.PostPoseSupportGrip)
    comparison = "Post-pose support grip ON";
   NotificationSystem.AddNotificationExtended(5, "Grip comparison", comparison);
   Print("[MLADSLEAN82] post_pose_support=" + MLADSLeanSettings.PostPoseSupportGrip);
   return;
  }
  if (key == KeyCode.KC_F5 && !m_MLADSLeanF5Down)
  {
   m_MLADSLeanF5Down = true;
   MLADSLeanSettings.WeaponShoulderOffset = !MLADSLeanSettings.WeaponShoulderOffset;
   Print("[MLADSLEAN82] shoulder_offset=" + MLADSLeanSettings.WeaponShoulderOffset);
   if (MLADSLeanSettings.WeaponShoulderOffset)
    NotificationSystem.AddNotificationExtended(5, "Lean v82", "Leftward lean: reference arm-and-hand pose ON.");
   else
    NotificationSystem.AddNotificationExtended(5, "Lean v82", "Leftward lean: reference arm-and-hand pose OFF.");
  }
  if (key == KeyCode.KC_F6 && !m_MLADSLeanF6Down)
  {
   m_MLADSLeanF6Down = true;
   MLADSLeanSettings.HeadCorrection = !MLADSLeanSettings.HeadCorrection;
   Print("[MLADSLEAN82] head_tilt_suppression=" + MLADSLeanSettings.HeadCorrection);
   if (MLADSLeanSettings.HeadCorrection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v82", "Custom lean head: automatic ADS head tilt OFF.");
   else
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v82", "Head comparison: automatic ADS head tilt ON.");
  }
  if (key == KeyCode.KC_F9 && !m_MLADSLeanF9Down)
  {
   m_MLADSLeanF9Down = true;
   ML49RestartDistance();
   NotificationSystem.AddNotificationExtended(8, "Standing lean v82", "Calibration restarted. Stand still with gun raised: neutral, Q, E, about 3 seconds each.");
   Print("[MLADSLEAN82] requested_status " + MLADSLeanSettings.Status);
   string cameraReport = "[MLCAM82] last_fp_camera=" + MLADSLeanSettings.FirstPersonRollCamera;
   cameraReport += " last_applied_roll_deg=" + MLADSLeanSettings.FirstPersonRoll;
   Print(cameraReport);
   if (MLADSLeanSettings.DemoActor)
    MLADSLeanSettings.DemoActor.MLADSLeanReportJoints();
   PlayerBase measuredPlayer = PlayerBase.Cast(GetGame().GetPlayer());
   if (measuredPlayer)
    measuredPlayer.MLADSLeanReportJoints();
  }
  if (key == KeyCode.KC_F10 && !m_MLADSLeanF10Down)
  {
   m_MLADSLeanF10Down = true;
   if (MLADSLeanSettings.DemoActor)
   {
    MLADSLeanSettings.DemoActor.MLADSLeanToggleDemoPause();
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v82", "NPC patrol pause toggled. Its aim/lean are retained while paused.");
   }
  }
  if (key == KeyCode.KC_F7 && !m_MLADSLeanF7Down)
  {
   m_MLADSLeanF7Down = true;
   NotificationSystem.AddNotificationExtended(4, "Custom leaning", "Custom aiming leans are permanent in this build. Use the v82 backup to compare.");
  }
  if (key == KeyCode.KC_F8 && !m_MLADSLeanF8Down)
  {
   m_MLADSLeanF8Down = true;
   NotificationSystem.AddNotificationExtended(4, "Custom leaning", "Custom raised poses remain enabled in both views.");
  }
 }
 protected void ML49ResetWindow()
 {
  m_ML49Samples = 0;
  m_ML49RootSum = vector.Zero;
  m_ML49Stable = 0;
  m_ML49Interval = 0;
  for (int i = 0; i < 7; i++)
   m_ML49Sum[i] = vector.Zero;
 }
 protected void ML49RestartDistance()
 {
  m_ML49Active = true;
  m_ML49Count = 0;
  m_ML49State = 9;
  m_ML49Elapsed = 0;
  m_ML49Setup = "";
  m_ML49Session = "";
  for (int i = 0; i < 3; i++)
   m_ML49Done[i] = false;
  ML49ResetWindow();
 }
 override void OnUpdate(float timeslice)
 {
  super.OnUpdate(timeslice);
  if (!m_ML49Active || GetGame().IsMultiplayer())
   return;
  PlayerBase measuredPlayer = PlayerBase.Cast(GetGame().GetPlayer());
  if (!measuredPlayer)
   return;
  m_ML49Elapsed += timeslice;
  if (m_ML49Elapsed > 180)
  {
   m_ML49Active = false;
   NotificationSystem.AddNotificationExtended(10, "Lean distance calibration", "Timed out. Press F9 to restart. Keep standing, gun raised: neutral, Q, E.");
   return;
  }
  if (timeslice > 0.25)
  {
   ML49ResetWindow();
   return;
  }
  int state = measuredPlayer.ML49DistanceState();
  if (state == 9)
  {
   m_ML49State = 9;
   ML49ResetWindow();
   return;
  }
  string setup = measuredPlayer.ML49DistanceSetup();
  if (m_ML49Setup == "")
  {
   m_ML49Setup = setup;
   m_ML49Session = GetGame().GetTime().ToString();
   string begin = "[MLDIST82] SESSION id=" + m_ML49Session;
   begin += " setup=" + setup;
   begin += " native_workspace=" + MLADSLeanSettings.DistanceNativeReference;
   Print(begin);
   NotificationSystem.AddNotificationExtended(8, "Lean distance calibration", "Keep this weapon and aiming mode. Hold neutral, Q and E about 3 seconds each.");
  }
  if (setup != m_ML49Setup || m_ML49Done[state + 1])
  {
   ML49ResetWindow();
   return;
  }
  if (state != m_ML49State)
  {
   ML49ResetWindow();
   m_ML49State = state;
  }
  m_ML49Stable += Math.Clamp(timeslice, 0, 0.1);
  if (m_ML49Stable < 0.5)
   return;
  m_ML49Interval += timeslice;
  if (m_ML49Interval < 0.05)
   return;
  m_ML49Interval = Math.Max(0, m_ML49Interval - 0.05);
  vector points[7];
  if (!measuredPlayer.ML49DistancePoints(points))
  {
   ML49ResetWindow();
   return;
  }
  if (m_ML49Samples == 0)
  {
   m_ML49FirstSampleTime = GetGame().GetTime();
   m_ML49HeadMin = points[0][0];
   m_ML49HeadMax = points[0][0];
  }
  m_ML49HeadMin = Math.Min(m_ML49HeadMin, points[0][0]);
  m_ML49HeadMax = Math.Max(m_ML49HeadMax, points[0][0]);
  for (int i = 0; i < 7; i++)
   m_ML49Sum[i] = m_ML49Sum[i] + points[i];
  m_ML49RootSum = m_ML49RootSum + measuredPlayer.GetPosition();
  m_ML49Samples++;
  if (m_ML49Samples < 20)
   return;
  float inverseSamples = 1.0 / m_ML49Samples;
  vector head = m_ML49Sum[0] * inverseSamples;
  vector chest = m_ML49Sum[1] * inverseSamples;
  vector pelvis = m_ML49Sum[2] * inverseSamples;
  vector leftFoot = m_ML49Sum[3] * inverseSamples;
  vector rightFoot = m_ML49Sum[4] * inverseSamples;
  vector eyeCentre = (m_ML49Sum[5] + m_ML49Sum[6]) * (0.5 * inverseSamples);
  vector rootWorld = m_ML49RootSum * inverseSamples;
  vector actorAngles = measuredPlayer.GetOrientation();
  int sampleDuration = GetGame().GetTime() - m_ML49FirstSampleTime;
  string mode = "custom";
  if (MLADSLeanSettings.DistanceNativeReference)
   mode = "native";
  string result = "[MLDIST82] RESULT session=" + m_ML49Session;
  result += " mode=" + mode;
  result += " setup=" + setup;
  result += " sign=" + state;
  result += " samples=" + m_ML49Samples;
  result += " duration_ms=" + sampleDuration;
  result += " root_ws=" + rootWorld;
  result += " actor_ypr=" + actorAngles;
  result += " head_ms=" + head;
  result += " chest_ms=" + chest;
  result += " pelvis_ms=" + pelvis;
  result += " left_foot_ms=" + leftFoot;
  result += " right_foot_ms=" + rightFoot;
  result += " eye_centre_ms=" + eyeCentre;
  result += " head_x_min=" + m_ML49HeadMin;
  result += " head_x_max=" + m_ML49HeadMax;
  Print(result);
  string marker = "[MLDIST82] POSE_FOLLOWS session=" + m_ML49Session;
  marker += " mode=" + mode;
  marker += " sign=" + state;
  Print(marker);
  measuredPlayer.ML49DistanceFullPose();
  m_ML49Done[state + 1] = true;
  m_ML49Count++;
  float reachCm = Math.Round(Math.AbsFloat(head[0] - measuredPlayer.ML55NeutralAimingHeadX()) * 1000) * 0.1;
  string notice = mode + " neutral reference recorded";
  if (state < 0)
   notice = mode + " LEFT head travel from neutral: " + reachCm + " cm";
  if (state > 0)
   notice = mode + " RIGHT head travel from neutral: " + reachCm + " cm";
  notice += " (" + m_ML49Count + "/3)";
  NotificationSystem.AddNotificationExtended(6, "Lean distance calibration", notice);
  ML49ResetWindow();
  if (m_ML49Count == 3)
  {
   m_ML49Active = false;
   Print("[MLDIST82] COMPLETE mode=" + mode + " session=" + m_ML49Session);
   NotificationSystem.AddNotificationExtended(12, "Lean distances captured", "Pose measurements saved. Close DayZ and use Collect-Logs.cmd if you want to send the result.");
  }
 }
 override void OnKeyRelease(int key)
 {
  super.OnKeyRelease(key);
  if (key == KeyCode.KC_LCONTROL || key == KeyCode.KC_RCONTROL)
   m_ML71ControlDown = false;
  if (key == KeyCode.KC_F5)
   m_MLADSLeanF5Down = false;
  if (key == KeyCode.KC_F6)
   m_MLADSLeanF6Down = false;
  if (key == KeyCode.KC_F7)
   m_MLADSLeanF7Down = false;
  if (key == KeyCode.KC_F8)
   m_MLADSLeanF8Down = false;
  if (key == KeyCode.KC_F9)
   m_MLADSLeanF9Down = false;
  if (key == KeyCode.KC_F10)
   m_MLADSLeanF10Down = false;
 }
};
