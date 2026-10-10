# Ctrl Modes v6, based on approved v4: sustained direction fix and body-only turning comparison

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

## v6 native fast crouch correction

V5 incorrectly capped crouched Shift input at gait 2. The uploaded locomotion
AGR has CroRunSprintBlend = clamp((MovementSpeed-2)*(1-Injured),0,1), so an
input of 2 suppresses its fast crouch blend. V6 restores native crouch input
instead of imposing another guessed fast gait. MovementLabRefreshCrouchJog
only releases custom standing speed ownership. No speed or angle override
is requested in crouch, and no graph/clip change is made.

The valid crouch-to-standing edge still selects persistent standing jog until
a new standing Ctrl press. Resetting the previous wanted gait on this edge
prevents same-frame Shift release from holding a fast crouch request while
waiting for a standing slowdown that was never started. Shift held across
standing requests normal standing sprint, then returns to jog on release.

The mission cancels standing braking in crouch and refreshes the ownership
release in either callback order. Native controls handle crouch Shift, normal
crouch and directional constraints. Standing filter code is identical to v4.

The crouch regression checks every frame for no speed/angle ownership at
30/60/144 FPS in both callback orders over directional masks. This fails on
v5 and passes on v6. The mock falls back to raw native action gait when an
override is absent; that models uncapped input, not measured crouch velocity.
Shift release before/after/same-frame standing, idle Shift, Ctrl held across
stance change and standing-brake interruption are checked. Standing movement
regressions remain passing. Native Enforce and visual/physics testing is local.
