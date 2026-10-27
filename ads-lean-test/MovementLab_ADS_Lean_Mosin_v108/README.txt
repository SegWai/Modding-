V108 elbow adjustment: left support elbow pole target is 45 degrees from vertical down toward the torso, during own-left raised walking lean. Existing fixed-wrist swivel and wrist counter-rotation retained. Right elbow, AJ loadout, camera and animation workspace unchanged from user-confirmed working v107. Actual elbow angle is constrained by the fixed hand position and arm reach; native appearance requires verification.

V108 — AJs Weapons loadout, custom category animations retained

Required Workshop mod: AJs Weapons, https://steamcommunity.com/sharedfiles/filedetails/?id=3571685323 . Subscribe/download through Steam before launching. The launcher checks that exact Workshop folder, then named AJ folders, and asks for its path only if necessary. It loads AJ plus our two lean packages. No Panacea package or player loadout is loaded.

Player loadout: up to four different AJ firearm models selected from the installed public CfgWeapons definitions. The selector prefers a shouldered gun, an SMG, a handgun and a precision rifle where identifiable, then fills missing choices with other distinct AJ guns. Category identification for loadout variety is best-effort; the actual class names always come from the game. Newer AJ versions do not need a manually hardcoded class list. Guns that reuse a vanilla DZ model are not selected by this loadout scanner.

Before equipping, the selector rejects generic script fallback classes, requires a running native weapon state machine, and requires successful ammunition loading. Compatible attachments are chosen from the installed attachment-slot definitions, preferring mod parts and then vanilla parts. Extra magazines, backpack and startup hands-slot verification remain. Quickbar 1–4 contains the resulting AJ guns; exact names are written to MLAJ107 logs. Maximum twelve spawn attempts. No previous player weapons are spawned. NPC keeps AK74 for pose comparisons.

The v106 animation workspace and camera are unchanged: shouldered firearms share custom body/arm lean; pistols and revolvers share the custom body lean while retaining their native handgun grip. Ctrl+F8 remains available. A working weapon mod still needs its own native weapon scripts, firing states and hand profiles.

Extract the full ZIP; run Launch-Mosin-Lean-Test.cmd. After testing aiming, firing and switching, run Collect-Logs.cmd and send its ZIP if there is a problem. Native Windows compilation and AJ gameplay have not been run here. Package/source checks do not establish that every AJ grip is visually correct.

Default game folder D:\SteamLibrary\steamapps\common\DayZ. Project root F:\DayZProjects. Earlier versions remain separate rollback ZIPs. Workshop files are not redistributed.
