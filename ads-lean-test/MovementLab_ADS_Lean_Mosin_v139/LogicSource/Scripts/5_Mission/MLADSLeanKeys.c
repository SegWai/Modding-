modded class MissionGameplay
{
 protected bool m_ML136LeftCtrl;
 protected bool m_ML136RightCtrl;
 protected bool m_ML136F8Down;
 protected bool m_ML136XDown;
 override void OnKeyPress(int key)
 {
  if (GetGame().IsMultiplayer())
  {
   super.OnKeyPress(key);
   return;
  }
  if (key == KeyCode.KC_LCONTROL)
   m_ML136LeftCtrl = true;
  if (key == KeyCode.KC_RCONTROL)
   m_ML136RightCtrl = true;
  if (GetGame().GetUIManager().GetMenu())
  {
   super.OnKeyPress(key);
   return;
  }
  if (key == KeyCode.KC_X)
  {
   if (!m_ML136XDown)
   {
    m_ML136XDown = true;
    // Reserve X for freeze without also crouching on its native binding.
    UAInput crouch = GetUApi().GetInputByName("UACrouch");
    if (crouch)
     crouch.Supress();
#ifdef DIAG_DEVELOPER
    MLFreeze135.Request();
#endif
   }
   return;
  }
  if (key == KeyCode.KC_F8 && (m_ML136LeftCtrl || m_ML136RightCtrl))
  {
   if (!m_ML136F8Down && MLADSLeanSettings.ArmDropControlBound)
   {
    MLADSLeanSettings.ArmDropTest = !MLADSLeanSettings.ArmDropTest;
    MLADSLeanSettings.ElbowReadyNoticeShown = false;
   }
   m_ML136F8Down = true;
   return;
  }
  super.OnKeyPress(key);
 }
 override void OnKeyRelease(int key)
 {
  if (key == KeyCode.KC_LCONTROL)
   m_ML136LeftCtrl = false;
  if (key == KeyCode.KC_RCONTROL)
   m_ML136RightCtrl = false;
  if (key == KeyCode.KC_F8)
   m_ML136F8Down = false;
  if (key == KeyCode.KC_X)
   m_ML136XDown = false;
  super.OnKeyRelease(key);
 }
};
