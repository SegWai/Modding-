class ML144Menu extends UIScriptedMenu
{
 protected ref array<SliderWidget> m_Sliders = new array<SliderWidget>;
 protected ref array<TextWidget> m_Readouts = new array<TextWidget>;
 protected TextWidget m_Status;
 protected bool m_Refreshing;
 protected bool m_Excluded;
 protected ref array<string> m_Excludes = {"movement", "aiming", "gestures", "stances", "optics", "actions", "hotkey", "UAGear"};
 override Widget Init()
 {
  ML144State.Init();
  layoutRoot = GetGame().GetWorkspace().CreateWidgets("MLADSLeanLogic/GUI/MLPoseEditor144.layout");
  if (!layoutRoot)
   return null;
  for (int row = 0; row < 6; row++)
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
   else
    slider.SetMinMax(-20, 20);
   slider.SetStep(0.1);
   m_Sliders.Insert(slider);
   m_Readouts.Insert(readout);
  }
  m_Status = TextWidget.Cast(layoutRoot.FindAnyWidget("Status"));
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
  ML144State.Open = true;
  GetGame().GetMission().AddActiveInputExcludes(m_Excludes);
  m_Excluded = true;
 }
 override void OnHide()
 {
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
  if (!ML144State.Values || m_Sliders.Count() != 6)
   return;
  m_Refreshing = true;
  ML144Values value = ML144State.Values;
  array<float> numbers = {value.X, value.Y, value.Z, value.Pitch, value.Yaw, value.Roll};
  for (int i = 0; i < 6; i++)
  {
   m_Sliders[i].SetCurrent(numbers[i]);
   m_Readouts[i].SetText(numbers[i].ToString());
  }
  ButtonWidget hold = ButtonWidget.Cast(layoutRoot.FindAnyWidget("Hold"));
  if (hold)
  {
   if (ML144State.HoldRight)
    hold.SetText("Hold right lean: ON");
   else
    hold.SetText("Hold right lean: OFF");
  }
  m_Refreshing = false;
 }
 protected void ApplySliders()
 {
  if (m_Refreshing || m_Sliders.Count() != 6)
   return;
  ML144Values candidate = new ML144Values;
  candidate.X = Math.Round(m_Sliders[0].GetCurrent()*10)*0.1;
  candidate.Y = Math.Round(m_Sliders[1].GetCurrent()*10)*0.1;
  candidate.Z = Math.Round(m_Sliders[2].GetCurrent()*10)*0.1;
  candidate.Pitch = Math.Round(m_Sliders[3].GetCurrent()*10)*0.1;
  candidate.Yaw = Math.Round(m_Sliders[4].GetCurrent()*10)*0.1;
  candidate.Roll = Math.Round(m_Sliders[5].GetCurrent()*10)*0.1;
  ML144State.Apply(candidate);
  RefreshValues();
 }
 override bool OnChange(Widget w, int x, int y, bool finished)
 {
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
  if (name == "Reset")
   ML144State.Reset();
  else if (name == "Save")
   ML144State.Save();
  else if (name == "Load")
   ML144State.Load();
  else if (name == "Hold")
  {
   ML144State.HoldRight = !ML144State.HoldRight;
   ButtonWidget holdButton = ButtonWidget.Cast(w);
   if (ML144State.HoldRight)
    holdButton.SetText("Hold right lean: ON");
   else
    holdButton.SetText("Hold right lean: OFF");
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
  if (key == KeyCode.KC_ESCAPE)
  {
   Close();
   return true;
  }
  if (key == KeyCode.KC_F6)
  {
   if (!ML144State.KeyDown)
   {
    ML144State.KeyDown = true;
    Close();
   }
   return true;
  }
  return super.OnKeyPress(w, x, y, key);
 }
 override bool OnKeyUp(Widget w, int x, int y, int key)
 {
  if (key == KeyCode.KC_F6)
   ML144State.KeyDown = false;
  return super.OnKeyUp(w, x, y, key);
 }
 override void Update(float timeslice)
 {
  super.Update(timeslice);
  if (m_Status)
  {
   if (!ML144State.Bound)
    m_Status.SetText("Waiting for live graph binding; check logs if unchanged.");
   else
    m_Status.SetText(ML144State.Status);
  }
 }
};
