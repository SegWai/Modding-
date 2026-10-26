modded class MissionGameplay
{
 protected bool m_MLADSPoseRecording = true; // Record the requested clip automatically once per test launch.
 protected float m_MLADSPoseStable;
 protected float m_MLADSPoseElapsed;
 protected float m_MLADSClipInterval;
 protected int m_MLADSClipFrames;
 protected int m_MLADSClipLastTime;
 protected string m_MLADSClipSession;
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
  if (key == KeyCode.KC_F5 && !m_MLADSLeanF5Down)
  {
   m_MLADSLeanF5Down = true;
   MLADSLeanSettings.WeaponShoulderOffset = !MLADSLeanSettings.WeaponShoulderOffset;
   Print("[MLADSLEAN46] shoulder_offset=" + MLADSLeanSettings.WeaponShoulderOffset);
   if (MLADSLeanSettings.WeaponShoulderOffset)
    NotificationSystem.AddNotificationExtended(5, "Lean v46", "Leftward lean: reference arm-and-hand pose ON.");
   else
    NotificationSystem.AddNotificationExtended(5, "Lean v46", "Leftward lean: reference arm-and-hand pose OFF.");
  }
  if (key == KeyCode.KC_F6 && !m_MLADSLeanF6Down)
  {
   m_MLADSLeanF6Down = true;
   MLADSLeanSettings.HeadCorrection = !MLADSLeanSettings.HeadCorrection;
   Print("[MLADSLEAN46] head_tilt_suppression=" + MLADSLeanSettings.HeadCorrection);
   if (MLADSLeanSettings.HeadCorrection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v46", "Custom lean head: automatic ADS head tilt OFF.");
   else
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v46", "Head comparison: automatic ADS head tilt ON.");
  }
  if (key == KeyCode.KC_F9 && !m_MLADSLeanF9Down)
  {
   m_MLADSLeanF9Down = true;
   m_MLADSPoseRecording = true;
   m_MLADSPoseStable = 0;
   m_MLADSPoseElapsed = 0;
   m_MLADSClipInterval = 0;
   m_MLADSClipFrames = 0;
   m_MLADSClipLastTime = 0;
   m_MLADSClipSession = "";
   NotificationSystem.AddNotificationExtended(8, "Left walking clip", "Recording NPC character-left walking lean automatically. Let the NPC patrol.");
   Print("[MLADSLEAN46] requested_status " + MLADSLeanSettings.Status);
   string cameraReport = "[MLCAM46] last_fp_camera=" + MLADSLeanSettings.FirstPersonRollCamera;
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
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v46", "NPC patrol pause toggled. Its aim/lean are retained while paused.");
   }
  }
  if (key == KeyCode.KC_F7 && !m_MLADSLeanF7Down)
  {
   m_MLADSLeanF7Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(6, "Mosin lean v46", "Custom graph unavailable. Press F9, collect logs.");
    return;
   }
   MLADSLeanSettings.Enabled = !MLADSLeanSettings.Enabled;
   Print("[MLADSLEAN46] comparison_custom=" + MLADSLeanSettings.Enabled);
   if (MLADSLeanSettings.Enabled)
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v46", "Custom lean ON. Q/E in ADS while standing, walking or crouching.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v46", "Native lean comparison ON.");
  }
  if (key == KeyCode.KC_F8 && !m_MLADSLeanF8Down)
  {
   m_MLADSLeanF8Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(6, "Mosin lean v46", "Custom graph unavailable. Press F9 and collect logs.");
    return;
   }
   MLADSLeanSettings.Inspection = !MLADSLeanSettings.Inspection;
   Print("[MLADSLEAN46] inspection=" + MLADSLeanSettings.Inspection);
   if (MLADSLeanSettings.Inspection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v46", "Custom raised-weapon pose ON in first and third person.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v46", "Custom raised-weapon pose OFF. Custom ADS pose remains enabled.");
  }
 }
 override void OnUpdate(float timeslice)
 {
  super.OnUpdate(timeslice);
  if (!m_MLADSPoseRecording || GetGame().IsMultiplayer())
   return;
  m_MLADSPoseElapsed += timeslice;
  if (m_MLADSPoseElapsed > 60)
  {
   m_MLADSPoseRecording = false;
   NotificationSystem.AddNotificationExtended(8, "Left walking clip", "Timed out. NPC must patrol at walk pace with custom lean ON. Press F9 to retry.");
   return;
  }
  PlayerBase clipActor = MLADSLeanSettings.DemoActor;
  if (!clipActor || !clipActor.MLADSLeanLeftWalkCaptureReady())
  {
   // Never join different directions or different patrol passes into one clip.
   m_MLADSPoseStable = 0;
   m_MLADSClipInterval = 0;
   m_MLADSClipFrames = 0;
   m_MLADSClipSession = "";
   return;
  }
  m_MLADSPoseStable += timeslice;
  if (m_MLADSPoseStable < 0.4)
   return;
  int now = GetGame().GetTime();
  if (m_MLADSClipFrames > 0 && now - m_MLADSClipLastTime > 250)
  {
   m_MLADSClipFrames = 0;
   m_MLADSClipSession = "";
   m_MLADSClipInterval = 0;
  }
  m_MLADSClipInterval += timeslice;
  if (m_MLADSClipFrames > 0 && m_MLADSClipInterval < 0.041666667)
   return;
  m_MLADSClipInterval = Math.Max(0, m_MLADSClipInterval - 0.041666667);
  if (m_MLADSClipFrames == 0)
   m_MLADSClipSession = now.ToString();
  clipActor.MLADSLeanExportLeftWalkFrame(m_MLADSClipSession, m_MLADSClipFrames);
  m_MLADSClipLastTime = now;
  m_MLADSClipFrames++;
  if (m_MLADSClipFrames >= 36)
  {
   string complete = "[MLWALK46] COMPLETE session=" + m_MLADSClipSession;
   complete += " frames=" + m_MLADSClipFrames;
   complete += " nominal_fps=24";
   Print(complete);
   m_MLADSPoseRecording = false;
   NotificationSystem.AddNotificationExtended(10, "Left walk clip captured", "Close DayZ. Run Build-Left-Walk-Blender.cmd, or Collect-Logs.cmd and send the ZIP.");
  }
 }
 override void OnKeyRelease(int key)
 {
  super.OnKeyRelease(key);
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
