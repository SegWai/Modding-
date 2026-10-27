class ML149Menu extends UIScriptedMenu
{
 protected ref array<SliderWidget> m_Sliders = new array<SliderWidget>;
 protected ref array<TextWidget> m_Readouts = new array<TextWidget>;
 protected TextWidget m_Title;
 protected XComboBoxWidget m_Part;
 protected TextWidget m_Status;
 protected bool m_Refreshing;
 protected bool m_Excluded;
 protected ref array<string> m_Excludes = {"movement", "aiming", "gestures", "stances", "optics", "actions", "hotkey", "UAGear"};
 override int GetID()
 {
  return 86149;
 }
 override Widget Init()
 {
  ML144State.Init();
  ML149State.Init();
  layoutRoot = GetGame().GetWorkspace().CreateWidgets("MLADSLeanLogic/GUI/MLBodyEditor149.layout");
  if (!layoutRoot)
   return null;
  m_Title = TextWidget.Cast(layoutRoot.FindAnyWidget("Title"));
  m_Part = XComboBoxWidget.Cast(layoutRoot.FindAnyWidget("Part"));
  if (m_Part)
  {
   foreach (string label : ML149State.Labels)
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
  ML149State.Open = true;
  ML144State.HoldRight = true;
  ML144State.Open = true;
  GetGame().GetMission().AddActiveInputExcludes(m_Excludes);
  m_Excluded = true;
 }
 override void OnHide()
 {
  ML149State.Open = false;
  ML144State.Open = false;
  if (m_Excluded)
  {
   GetGame().GetMission().RemoveActiveInputExcludes(m_Excludes);
   m_Excluded = false;
  }
  super.OnHide();
 }
 protected void RefreshValues()
 {
  if (m_Sliders.Count() != 6)
   return;
  ML149Data data = ML149State.Current();
  if (!data)
   return;
  ML149Part part = data.Parts[ML149State.SelectedPart];
  array<float> values = {part.X, part.Y, part.Z, part.Pitch, part.Yaw, part.Roll};
  m_Refreshing = true;
  for (int i = 0; i < 6; i++)
  {
   m_Sliders[i].SetCurrent(values[i]);
   m_Readouts[i].SetText(values[i].ToString());
  }
  if (m_Title)
  {
   if (ML144State.EditLeft)
    m_Title.SetText("BODY - STANDING LEFT");
   else
    m_Title.SetText("BODY - STANDING RIGHT");
  }
  if (m_Part)
   m_Part.SetCurrentItem(ML149State.SelectedPart);
  m_Refreshing = false;
 }
 protected void ApplySliders()
 {
  if (m_Refreshing || m_Sliders.Count() != 6)
   return;
  ML149Part part = new ML149Part;
  part.BoneName = ML149State.Bones[ML149State.SelectedPart];
  part.X = Math.Round(m_Sliders[0].GetCurrent()*10)*0.1;
  part.Y = Math.Round(m_Sliders[1].GetCurrent()*10)*0.1;
  part.Z = Math.Round(m_Sliders[2].GetCurrent()*10)*0.1;
  part.Pitch = Math.Round(m_Sliders[3].GetCurrent()*10)*0.1;
  part.Yaw = Math.Round(m_Sliders[4].GetCurrent()*10)*0.1;
  part.Roll = Math.Round(m_Sliders[5].GetCurrent()*10)*0.1;
  ML149State.Apply(part);
  RefreshValues();
 }
 override bool OnChange(Widget w, int x, int y, bool finished)
 {
  if (w == m_Part)
  {
   if (!m_Refreshing)
   {
    int selected = m_Part.GetCurrentItem();
    if (selected >= 0 && selected < ML149State.Bones.Count() && selected != ML149State.SelectedPart)
    {
     ML149State.SelectedPart = selected;
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
  string name = w.GetName();
  if (name == "Close")
  {
   Close();
   return true;
  }
  if (name == "LeftSide" || name == "RightSide")
   ML144State.SelectSide(name == "LeftSide");
  else if (name == "Previous")
  {
   ML149State.SelectedPart--;
   if (ML149State.SelectedPart < 0)
    ML149State.SelectedPart = ML149State.Bones.Count()-1;
  }
  else if (name == "Next")
  {
   ML149State.SelectedPart++;
   if (ML149State.SelectedPart >= ML149State.Bones.Count())
    ML149State.SelectedPart = 0;
  }
  else if (name == "ResetPart")
   ML149State.ResetPart();
  else if (name == "ResetSide")
   ML149State.ResetSide();
  else if (name == "Save")
   ML149State.Save();
  else if (name == "Load")
   ML149State.Load();
  else
  {
   for (int i = 0; i < 6; i++)
   {
    float step = 0.5;
    if (i >= 3)
     step = 1;
    if (name == "Minus" + i)
    {
     m_Sliders[i].SetCurrent(m_Sliders[i].GetCurrent()-step);
     ApplySliders();
     return true;
    }
    if (name == "Plus" + i)
    {
     m_Sliders[i].SetCurrent(m_Sliders[i].GetCurrent()+step);
     ApplySliders();
     return true;
    }
   }
   return super.OnClick(w, x, y, button);
  }
  RefreshValues();
  return true;
 }
 override bool OnKeyPress(Widget w, int x, int y, int key)
 {
  if (key == KeyCode.KC_F6)
  {
   if (!ML144State.KeyDown)
   {
    ML144State.KeyDown = true;
    Close();
    GetGame().GetUIManager().EnterScriptedMenu(86144, null);
   }
   return true;
  }
  if (key == KeyCode.KC_F7)
  {
   if (!ML149State.KeyDown)
   {
    ML149State.KeyDown = true;
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
   ML144State.KeyDown = false;
  if (key == KeyCode.KC_F7)
   ML149State.KeyDown = false;
  return super.OnKeyUp(w, x, y, key);
 }
 override void Update(float timeslice)
 {
  super.Update(timeslice);
  if (m_Status)
  {
   if (!ML149State.Bound)
    m_Status.SetText("Waiting for body graph binding...");
   else
    m_Status.SetText(ML149State.Status);
  }
 }
};
