CROUCH WHEEL TEST V3 - V1 BASE, ORDERED DOWNSHIFT

Close DayZ, extract whole ZIP to a fresh folder, keep Steam running and run Launch-Movement-Test.cmd. Original local assets are read only.

Built from working wheel v1. Upward wheel selection and native Shift behavior remain unchanged. Downward scrolling sets a target; actual selection steps down one adjacent level at a time. Native level5 first eases gait3->1 over .22s before selecting level4; subsequent levels each take .12s. Full5->1 about .58s plus frame rounding; 3->1 about .24s. Rapid downward scroll retargets without restarting the current stage. Idle/standing selects target immediately.

Uses v1 integer animation-group selection, not v2 continuous cross-group selection. Existing stable strafe/standing behavior retained. Native visual behavior requires in-game testing; controller tests verify ordered levels/timing and v1 upward behavior. Working v1 remains unchanged.
