class ML149Menu extends UIScriptedMenu
{
 protected ref array<SliderWidget> m_Sliders = new array<SliderWidget>;
 protected ref array<TextWidget> m_Readouts = new array<TextWidget>;
 protected TextWidget m_Title;
 protected XComboBoxWidget m_Part;
 protected TextWidget m_Status;
 protected bool m_Refreshing;
 protected bool m_Excluded;
 protected ref ML152PanelNavigation m_Navigation;
 protected ref array<string> m_Excludes = {"movement", "aiming", "gestures", "stances", "optics", "actions", "hotkey", "UAGear"};
 override int GetID()
 {
  return 86149;
 }
 override Widget Init()
 {
  ML207Preset.Init();
  layoutRoot = GetGame().GetWorkspace().CreateWidgets("MLADSLeanLogic/GUI/MLBodyEditor149.layout");
  if (!layoutRoot)
   return null;
  m_Title = TextWidget.Cast(layoutRoot.FindAnyWidget("Title"));
  m_Part = XComboBoxWidget.Cast(layoutRoot.FindAnyWidget("Part"));
  if (m_Part)
  {
   foreach (string label : ML207BodyState.Labels)
    m_Part.AddItem(label);
  }
  m_Status = TextWidget.Cast(layoutRoot.FindAnyWidget("Status"));
  for (int i = 0; i < 6; i++)
  {
   SliderWidget slider = SliderWidget.Cast(layoutRoot.FindAnyWidget("Value" + i));
   TextWidget readout = TextWidget.Cast(layoutRoot.FindAnyWidget("Readout" + i));
   if (!slider || !readout)
    return layoutRoot;
   float limit = 15;
   if (i >= 3)
    limit = 45;
   slider.SetMinMax(-limit, limit);
   slider.SetStep(0.1);
   m_Sliders.Insert(slider);
   m_Readouts.Insert(readout);
  }
  RefreshValues();
  return layoutRoot;
 }
 override void OnShow()
 {
  super.OnShow();
  ML207BodyState.Open = true;
  ML207WeaponState.HoldRight = true;
  ML207WeaponState.Open = true;
  GetGame().GetMission().AddActiveInputExcludes(m_Excludes);
  m_Excluded = true;
  m_Navigation = new ML152PanelNavigation;
  m_Navigation.Show(this);
 }
 override void OnHide()
 {
  if (m_Navigation)
   m_Navigation.Hide();
  ML207BodyState.Open = false;
  ML207WeaponState.Open = false;
  if (m_Excluded)
  {
   if (GetGame() && GetGame().GetMission())
    GetGame().GetMission().RemoveActiveInputExcludes(m_Excludes);
   m_Excluded = false;
  }
  super.OnHide();
 }
 protected void RefreshValues()
 {
  if (m_Sliders.Count() != 6)
   return;
  ML149Data data = ML207BodyState.Current();
  if (!data)
   return;
  ML149Part part = data.Parts[ML207BodyState.SelectedPart];
  array<float> values = {part.X, part.Y, part.Z, part.Pitch, part.Yaw, part.Roll};
  m_Refreshing = true;
  for (int i = 0; i < 6; i++)
  {
   m_Sliders[i].SetCurrent(values[i]);
   m_Readouts[i].SetText(values[i].ToString());
  }
  if (m_Title)
  {
   if (ML207WeaponState.EditLeft)
    m_Title.SetText("SMG WALKING POSE BODY - LEFT");
   else
    m_Title.SetText("SMG WALKING POSE BODY - RIGHT");
  }
  if (m_Part)
   m_Part.SetCurrentItem(ML207BodyState.SelectedPart);
  m_Refreshing = false;
 }
 protected void ApplySliders()
 {
  if (m_Refreshing || m_Sliders.Count() != 6)
   return;
  ML149Part part = new ML149Part;
  part.BoneName = ML207BodyState.Bones[ML207BodyState.SelectedPart];
  part.X = Math.Round(m_Sliders[0].GetCurrent()*10)*0.1;
  part.Y = Math.Round(m_Sliders[1].GetCurrent()*10)*0.1;
  part.Z = Math.Round(m_Sliders[2].GetCurrent()*10)*0.1;
  part.Pitch = Math.Round(m_Sliders[3].GetCurrent()*10)*0.1;
  part.Yaw = Math.Round(m_Sliders[4].GetCurrent()*10)*0.1;
  part.Roll = Math.Round(m_Sliders[5].GetCurrent()*10)*0.1;
  ML207BodyState.Apply(part);
  RefreshValues();
 }
 override bool OnChange(Widget w, int x, int y, bool finished)
 {
  if (m_Navigation && m_Navigation.IsActive())
   return true;
  if (w == m_Part)
  {
   if (!m_Refreshing)
   {
    int selected = m_Part.GetCurrentItem();
    if (selected >= 0 && selected < ML207BodyState.Bones.Count() && selected != ML207BodyState.SelectedPart)
    {
     ML207BodyState.SelectedPart = selected;
     RefreshValues();
    }
   }
   return true;
  }
  if (SliderWidget.Cast(w))
  {
   ApplySliders();
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
  if (name == "Close")
  {
   Close();
   return true;
  }
  if (name == "LeftSide" || name == "RightSide")
   ML207WeaponState.SelectSide(name == "LeftSide");
  else if (name == "Previous")
  {
   ML207BodyState.SelectedPart--;
   if (ML207BodyState.SelectedPart < 0)
   {
    int partCount = ML207BodyState.Bones.Count();
    ML207BodyState.SelectedPart = partCount - 1;
   }
  }
  else if (name == "Next")
  {
   ML207BodyState.SelectedPart++;
   if (ML207BodyState.SelectedPart >= ML207BodyState.Bones.Count())
    ML207BodyState.SelectedPart = 0;
  }
  else if (name == "ResetPart")
   ML207BodyState.ResetPart();
  else if (name == "ResetSide")
   ML207BodyState.ResetSide();
  else if (name == "Save")
   ML207BodyState.Save();
  else if (name == "Load")
   ML207BodyState.Load();
  else
  {
   for (int i = 0; i < 6; i++)
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
  if (key == KeyCode.KC_F6)
  {
   if (!ML207WeaponState.KeyDown)
   {
    ML207WeaponState.KeyDown = true;
    Close();
    GetGame().GetUIManager().EnterScriptedMenu(86144, null);
   }
   return true;
  }
  if (key == KeyCode.KC_F7)
  {
   if (!ML207BodyState.KeyDown)
   {
    ML207BodyState.KeyDown = true;
    Close();
   }
   return true;
  }
  if (key == KeyCode.KC_ESCAPE)
  {
   Close();
   return true;
  }
  return super.OnKeyPress(w, x, y, key);
 }
 override bool OnKeyUp(Widget w, int x, int y, int key)
 {
  if (key == KeyCode.KC_F6)
   ML207WeaponState.KeyDown = false;
  if (key == KeyCode.KC_F7)
   ML207BodyState.KeyDown = false;
  return super.OnKeyUp(w, x, y, key);
 }
 override void Update(float timeslice)
 {
  if (m_Navigation)
   m_Navigation.Tick();
  super.Update(timeslice);
  if (m_Status)
  {
   if (!ML207BodyState.Bound)
    m_Status.SetText("Waiting for body graph binding...");
   else
    m_Status.SetText(ML207BodyState.Status);
  }
 }
};
