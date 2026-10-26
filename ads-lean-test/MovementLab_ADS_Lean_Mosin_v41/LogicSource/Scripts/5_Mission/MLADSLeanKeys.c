modded class MissionGameplay
{
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
   Print("[MLADSLEAN41] shoulder_offset=" + MLADSLeanSettings.WeaponShoulderOffset);
   if (MLADSLeanSettings.WeaponShoulderOffset)
    NotificationSystem.AddNotificationExtended(5, "Lean v41", "Leftward lean: reference arm-and-hand pose ON.");
   else
    NotificationSystem.AddNotificationExtended(5, "Lean v41", "Leftward lean: reference arm-and-hand pose OFF.");
  }
  if (key == KeyCode.KC_F6 && !m_MLADSLeanF6Down)
  {
   m_MLADSLeanF6Down = true;
   MLADSLeanSettings.HeadCorrection = !MLADSLeanSettings.HeadCorrection;
   Print("[MLADSLEAN41] head_tilt_suppression=" + MLADSLeanSettings.HeadCorrection);
   if (MLADSLeanSettings.HeadCorrection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v41", "Custom lean head: automatic ADS head tilt OFF.");
   else
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v41", "Head comparison: automatic ADS head tilt ON.");
  }
  if (key == KeyCode.KC_F9 && !m_MLADSLeanF9Down)
  {
   m_MLADSLeanF9Down = true;
   NotificationSystem.AddNotificationExtended(8, "Mosin lean v41 status", MLADSLeanSettings.Status);
   Print("[MLADSLEAN41] requested_status " + MLADSLeanSettings.Status);
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
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v41", "NPC patrol pause toggled. Its aim/lean are retained while paused.");
   }
  }
  if (key == KeyCode.KC_F7 && !m_MLADSLeanF7Down)
  {
   m_MLADSLeanF7Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(6, "Mosin lean v41", "Custom graph unavailable. Press F9, collect logs.");
    return;
   }
   MLADSLeanSettings.Enabled = !MLADSLeanSettings.Enabled;
   Print("[MLADSLEAN41] comparison_custom=" + MLADSLeanSettings.Enabled);
   if (MLADSLeanSettings.Enabled)
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v41", "Custom lean ON. Q/E in ADS while standing, walking or crouching.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v41", "Native lean comparison ON.");
  }
  if (key == KeyCode.KC_F8 && !m_MLADSLeanF8Down)
  {
   m_MLADSLeanF8Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(6, "Mosin lean v41", "Custom graph unavailable. Press F9 and collect logs.");
    return;
   }
   MLADSLeanSettings.Inspection = !MLADSLeanSettings.Inspection;
   Print("[MLADSLEAN41] inspection=" + MLADSLeanSettings.Inspection);
   if (MLADSLeanSettings.Inspection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v41", "Custom raised-weapon pose ON in first and third person.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v41", "Custom raised-weapon pose OFF. Custom ADS pose remains enabled.");
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
