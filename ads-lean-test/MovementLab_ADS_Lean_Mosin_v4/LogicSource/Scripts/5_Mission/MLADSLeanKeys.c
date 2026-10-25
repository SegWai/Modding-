modded class MissionGameplay
{
 protected bool m_MLADSLeanF7Down;
 protected bool m_MLADSLeanF8Down;
 protected bool m_MLADSLeanF9Down;
 override void OnKeyPress(int key)
 {
  super.OnKeyPress(key);
  if (GetGame().IsMultiplayer())
   return;
  if (key == KeyCode.KC_F9 && !m_MLADSLeanF9Down)
  {
   m_MLADSLeanF9Down = true;
   NotificationSystem.AddNotificationExtended(8, "Mosin lean v4 status", MLADSLeanSettings.Status);
   Print("[MLADSLEAN4] requested_status " + MLADSLeanSettings.Status);
   PlayerBase measuredPlayer = PlayerBase.Cast(GetGame().GetPlayer());
   if (measuredPlayer)
    measuredPlayer.MLADSLeanReportJoints();
  }
  if (key == KeyCode.KC_F7 && !m_MLADSLeanF7Down)
  {
   m_MLADSLeanF7Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(6, "Mosin lean v4", "Custom graph unavailable. Press F9, collect logs. Baseline mode has no custom graph.");
    return;
   }
   MLADSLeanSettings.Enabled = !MLADSLeanSettings.Enabled;
   Print("[MLADSLEAN4] comparison_custom=" + MLADSLeanSettings.Enabled);
   if (MLADSLeanSettings.Enabled)
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v4", "Custom lean ON. Q/E while standing still in ADS.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v4", "Native lean comparison ON.");
  }
  if (key == KeyCode.KC_F8 && !m_MLADSLeanF8Down)
  {
   m_MLADSLeanF8Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(6, "Mosin lean v4", "Custom graph unavailable. Press F9 and collect logs.");
    return;
   }
   MLADSLeanSettings.Inspection = !MLADSLeanSettings.Inspection;
   Print("[MLADSLEAN4] inspection=" + MLADSLeanSettings.Inspection);
   if (MLADSLeanSettings.Inspection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean v4", "Third-person inspection ON. Raise Mosin and hold Q/E. Not an ADS alignment test.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean v4", "Inspection OFF. Custom pose is ADS-only again.");
  }
 }
 override void OnKeyRelease(int key)
 {
  super.OnKeyRelease(key);
  if (key == KeyCode.KC_F7)
   m_MLADSLeanF7Down = false;
  if (key == KeyCode.KC_F8)
   m_MLADSLeanF8Down = false;
  if (key == KeyCode.KC_F9)
   m_MLADSLeanF9Down = false;
 }
};
