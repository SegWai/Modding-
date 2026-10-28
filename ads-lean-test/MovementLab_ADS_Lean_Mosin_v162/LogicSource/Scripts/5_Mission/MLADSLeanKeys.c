modded class MissionGameplay
{
 override UIScriptedMenu CreateScriptedMenu(int id)
 {
  if (id == 86149)
   return new ML149Menu;
  if (id == 86144)
   return new ML144Menu;
  return super.CreateScriptedMenu(id);
 }

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
  if (key == KeyCode.KC_F7)
  {
   if (!ML149State.KeyDown)
   {
    ML149State.KeyDown = true;
    UIScriptedMenu active = GetGame().GetUIManager().GetMenu();
    ML149Menu body = ML149Menu.Cast(active);
    ML144Menu weapon = ML144Menu.Cast(active);
    if (body)
     body.Close();
    else if (weapon)
    {
     weapon.Close();
     GetGame().GetUIManager().EnterScriptedMenu(86149, null);
    }
    else if (!active)
     GetGame().GetUIManager().EnterScriptedMenu(86149, null);
   }
   return;
  }
  if (key == KeyCode.KC_F6)
  {
   if (!ML144State.KeyDown)
   {
    ML144State.KeyDown = true;
    UIScriptedMenu currentMenu = GetGame().GetUIManager().GetMenu();
    ML144Menu editor = ML144Menu.Cast(currentMenu);
    if (editor)
     editor.Close();
    else if (ML149Menu.Cast(currentMenu))
    {
     currentMenu.Close();
     GetGame().GetUIManager().EnterScriptedMenu(86144, null);
    }
    else if (!currentMenu)
     GetGame().GetUIManager().EnterScriptedMenu(86144, null);
   }
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
  if (key == KeyCode.KC_F7)
   ML149State.KeyDown = false;
  if (key == KeyCode.KC_F6)
   ML144State.KeyDown = false;
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
