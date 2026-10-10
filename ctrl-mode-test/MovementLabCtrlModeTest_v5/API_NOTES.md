# Ctrl Modes v5, based on approved v4: sustained direction fix and body-only turning comparison

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

## v5 crouch rule

World accepts erect/crouch stances only after existing local-player/life/UI/aim
checks. Crouch bypasses standing startup/stop logic. Held Shift plus movement
requests gait 2; otherwise speed ownership is released to native crouch. A
valid crouch-to-erect edge selects persistent standing jog, regardless of Shift
release order or whether Shift was used. A new standing Ctrl edge selects walk.
Ctrl is still sampled in crouch to prevent a phantom edge on standing.

Mission cancels its standing brake in crouch and refreshes the same World-owned
crouch request, so cancellation cannot erase it in either callback order.
Other excluded states cancel custom ownership as before. Wanted gait cannot
report 3 while crouched Shift is held. No crouch animation graph or playback
rate is changed. Native stance/direction/weapon movement restrictions apply.

Actual translated crouch cases run at 30/60/144 FPS, both callback orders,
including keys W/A/S/D and rear/front diagonals, Shift release before/after
standing, idle Shift, Ctrl held across stance change, standing brake interruption
and prone/disabled-profile exclusions. Standing movement regressions still
pass; the native filter method is identical to approved v4. Native Enforce
compilation and crouch animation/physics need the in-game test.
