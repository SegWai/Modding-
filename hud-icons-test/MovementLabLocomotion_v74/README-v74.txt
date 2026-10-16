MovementLab v74 - native head and camera controls restored

Removes the stationary head/body locking system and all later camera handoff, camera limit, head-only pose, extra head rotation and shoulder-trim experiments. This package uses the pre-head-lock v42 gameplay source, which matches v66 gameplay scripts and mission except for the removed MovementLabHeadLook90.c module. The animation speed profiles are migrated into the working DayZ 1.30 workspace format.

Native DayZ camera/head controls and body following are restored. Existing weapon sway/alignment work, movement speeds and momentum, six stance HUD icons, normal stamina and MMG/SNAFU loadout are retained. Later custom item-preview UI and quickbar experiments are not added.

Extract into a fresh folder and launch Launch-Movement-Test.cmd. Do not merge into an older version folder, since leftover head/camera scripts could still be loaded. Static graph/dependency/source and package integrity checks passed. Native DayZ compile/playback require local testing.
