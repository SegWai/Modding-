# Ctrl Modes v4: sustained direction fix and body-only turning comparison

Based on v3, retaining v2 controls and v11 timing budgets. Original packages
are unchanged; the discarded standalone jog/walk blend is not integrated.

The previous World hook re-entered startup whenever native achieved speed was
below 1.75, even while continuous jogging was requested. Directional turns
can reduce native gait independently of selected mode. A new regression
injects sustained gait 1.4 during jogging over W/WA/A/SA/S/SD/D/WD input and
reproduces repeated startup on v3. V4 requires an actual previous wanted mode
of walking for this startup branch. Idle-start detection remains unchanged.

World tracks selected gait and owns a decrease-pending flag only until the
mission begins its slowdown. It no longer indefinitely preserves a residual
achieved gait after the slowdown finishes. Mission tracks wanted gait too:
generic jog-to-walk brakes start on a decrease edge, not every residual native
speed sample above 1.05. Existing timer formulas and curves are preserved.

While a mode-return brake has live directional input, the speed envelope can
continue through direction changes and the angle override is disabled. The
native controller receives steering. Current keys/angle are remembered for
release during the return. Released-input braking retains its original angle
ownership and cardinal finish rules. New faster input still cancels a return.

F8 changes ONLY SetTurnSpanModifier from 2.5 to 1.6 in the custom profile.
SetDirectionFilterModifier remains 2.5 for both A/B choices. Sprint-specific
heading/direction, run/sprint filters and stamina formulas are unchanged.
F8 does not cancel or restart speed state. F7 retains the vanilla comparison.

Checks execute actual mechanically translated World and mission methods at
30/60/144 FPS in both callback orders. Added sustained-gait-dip cases span
selected walking and jogging plus backward diagonals. Live mode-return angle
ownership is checked. Full-stop curves/deadlines still compare to v11; return
to walk still matches the stop envelope down to the walking floor. Separate
actual filter/key-toggle methods verify A/B differs only in body heading.
No native engine, clip frames or actual movement paths are measured here.
Native Enforce compilation and visual/physics validation require local DayZ.
