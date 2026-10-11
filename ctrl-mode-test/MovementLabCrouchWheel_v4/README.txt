CROUCH WHEEL TIMED POSE BLEND TEST V4 — EXPERIMENTAL

Close DayZ, keep Steam running, extract the ENTIRE ZIP into a new folder, and run Launch-Movement-Test.cmd. No Addon Builder needed. Local DZ originals must remain where v1 found them. Preparation reads originals and builds only the test folder PBOs.

Working v1 is unchanged. This test replaces wheel BlendN selection with four timed AnimNodeBlendT transitions (0.18s each), using the existing native graph node syntax and synchronization flags. Unlike rejected v2/v3, the graph itself now requests time-based pose transitions. Moving downward pace progresses at five levels per second: 5 to1 .80s, 3 to1 .40s; graph blends may continue briefly afterward. Upward wheel selection and Shift request retain immediate v1 behavior, though new graph blending can affect their appearance. Standing controls and strafe baseline are unchanged.

Test crouch forward at level5, scroll quickly down to1 while continuing to move. Repeat 3 to1, and single 4 to3. Watch for foot-contact jumps or sliding, and compare with v1. Also test back/diagonal crouch and rapid scroll retargeting. Exit and launch your original v1 folder to revert.

Verified here: translated script/controller regressions, graph source structure and source/PBO packaging. Native DayZ compilation, node flags, clip phase preservation and visual result require this in-game test. This is a distinct experiment, not a confirmed fix. Shared group-subtree behavior remains an unverified possible cause if timed blends still jump.
