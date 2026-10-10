MovementLab Ctrl Modes v9 - Ctrl jog-to-walk momentum / unchanged duration

Close DayZ, keep Steam running, extract the WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing/import needed.

NEW CHANGE:
Ctrl jog-to-walk uses smoothstep rather than front-loaded ease-out. It retains
more momentum at the start, then settles into walking within the SAME existing
transition duration. No pause, frozen frame, extra cycle or walking tail added.
Forward/side/diagonal jogging retain the 0.42s budget (scaled for achieved gait);
pure backward retains its shorter 0.18s budget. Actual physical velocity and
animation blending are native; the script changes the gait request curve.
Test: jog holding W, tap Ctrl without releasing W, then compare with v8.

The preferred responsive body rotation is enabled from startup. The old F8
comparison flag and handler have been removed; F8 has no custom movement effect.
This is the former second/F8-on setting: walk/jog heading multiplier 1.6.
Direction multiplier remains 2.5. Sprint settings are unchanged.
F7 still retains the separate whole-profile vanilla comparison.

Standing controls and the v7 crouch rules are unchanged:
- Tap Ctrl while standing to toggle walk/jog; hold Shift for standing sprint.
- Crouch without Shift: slow crouch.
- Crouch with Shift + direction: original native DayZ fast crouch.
- Stand from active fast crouch: jogging until Ctrl selects walk. Release
  that existing Shift hold before pressing it again for standing sprint.
- Stand from slow crouch: preserve the previous standing walk/jog mode.
- Releasing Shift while still crouched returns to slow crouch; its exit
  preserves the previous standing mode. Shift alone does not move you.

World source and filter code are unchanged from v8. Only the Ctrl jog-to-walk
speed curve changes; full stop, sprint-to-walk and sprint-to-jog keep existing
curves and deadlines. Actual translated checks at 30/60/144 FPS verify higher
early gait, monotonic easing and the same completion tick/deadline as v8 across
eight directions and achieved gait levels. Standing and crouch regressions
still pass. No animation clip or playback rate edits. Native Enforce compilation,
visual blending and physical velocity require the local DayZ test.
Logs: Profiles/MovementLogic. Previous packages remain unchanged.
