// Temporary navigation inside either editor. Balance only this menu's focus;
// never reset global game focus or change camera/player simulation state.
class ML152PanelNavigation
{
 protected UIScriptedMenu m_Menu;
 protected bool m_Active;
 protected bool m_Registered;
 protected ref array<string> m_LookExcludes = {"movement", "aiming"};
 protected ref array<string> m_WeaponExcludes = {"UATempRaiseWeapon", "UAFire"};
 void Show(UIScriptedMenu menu)
 {
  m_Menu = menu;
  m_Active = false;
  GetGame().GetMission().AddActiveInputExcludes(m_WeaponExcludes);
  m_Registered = true;
 }
 bool IsActive()
 {
  return m_Active;
 }
 void Begin()
 {
  if (m_Active || !m_Menu || !GetGame().IsAppActive())
   return;
  GetGame().GetMission().AddActiveInputExcludes(m_WeaponExcludes);
  GetGame().GetMission().RemoveActiveInputExcludes(m_LookExcludes);
  // Inverse of this same menu's normal OnShow/LockControls, one time only.
  m_Menu.UnlockControls();
  SetFocus(m_Menu.GetLayoutRoot());
  m_Active = true;
 }
 void End()
 {
  if (!m_Active || !m_Menu)
   return;
  // Restore the menu lock before base OnHide, if the menu is closing.
  m_Menu.LockControls();
  GetGame().GetMission().AddActiveInputExcludes(m_LookExcludes);
  m_Active = false;
 }
 void Tick()
 {
  if (!m_Menu || !GetGame())
   return;
  if (!GetGame().IsAppActive())
  {
   End();
   return;
  }
  // Poll physical button state: release may arrive outside the UI while
  // game input owns the cursor, so OnMouseButtonUp alone is insufficient.
  int state = GetMouseState(MouseState.RIGHT);
  bool held = (state & 0x80000000) != 0;
  if (held)
   Begin();
  else
   End();
 }
 void Hide()
 {
  End();
  if (m_Registered && GetGame() && GetGame().GetMission())
   GetGame().GetMission().RemoveActiveInputExcludes(m_WeaponExcludes);
  m_Registered = false;
  m_Menu = null;
 }
};
