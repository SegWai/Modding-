modded class MissionGameplay
{
 protected bool m_MLADSLeanF7Down;
 protected bool m_MLADSLeanF8Down;

 override void OnKeyPress(int key)
 {
  super.OnKeyPress(key);
  if (GetGame().IsMultiplayer())
   return;
  if (key == KeyCode.KC_F7 && !m_MLADSLeanF7Down)
  {
   m_MLADSLeanF7Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(4, "Mosin lean", "Native baseline: the custom workspace is not loaded.");
    return;
   }
   MLADSLeanSettings.Enabled = !MLADSLeanSettings.Enabled;
   Print("[MLADSLEAN1] comparison_custom=" + MLADSLeanSettings.Enabled);
   if (MLADSLeanSettings.Enabled)
    NotificationSystem.AddNotificationExtended(4, "Mosin lean", "Custom lean enabled. Q/E while standing still in ADS.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean", "Native lean comparison enabled.");
  }
  if (key == KeyCode.KC_F8 && !m_MLADSLeanF8Down)
  {
   m_MLADSLeanF8Down = true;
   if (!MLADSLeanSettings.HasGraph)
   {
    NotificationSystem.AddNotificationExtended(4, "Mosin lean", "Native baseline: custom inspection is unavailable.");
    return;
   }
   MLADSLeanSettings.Inspection = !MLADSLeanSettings.Inspection;
   Print("[MLADSLEAN1] inspection=" + MLADSLeanSettings.Inspection);
   if (MLADSLeanSettings.Inspection)
    NotificationSystem.AddNotificationExtended(5, "Mosin lean", "Third-person inspection ON. Raise Mosin and hold Q/E. Not an ADS alignment test.");
   else
    NotificationSystem.AddNotificationExtended(4, "Mosin lean", "Inspection OFF. Custom pose is ADS-only again.");
  }
 }
 override void OnKeyRelease(int key)
 {
  super.OnKeyRelease(key);
  if (key == KeyCode.KC_F7)
   m_MLADSLeanF7Down = false;
  if (key == KeyCode.KC_F8)
   m_MLADSLeanF8Down = false;
 }
};
