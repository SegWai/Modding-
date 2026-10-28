modded class MissionGameplay
{
 override void OnUpdate(float timeslice)
 {
  super.OnUpdate(timeslice);
  if (GetGame().IsMultiplayer() || GetGame().GetUIManager().GetMenu())
   return;
  UAInput shoulder = GetUApi().GetInputByName("UAMLAShoulderSwap");
  if (shoulder && shoulder.LocalPress())
  {
   MLAShoulderSettings.LeftRequested = !MLAShoulderSettings.LeftRequested;
   Print("[MLASHOULDER] left_requested=" + MLAShoulderSettings.LeftRequested);
  }
 }
};
