V112: during anatomical left standing raised walking lean, move the weapon hold and both hands 5cm toward the character's own RIGHT (+model X). Uses the existing arm rotation path before final grip IK, preserving hand orientations and reference limb lengths. Same Ctrl+F8 comparison scope (ON applies new hold; OFF original baseline); own-right hold, first-person, crouch, body/head/legs, AJ loadout, CF and elbow target angles retained. Captured-reference math passed; actual native weapon displacement/hand contact need in-game verification.

V112 elbow targets for own-left raised walking lean: RIGHT elbow 45 degrees from vertical down/outward; LEFT elbow 20 degrees from vertical down/outward. Both horizontal directions point away from the torso. Fixed hand positions constrain the achieved elbow angles. Original scope/shared NPC-player path, AJ loadout, CF-before-AJ launcher, camera and animation workspace retained. Native appearance pending.

V112 launcher dependency fix: AJs Weapons requires Community Framework (CF), Workshop item 1559212036: https://steamcommunity.com/sharedfiles/filedetails/?id=1559212036 . Install/download CF through Steam. The launcher detects its Workshop folder or @CF folder, then loads CF before AJ and the lean packages. It asks for the CF folder only if automatic detection fails. All PBOs, elbow targets, camera and AJ loadout are byte-identical to v109.

V112 elbow correction: left support elbow pole target is 45 degrees from vertical down, OUTWARD away from the torso during own-left raised walking lean. This reverses only the horizontal component of the v108 target. Right elbow, AJ weapons, camera and animation workspace retained. Fixed hand position constrains the actual visible angle; native verification pending.

V112 — AJs Weapons loadout, custom category animations retained

Required Workshop mod: AJs Weapons, https://steamcommunity.com/sharedfiles/filedetails/?id=3571685323 . Subscribe/download through Steam before launching. The launcher checks that exact Workshop folder, then named AJ folders, and asks for its path only if necessary. It loads AJ plus our two lean packages. No Panacea package or player loadout is loaded.

Player loadout: up to four different AJ firearm models selected from the installed public CfgWeapons definitions. The selector prefers a shouldered gun, an SMG, a handgun and a precision rifle where identifiable, then fills missing choices with other distinct AJ guns. Category identification for loadout variety is best-effort; the actual class names always come from the game. Newer AJ versions do not need a manually hardcoded class list. Guns that reuse a vanilla DZ model are not selected by this loadout scanner.

Before equipping, the selector rejects generic script fallback classes, requires a running native weapon state machine, and requires successful ammunition loading. Compatible attachments are chosen from the installed attachment-slot definitions, preferring mod parts and then vanilla parts. Extra magazines, backpack and startup hands-slot verification remain. Quickbar 1–4 contains the resulting AJ guns; exact names are written to MLAJ107 logs. Maximum twelve spawn attempts. No previous player weapons are spawned. NPC keeps AK74 for pose comparisons.

The v106 animation workspace and camera are unchanged: shouldered firearms share custom body/arm lean; pistols and revolvers share the custom body lean while retaining their native handgun grip. Ctrl+F8 remains available. A working weapon mod still needs its own native weapon scripts, firing states and hand profiles.

Extract the full ZIP; run Launch-Mosin-Lean-Test.cmd. After testing aiming, firing and switching, run Collect-Logs.cmd and send its ZIP if there is a problem. Native Windows compilation and AJ gameplay have not been run here. Package/source checks do not establish that every AJ grip is visually correct.

Default game folder D:\SteamLibrary\steamapps\common\DayZ. Project root F:\DayZProjects. Earlier versions remain separate rollback ZIPs. Workshop files are not redistributed.
