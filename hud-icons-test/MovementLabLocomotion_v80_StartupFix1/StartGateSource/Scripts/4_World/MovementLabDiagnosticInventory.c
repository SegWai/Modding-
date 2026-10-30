// DayZDiag compiles inventory diagnostic calls even when IsDebug() is false.
// Keep the native diagnostic plugin registered for this offline test.
modded class PluginManager
{
    override protected void RegisterPluginDebug(string plugin_class_name, bool reg_on_client, bool reg_on_server)
    {
#ifdef DIAG_DEVELOPER
        bool requiredOfflinePlugin = plugin_class_name == "PluginInventoryDebug";
        requiredOfflinePlugin = requiredOfflinePlugin || plugin_class_name == "PluginConfigDebugProfile";
        requiredOfflinePlugin = requiredOfflinePlugin || plugin_class_name == "PluginConfigDebugProfileFixed";
        if (requiredOfflinePlugin && !GetGame().IsMultiplayer())
        {
            RegisterPlugin(plugin_class_name, reg_on_client, reg_on_server, true);
            return;
        }
#endif
        super.RegisterPluginDebug(plugin_class_name, reg_on_client, reg_on_server);
    }
}
