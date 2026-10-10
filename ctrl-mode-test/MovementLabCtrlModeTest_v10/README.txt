MovementLab Ctrl Modes v10 - later walk entry / stronger jog-to-walk momentum

Close DayZ, keep Steam running, extract the WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing/import needed.

TEST THIS CHANGE:
Hold W to jog, then tap Ctrl while keeping W held. Instead of immediately
reducing the jog gait toward walking, the controller keeps the moving jog
briefly, then eases into walking. For achieved full jogging: about 0.12 seconds
of continued jogging followed by a 0.30-second smooth reduction into walk.
Total request duration is still 0.42 seconds, not longer than v9. This holds
the requested moving gait, NOT an animation frame. No freeze or extra walking
tail. Backward/partial-gait transitions retain their shorter existing budgets
and the same jog/blend proportions. Native animation blending owns the result.

Everything else is retained:
- Responsive body rotation is permanent; no F8 movement toggle.
- Ctrl while standing toggles walk/jog; new standing Shift press sprints.
- Without Shift crouch is slow. Shift+direction uses native fast crouch.
- Stand from active fast crouch: jogging until Ctrl selects walk. Release
  the Shift hold used for fast crouch before pressing it again for sprint.
- Stand from slow crouch: preserve previous standing walk/jog mode.
- Releasing Shift while still crouched returns to slow crouch; standing
  then preserves the previous standing mode.
- Direction fixes, full stopping, sprint-to-walk/jog curves and timers remain.
- F7 still compares the whole profile with vanilla.

Actual translated checks pass at 30/60/144 FPS and both callback orders.
Comparison with v9 verifies initial gait retention, monotonic blend, higher
early momentum and identical deadline/completion tick in eight directions
and achieved gait levels. Standing/crouch/stop regressions pass; World source
and native filters remain unchanged. Native Enforce compilation and animation
feel need the local game test. No clip or playback-rate edits.
Logs: Profiles/MovementLogic. Previous packages remain unchanged.
