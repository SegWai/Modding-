// Only the retained arm comparison and the requested mimic recorder keys.
// No distance-calibration prompts, notifications, or other test toggles.
modded class MissionGameplay
{
 protected bool m_ML114LeftCtrl;
 protected bool m_ML114RightCtrl;
 protected bool m_ML114LeftShift;
 protected bool m_ML114RightShift;
 protected bool m_ML114F8Down;
 protected bool m_ML114LDown;
 protected bool m_ML114LConsumed;
 protected bool m_ML114LReset;
 protected bool m_ML114ColonDown;
 protected float m_ML114LHold;
 override void OnKeyPress(int key)
 {
  if (GetGame().IsMultiplayer())
  {
   super.OnKeyPress(key);
   return;
  }
  if (key == KeyCode.KC_LCONTROL)
   m_ML114LeftCtrl = true;
  if (key == KeyCode.KC_RCONTROL)
   m_ML114RightCtrl = true;
  if (key == KeyCode.KC_LSHIFT)
   m_ML114LeftShift = true;
  if (key == KeyCode.KC_RSHIFT)
   m_ML114RightShift = true;
  if (GetGame().GetUIManager().GetMenu())
  {
   super.OnKeyPress(key);
   return;
  }
  if (key == KeyCode.KC_F8 && (m_ML114LeftCtrl || m_ML114RightCtrl))
  {
   if (!m_ML114F8Down && MLADSLeanSettings.ArmDropControlBound)
   {
    MLADSLeanSettings.ArmDropTest = !MLADSLeanSettings.ArmDropTest;
    MLADSLeanSettings.ElbowReadyNoticeShown = false;
    Print("[MLDROP114] toggle_on=" + MLADSLeanSettings.ArmDropTest);
   }
   m_ML114F8Down = true;
   return;
  }
  if (key == KeyCode.KC_L)
  {
   if (!m_ML114LDown)
   {
    m_ML114LDown = true;
    m_ML114LHold = 0;
    m_ML114LConsumed = false;
    m_ML114LReset = false;
    if (MLADSLeanSettings.Mimic && MLADSLeanSettings.Mimic.Playing)
    {
     MLADSLeanSettings.Mimic.StopPlayback();
     m_ML114LConsumed = true;
    }
   }
   return;
  }
  bool colon = key == KeyCode.KC_COLON || key == KeyCode.KC_SEMICOLON;
  // Portuguese keyboards type ':' with Shift+period; US uses Shift+semicolon.
  colon = colon || (key == KeyCode.KC_PERIOD && (m_ML114LeftShift || m_ML114RightShift));
  if (colon)
  {
   if (!m_ML114ColonDown && MLADSLeanSettings.Mimic)
    MLADSLeanSettings.Mimic.StartPlayback();
   m_ML114ColonDown = true;
   return;
  }
  super.OnKeyPress(key);
 }
 override void OnKeyRelease(int key)
 {
  if (GetGame().IsMultiplayer())
  {
   super.OnKeyRelease(key);
   return;
  }
  if (key == KeyCode.KC_LCONTROL)
   m_ML114LeftCtrl = false;
  if (key == KeyCode.KC_RCONTROL)
   m_ML114RightCtrl = false;
  if (key == KeyCode.KC_LSHIFT)
   m_ML114LeftShift = false;
  if (key == KeyCode.KC_RSHIFT)
   m_ML114RightShift = false;
  if (key == KeyCode.KC_F8)
   m_ML114F8Down = false;
  if (key == KeyCode.KC_L)
  {
   bool tap = m_ML114LDown && !m_ML114LConsumed;
   m_ML114LDown = false;
   if (tap && !GetGame().IsMultiplayer() && !GetGame().GetUIManager().GetMenu() && MLADSLeanSettings.Mimic)
    MLADSLeanSettings.Mimic.ToggleRecording();
   return;
  }
  if (key == KeyCode.KC_COLON || key == KeyCode.KC_SEMICOLON || key == KeyCode.KC_PERIOD)
   m_ML114ColonDown = false;
  super.OnKeyRelease(key);
 }
 override void OnUpdate(float timeslice)
 {
  super.OnUpdate(timeslice);
  if (GetGame().IsMultiplayer())
   return;
  if (m_ML114LDown)
  {
   if (GetGame().GetUIManager().GetMenu())
   {
    m_ML114LDown = false;
    m_ML114LConsumed = true;
   }
   else
   {
    m_ML114LHold += Math.Max(0, timeslice);
    if (!m_ML114LReset && m_ML114LHold >= 0.75 && MLADSLeanSettings.Mimic)
    {
     MLADSLeanSettings.Mimic.Reset();
     m_ML114LConsumed = true;
     m_ML114LReset = true;
    }
   }
  }
  if (MLADSLeanSettings.Mimic)
   MLADSLeanSettings.Mimic.Tick(timeslice);
 }
};
