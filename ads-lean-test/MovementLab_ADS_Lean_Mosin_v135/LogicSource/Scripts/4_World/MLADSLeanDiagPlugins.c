// Public DayZDiag builds can compile DIAG_DEVELOPER inventory calls while
// IsDebug() is false, causing the stock RegisterPluginDebug calls to skip
// the very plugin those calls dereference. Register the stock defaults for
// this offline test; do not change the native inventory implementation.
modded class PluginManager
{
 override void Init()
 {
  super.Init();
#ifdef DIAG_DEVELOPER
  if (!GetGame().IsMultiplayer() && !GetGame().IsDebug())
  {
   RegisterPlugin("PluginInventoryDebug", true, true);
   RegisterPlugin("PluginConfigDebugProfile", true, true);
   Print("[MLADSLEAN104] Registered offline DayZDiag inventory/profile debug dependencies.");
  }
#endif
 }
};

#ifdef DIAG_DEVELOPER
// Keep native Alt+E and its menu entry, but execute the simulation change from
// the next system queue turn instead of inside the diagnostic input callback.
class MLFreeze135
{
 static PlayerBase PendingPlayer;
 static bool Pending;
 static void Request()
 {
  if (!GetGame() || GetGame().IsMultiplayer() || Pending)
   return;
  PendingPlayer = PlayerBase.Cast(GetGame().GetPlayer());
  if (!PendingPlayer || !PendingPlayer.IsAlive())
   return;
  Pending = true;
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(Apply, 1, false);
  Print("[MLFREEZE135] queued");
 }
 static void Apply()
 {
  PlayerBase target = PendingPlayer;
  PendingPlayer = null;
  Pending = false;
  if (!GetGame() || GetGame().IsMultiplayer() || !target || !target.IsAlive())
   return;
  if (GetGame().GetPlayer() != target)
   return;
  bool disabled = !target.GetIsSimulationDisabled();
  Print("[MLFREEZE135] applying disabled=" + disabled);
  target.DisableSimulation(disabled);
  Print("[MLFREEZE135] applied disabled=" + target.GetIsSimulationDisabled());
 }
};
modded class PluginDiagMenuClient
{
 override protected void BindCallbacks()
 {
  super.BindCallbacks();
  DiagMenu.BindCallback(DiagMenuIDs.MISC_FREEZE_PLAYER, ML135FreezeCallback);
  Print("[MLFREEZE135] Alt+E callback installed");
 }
 static void ML135FreezeCallback(bool enabled, int id)
 {
  if (GetGame().IsMultiplayer())
  {
   CBMiscFreezePlayer(enabled, id);
   return;
  }
  if (enabled)
  {
   DiagMenu.SetValue(id, false);
   MLFreeze135.Request();
  }
 }
};
#endif
