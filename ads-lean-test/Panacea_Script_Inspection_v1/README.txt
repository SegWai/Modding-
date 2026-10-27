Panacea script inspection

Extract and run Inspect-Panacea.cmd, then send the ZIP it creates. No game test is needed.

The isolated handling logs show SCAR-H falling back to generic Rifle_Base and AWM falling back to generic BoltActionRifle_Base, with weapon state-machine errors. This inspection checks whether the installed Panacea package contains the expected weapon script files and script-module definitions. It reads PBO headers, script paths and uncompressed script-module config definitions only; it does not extract models/textures or modify the mod. Packed or protected config/script data may require further inspection.

Default folder comes from your launcher log: D:\SteamLibrary\steamapps\workshop\content\221100\2389010221 . The output contains local folder path, PBO names/sizes, script-related entry names, PBO prefix properties, mod.cpp/meta.cpp and any readable script-module config definitions. Your custom animation package is unchanged.
