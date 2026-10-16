MovementLab v70 - roll back v69 camera regression

Restores the v68 scripts and animation workspace exactly. Removes v69 HeadingModel observation, persistent absolute world-yaw hold, per-command world-yaw accumulation and pitch promotion. The v68 native movement handoff and camera compensation are restored. All movement/stance/loadout features and the working DayZ 1.30 animation workspace are retained.

This is a regression rollback to the last user-tested build reported as improved. The remaining v68 camera movement is not fixed by this rollback. Further diagnosis needs the failed v69 logs and matching video, since native camera playback is not available here.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Source scripts and workspace bytes were checked against v68. PBO and ZIP integrity checked. Native in-game playback remains untested in this environment.
