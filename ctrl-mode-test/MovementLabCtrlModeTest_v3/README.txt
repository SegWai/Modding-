MovementLab Ctrl Modes v3 - v2 movement plus F8 turning comparison

Close DayZ, keep Steam running, extract into a fresh folder and run
Launch-Movement-Test.cmd. No packing/import needed. Original v11 is unchanged.

Turning comparison:
- Starts with ORIGINAL V2 TURNING (A), exactly the previous filter settings.
- Press F8 for MORE RESPONSIVE WALK/JOG TURNING (B); press again to restore A.
- B reduces the native non-sprint body heading span and movement direction
  delay multipliers from 2.5 to 1.6. This should reduce the slow, wide curve
  when steering with the mouse while walking/jogging. Sprint settings are
  unchanged. It does not rotate/teleport the entity or change camera controls.
- Use Ctrl to select walking or jogging, hold W, and turn with the mouse.
  Compare the same turn with F8. The on-screen message confirms A/B selection.
  Normal Alt free-look still works as in DayZ; this is a movement-turn test.
- F8 keeps the current movement/braking state running; it does not reset it.
- Leave F7 in the custom movement mode for the A/B comparison. F7 still
  switches the whole movement profile against vanilla as before.

Controls:
- Initial mode: jogging, with v11's brief walking startup before jogging.
- Tap Ctrl once: toggle jogging <-> walking. It stays selected after release
  of Ctrl and after stopping; holding Ctrl does not keep toggling.
- Hold Shift in either mode: full sprint, using native v11 acceleration.
  From walking it first uses the original walk/jog lead-in.
- Release Shift while still holding movement: smoothly return to the mode
  you used before sprinting (jogging or walking).
- Release all movement while Shift is still held: sprint -> jog -> walk ->
  stop, keeping the v11 stopping budget and direction. Shift cannot sustain
  movement by itself. If another direction key is held, movement continues
  in that direction; releasing one diagonal key does not stop all movement.
- Ctrl during held Shift is ignored to preserve your pre-sprint mode.
- F7 compares against native/vanilla controls and filters.

Timing:
V11 startup: walking lead-in 0.10s, walk/jog blend 0.18s, startup handoff 0.35s.
V11 sustained full-sprint stop: max 1.15s, scaled by achieved speed/exposure;
longer jog and shorter walk phases in the same budget. Brief Shift taps cannot
receive a full-sprint stop just from requesting sprint.
Jog stop: original 0.42s settle, with 0.18s pure backward finish.
Walking stop: original native behavior; no new walking-stop timer.
Ctrl jog->walk uses the original jogging settle timer, finishing at walking.
Shift sprint->jog uses original 0.12+0.33*weight slowdown. Sprint->walk uses
the original full-stop phase budget AND speed curve, then stays at walking
instead of going idle. This includes partial sprint below gait 2.5 and the
same directional walking finish. There is no animation freeze or new timer.

Test Ctrl toggles while moving and idle. Test Shift from each mode, release
Shift while holding W, then release W while still holding Shift. Check all
stopping directions and very brief Shift taps. Logs: Profiles/MovementLogic.
Native direction/stamina/stance limitations remain; native engine owns clips
and blending. Standing controls only; other stances/gestures/aiming/UI restore
native controls. No custom reversal, frame hold or direct position changes.

Actual translated PlayerBase and mission checks passed at 30/60/144 FPS,
in both command/mission callback orders, with a mocked SDK. Sprint/jog stop
curves and deadlines match v11 tick-for-tick in forward/diagonal/side/backward
cases. Sprint-to-walk requests match the original stop frame-for-frame down
to walking at partial/full sprint speeds and short/full sprint exposure.
Native Enforce compilation and animation behavior need the local test.

The World hook and mission start/brake methods match v2 exactly. Actual
translated filter checks verify A/v2 equality and only two B filter changes
across braking/stamina states; F8 does not cancel startup/braking. Movement
regression checks pass at 30/60/144 FPS. Native turning behavior needs the
local game test. This does not include the discarded isolated walk-blend test.
