All Locomotion Pose Smoothing v1 — separate test from CONFIRMED PoseExit v2 default.
Default source/package preserved unchanged. Extract entire ZIP, close DayZ, launch.
Coverage: walk/jog/sprint pose changes in both directions, walking and jog wheel
profiles, all slow crouch levels and fast exit to lower levels, left/right strafe
pose reversals, forward/back transition blends, stand/crouch/prone posture handoffs,
movement start/stop pose handoffs. Native clips stay forward, no freezing.
Input rules, speed levels, gait requests, acceleration/braking timers untouched.
Stance clips/tags/foot-phase conditions kept; their pose crossfade windows extended.
Known nativefast->87 exit retained; exit to lower tiers holds87 profile while
fast pose fades, then blends lower walking profiles. Crouch default60% unchanged.
Direct lateral blend avoids interpolating through forward-walk poses on A/D.
No new UI messages or F8 toggle. F7 still compares input filters; some graph
transition windows remain modified, so load default package for exact baseline.
Native compilation/animation/physical motion/phase require in-game confirmation.
Any pose blend can affect native root motion; actual speed/feet need checking.
This does not modify unrelated combat/actions/vehicle animations.
If a regression appears, run Collect-Logs.cmd and send generated ZIP.
