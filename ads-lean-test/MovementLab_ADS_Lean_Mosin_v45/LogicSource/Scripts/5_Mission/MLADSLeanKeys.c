modded class MissionGameplay
{
 protected bool m_MLADSPoseRecording;
 protected float m_MLADSPoseStable;
 protected float m_MLADSPoseElapsed;
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
   Print("[MLADSLEAN45] shoulder_offset=" + MLADSLeanSettings.WeaponShoulderOffset);
   if (MLADSLeanSettings.WeaponShoulderOffset)
    NotificationSystem.AddNotificationExtended(5, "Lean v45", "Leftward lean: reference arm-and-hand pose ON.");
   else
    NotificationSystem.AddNotificationExtended(5, "Lean v45", "Leftward lean: reference arm-and-hand pose OFF.");
  }
  if (key == KeyCode.KC_F6 && !m_MLADSLeanF6Down)
  {
   m_MLADSLeanF6Down = true;
   MLADSLeanSettings.HeadCorrection = !MLADSLeanSettings.HeadCorrection;
   Print("[MLADSLEAN45] head_tilt_suppression=" + MLADSLeanSettings.HeadCorrection);
   if (MLADSLeanSettings.HeadCorrection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v45", "Custom lean head: automatic ADS head tilt OFF.");
   else
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v45", "Head comparison: automatic ADS head tilt ON.");
  }
  if (key == KeyCode.KC_F9 && !m_MLADSLeanF9Down)
  {
   m_MLADSLeanF9Down = true;
   m_MLADSPoseRecording = true;
   m_MLADSPoseStable = 0;
   m_MLADSPoseElapsed = 0;
   NotificationSystem.AddNotificationExtended(8, "Pose capture v44", "Hold your gun raised, stand still, and lean to YOUR RIGHT. Recording that reference only.");
   Print("[MLADSLEAN45] requested_status " + MLADSLeanSettings.Status);
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
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v45", "NPC patrol pause toggled. Its aim/lean are retained while paused.");
   }
  }
  if (key == KeyCode.KC_F7 && !m_MLADSLeanF7Down)
  {
   m_MLADSLeanF7Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(6, "Mosin lean v45", "Custom graph unavailable. Press F9, collect logs.");
    return;
   }
   MLADSLeanSettings.Enabled = !MLADSLeanSettings.Enabled;
   Print("[MLADSLEAN45] comparison_custom=" + MLADSLeanSettings.Enabled);
   if (MLADSLeanSettings.Enabled)
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v45", "Custom lean ON. Q/E in ADS while standing, walking or crouching.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v45", "Native lean comparison ON.");
  }
  if (key == KeyCode.KC_F8 && !m_MLADSLeanF8Down)
  {
   m_MLADSLeanF8Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(6, "Mosin lean v45", "Custom graph unavailable. Press F9 and collect logs.");
    return;
   }
   MLADSLeanSettings.Inspection = !MLADSLeanSettings.Inspection;
   Print("[MLADSLEAN45] inspection=" + MLADSLeanSettings.Inspection);
   if (MLADSLeanSettings.Inspection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v45", "Custom raised-weapon pose ON in first and third person.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v45", "Custom raised-weapon pose OFF. Custom ADS pose remains enabled.");
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
   NotificationSystem.AddNotificationExtended(8, "Standing right pose", "Timed out. Press F9 again, raise your weapon, stand still and lean to YOUR RIGHT.");
   return;
  }
  PlayerBase capturePlayer = PlayerBase.Cast(GetGame().GetPlayer());
  if (!capturePlayer || !capturePlayer.MLADSLeanStaticReferenceReady())
  {
   m_MLADSPoseStable = 0;
   return;
  }
  m_MLADSPoseStable += timeslice;
  if (m_MLADSPoseStable < 0.5)
   return;
  capturePlayer.MLADSLeanExportStaticReference();
  m_MLADSPoseRecording = false;
  NotificationSystem.AddNotificationExtended(10, "Standing right pose captured", "Close DayZ, run Collect-Logs.cmd and send the ZIP. Standing right pose logged.");
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
