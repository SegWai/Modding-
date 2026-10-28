class ML144Menu extends UIScriptedMenu
{
 protected ref array<SliderWidget> m_Sliders = new array<SliderWidget>;
 protected ref array<TextWidget> m_Readouts = new array<TextWidget>;
 protected TextWidget m_Status;
 protected bool m_Refreshing;
 protected float m_ML176Displayed[17];
 protected bool m_Excluded;
 protected ref ML152PanelNavigation m_Navigation;
 protected bool m_ArmPage;
 protected ref array<string> m_Excludes = {"movement", "aiming", "gestures", "stances", "optics", "actions", "hotkey", "UAGear"};
 override Widget Init()
 {
  ML173Preset.Init();
  layoutRoot = GetGame().GetWorkspace().CreateWidgets("MLADSLeanLogic/GUI/MLPoseEditor144.layout");
  if (!layoutRoot)
   return null;
  for (int row = 0; row < 17; row++)
  {
   SliderWidget slider = SliderWidget.Cast(layoutRoot.FindAnyWidget("Value" + row));
   TextWidget readout = TextWidget.Cast(layoutRoot.FindAnyWidget("Readout" + row));
   if (!slider || !readout)
    return layoutRoot;
   if (row == 0)
    slider.SetMinMax(-20, 20);
   else if (row == 1)
    slider.SetMinMax(-25, 15);
   else if (row == 2)
    slider.SetMinMax(-20, 25);
   else if (row < 8)
    slider.SetMinMax(-20, 20);
   else if (row < 14)
    slider.SetMinMax(-90, 90);
   else
    slider.SetMinMax(-45, 45);
   slider.SetStep(0.1);
   m_Sliders.Insert(slider);
   m_Readouts.Insert(readout);
  }
  m_Status = TextWidget.Cast(layoutRoot.FindAnyWidget("Status"));
  ShowPage(false);
  RefreshValues();
  return layoutRoot;
 }
 override int GetID()
 {
  return 86144;
 }
 override void OnShow()
 {
  super.OnShow();
  ML173WeaponState.Open = true;
  GetGame().GetMission().AddActiveInputExcludes(m_Excludes);
  m_Excluded = true;
  m_Navigation = new ML152PanelNavigation;
  m_Navigation.Show(this);
 }
 override void OnHide()
 {
  if (m_Navigation)
   m_Navigation.Hide();
  ML173WeaponState.Open = false;
  if (m_Excluded)
  {
   if (GetGame() && GetGame().GetMission())
    GetGame().GetMission().RemoveActiveInputExcludes(m_Excludes);
   m_Excluded = false;
  }
  super.OnHide();
 }
 protected void ShowPage(bool arms)
 {
  m_ArmPage = arms;
  Widget weaponPage = layoutRoot.FindAnyWidget("WeaponPage");
  Widget armPage = layoutRoot.FindAnyWidget("ArmPage");
  if (weaponPage)
   weaponPage.Show(!arms);
  if (armPage)
   armPage.Show(arms);
 }
 protected void RefreshValues()
 {
  if (!ML173WeaponState.Values || m_Sliders.Count() != 17)
   return;
  m_Refreshing = true;
  ML144Values value = ML173WeaponState.Values;
  array<float> numbers = new array<float>;
  numbers.Insert(value.X);
  numbers.Insert(value.Y);
  numbers.Insert(value.Z);
  numbers.Insert(value.Pitch);
  numbers.Insert(value.Yaw);
  numbers.Insert(value.Roll);
  numbers.Insert(value.MuzzleYaw);
  numbers.Insert(value.MuzzlePitch);
  numbers.Insert(value.LeftPitch);
  numbers.Insert(value.LeftYaw);
  numbers.Insert(value.LeftRoll);
  numbers.Insert(value.RightPitch);
  numbers.Insert(value.RightYaw);
  numbers.Insert(value.RightRoll);
  numbers.Insert(value.HeadPitch);
  numbers.Insert(value.HeadYaw);
  numbers.Insert(value.HeadRoll);
  for (int i = 0; i < 17; i++)
  {
   m_Sliders[i].SetCurrent(numbers[i]);
   m_ML176Displayed[i] = m_Sliders[i].GetCurrent();
   m_Readouts[i].SetText(numbers[i].ToString());
  }
  ButtonWidget hold = ButtonWidget.Cast(layoutRoot.FindAnyWidget("Hold"));
  if (hold)
  {
   hold.Show(false);
   if (ML173WeaponState.HoldRight)
    hold.SetText("Hold selected lean: ON");
   else
    hold.SetText("Hold selected lean: OFF");
  }
  TextWidget title = TextWidget.Cast(layoutRoot.FindAnyWidget("Title"));
  if (title)
  {
   if (ML173WeaponState.EditLeft)
    title.SetText("WALKING NPC - LEFT");
   else
    title.SetText("WALKING NPC - RIGHT");
  }
  m_Refreshing = false;
 }
 protected void ApplySliders()
 {
  if (m_Refreshing || m_Sliders.Count() != 17)
   return;
  ML144Values candidate = new ML144Values;
  candidate.X = Math.Round(m_Sliders[0].GetCurrent()*10)*0.1;
  candidate.Y = Math.Round(m_Sliders[1].GetCurrent()*10)*0.1;
  candidate.Z = Math.Round(m_Sliders[2].GetCurrent()*10)*0.1;
  candidate.Pitch = Math.Round(m_Sliders[3].GetCurrent()*10)*0.1;
  candidate.Yaw = Math.Round(m_Sliders[4].GetCurrent()*10)*0.1;
  candidate.Roll = Math.Round(m_Sliders[5].GetCurrent()*10)*0.1;
  candidate.MuzzleYaw = Math.Round(m_Sliders[6].GetCurrent()*10)*0.1;
  candidate.MuzzlePitch = Math.Round(m_Sliders[7].GetCurrent()*10)*0.1;
  candidate.LeftPitch = Math.Round(m_Sliders[8].GetCurrent()*10)*0.1;
  candidate.LeftYaw = Math.Round(m_Sliders[9].GetCurrent()*10)*0.1;
  candidate.LeftRoll = Math.Round(m_Sliders[10].GetCurrent()*10)*0.1;
  candidate.RightPitch = Math.Round(m_Sliders[11].GetCurrent()*10)*0.1;
  candidate.RightYaw = Math.Round(m_Sliders[12].GetCurrent()*10)*0.1;
  candidate.RightRoll = Math.Round(m_Sliders[13].GetCurrent()*10)*0.1;
  candidate.HeadPitch = Math.Round(m_Sliders[14].GetCurrent()*10)*0.1;
  candidate.HeadYaw = Math.Round(m_Sliders[15].GetCurrent()*10)*0.1;
  candidate.HeadRoll = Math.Round(m_Sliders[16].GetCurrent()*10)*0.1;
  ML173WeaponState.Apply(candidate);
  RefreshValues();
 }
 override bool OnChange(Widget w, int x, int y, bool finished)
 {
  if (m_Navigation && m_Navigation.IsActive())
   return true;
  if (SliderWidget.Cast(w))
  {
   if (!m_Refreshing)
   {
    for (int index = 0; index < 17; index++)
    {
     if (w == m_Sliders[index] && m_Sliders[index].GetCurrent() != m_ML176Displayed[index])
     {
      ApplySliders();
      break;
     }
    }
   }
   return true;
  }
  return super.OnChange(w, x, y, finished);
 }
 override bool OnClick(Widget w, int x, int y, int button)
 {
  if (button != MouseState.LEFT)
   return true;
  if (m_Navigation && m_Navigation.IsActive())
   return true;
  string name = w.GetName();
  if (name == "LeftSide" || name == "RightSide")
  {
   ML173WeaponState.SelectSide(name == "LeftSide");
   RefreshValues();
   return true;
  }
  if (name == "WeaponTab")
  {
   ShowPage(false);
   return true;
  }
  if (name == "ArmTab")
  {
   ShowPage(true);
   return true;
  }
  if (name == "Close")
  {
   Close();
   return true;
  }
  if (name == "Reset")
   ML173WeaponState.Reset();
  else if (name == "Save")
   ML173WeaponState.Save();
  else if (name == "Load")
   ML173WeaponState.Load();
  else if (name == "Hold")
  {
   ML173WeaponState.HoldRight = !ML173WeaponState.HoldRight;
   ButtonWidget holdButton = ButtonWidget.Cast(w);
   if (ML173WeaponState.HoldRight)
    holdButton.SetText("Hold selected lean: ON");
   else
    holdButton.SetText("Hold selected lean: OFF");
  }
  else
  {
   for (int i = 0; i < m_Sliders.Count(); i++)
   {
    float step = 0.5;
    if (i >= 3)
     step = 1;
    if (name == "Minus" + i)
    {
     float decreased = m_Sliders[i].GetCurrent();
     decreased = decreased - step;
     m_Sliders[i].SetCurrent(decreased);
     ApplySliders();
     return true;
    }
    if (name == "Plus" + i)
    {
     float increased = m_Sliders[i].GetCurrent();
     increased = increased + step;
     m_Sliders[i].SetCurrent(increased);
     ApplySliders();
     return true;
    }
   }
   return super.OnClick(w, x, y, button);
  }
  RefreshValues();
  return true;
 }
 override bool OnMouseButtonDown(Widget w, int x, int y, int button)
 {
  if (button == MouseState.RIGHT && m_Navigation)
  {
   m_Navigation.Begin();
   return true;
  }
  return super.OnMouseButtonDown(w, x, y, button);
 }
 override bool OnMouseButtonUp(Widget w, int x, int y, int button)
 {
  if (button == MouseState.RIGHT && m_Navigation)
  {
   m_Navigation.End();
   return true;
  }
  return super.OnMouseButtonUp(w, x, y, button);
 }
 override void OnVisibilityChanged(bool isVisible)
 {
  if (!isVisible && m_Navigation)
   m_Navigation.End();
  super.OnVisibilityChanged(isVisible);
 }
 override bool OnKeyPress(Widget w, int x, int y, int key)
 {
  if (key == KeyCode.KC_F7)
  {
   if (!ML173BodyState.KeyDown)
   {
    ML173BodyState.KeyDown = true;
    Close();
    GetGame().GetUIManager().EnterScriptedMenu(86149, null);
   }
   return true;
  }
  if (key == KeyCode.KC_ESCAPE)
  {
   Close();
   return true;
  }
  if (key == KeyCode.KC_F6)
  {
   if (!ML173WeaponState.KeyDown)
   {
    ML173WeaponState.KeyDown = true;
    Close();
   }
   return true;
  }
  return super.OnKeyPress(w, x, y, key);
 }
 override bool OnKeyUp(Widget w, int x, int y, int key)
 {
  if (key == KeyCode.KC_F7)
   ML173BodyState.KeyDown = false;
  if (key == KeyCode.KC_F6)
   ML173WeaponState.KeyDown = false;
  return super.OnKeyUp(w, x, y, key);
 }
 override void Update(float timeslice)
 {
  if (m_Navigation)
   m_Navigation.Tick();
  super.Update(timeslice);
  if (m_Status)
  {
   if (!ML173WeaponState.Bound)
    m_Status.SetText("Waiting for live graph binding; check logs if unchanged.");
   else if (m_ArmPage && !ML173WeaponState.ArmsReady)
    m_Status.SetText("Hold selected lean; arm reference settles briefly after weapon edits.");
   else
    m_Status.SetText(ML173WeaponState.Status);
  }
 }
};
