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
