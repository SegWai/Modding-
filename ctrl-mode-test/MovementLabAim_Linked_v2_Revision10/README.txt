Immediate Scroll Targets v2 — based on user-confirmed all-pose smoothing v1.
Standing upward ladder: walk~85,walk100,walk120,jog80,jog100,sprint100.
Prior downward boundary retained: jog80 -> defaultwalk~85 (notwalk120).
A wheel burst can select any target across mode boundaries in one update.
Crouch ladder remains30/~47/60/~73/~87/nativefast.
Raw signed wheel delta counted; common120-unit deltas normalized, action press fallback.
Animations/acceleration blend toward the stored target after scrolling stops.
No need to wait for animation completion before selecting another speed.
Pending input during temporary native command restrictions is applied when eligible;
menus/pause/stance changes clear pending input. Clamp at ladder endpoints.
Physical held Shift still overrides current gait; target selection is retained.
No graph/clip/brake/pose timer changes from confirmed all-smoothing package.
Close DayZ, extract ZIP, run Launch-Movement-Test.cmd.
Native wheel sign/units/focus and visual pacing require local test; logs record raw steps.
Default confirmed PoseExit v2 and previous all-smoothing package stay preserved.

Revision10: jog100 -> fast aim native100; fast aim100/120 -> jog100 on lowering. Fast aim80 -> jog80. Fast aim level2 now uses original native animation sources. Entry Shift latch initialized from held input.

Sprint -> aim enters exclusive fast aim140% (42FPS), smoothly falls to native100% over0.5s. Wheel events during transition are discarded. Normal wheel levels remain80/100/120. Crouch/slow aim unchanged.
