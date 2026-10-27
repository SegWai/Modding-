V106: custom lean support uses the actual firearm and its native class ancestry, rather than an AK74/Mosin allowlist. Modded subclasses participate automatically.

Shouldered guns (assault rifles, SMGs, snipers, shotguns and other firearms) use the shared custom body/arm lean with the currently held weapon's native IK input. Handguns/revolvers use the shared custom torso/head/legs and aim, retaining their own native hand grip; rifle arm and stock corrections are zeroed for them. Empty hands, tools and bows do not enter the custom gun path. The player and NPC use the same classifier and graph.

MLWEAPON106 logs actual held class, chosen handling profile, control binding and native weapon-command availability. A weapon mod must still supply working native hand/reload/firing profiles. The reported Panacea fists/switching issue has not yet been isolated or confirmed fixed; category support is not a replacement for those profiles. Native Windows compilation and per-weapon visual validation are pending.

Panacea remains required for this range loadout: https://steamcommunity.com/sharedfiles/filedetails/?id=2389010221 . Subscribe/download through Steam first. Launcher finds the Workshop folder or asks for its path. Workshop files are not included. Quickbar: 1 SCAR-H, 2 Honey Badger, 3 AWM, 4 Origin-12. Backpack and startup hands-slot check retained. NPC keeps AK74 for pose comparison. Ctrl+F8 compares arm adjustments.

Extract the full ZIP and run Launch-Mosin-Lean-Test.cmd. Use Collect-Logs.cmd after testing. Default game folder D:\SteamLibrary\steamapps\common\DayZ; project root F:\DayZProjects. Earlier ZIPs remain separate rollback copies.
