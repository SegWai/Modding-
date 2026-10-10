MovementLab Ctrl Modes v1 - original v11 plus Ctrl toggle / Shift return mode

Close DayZ, keep Steam running, extract into a fresh folder and run
Launch-Movement-Test.cmd. No packing/import needed. Original v11 is unchanged.

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
the original full-stop phase budget but finishes at walking instead of idle.

Test Ctrl toggles while moving and idle. Test Shift from each mode, release
Shift while holding W, then release W while still holding Shift. Check all
stopping directions and very brief Shift taps. Logs: Profiles/MovementLogic.
Native direction/stamina/stance limitations remain; native engine owns clips
and blending. Standing controls only; other stances/gestures/aiming/UI restore
native controls. No custom reversal, frame hold or direct position changes.

Actual translated PlayerBase and mission checks passed at 30/60/144 FPS,
in both command/mission callback orders, with a mocked SDK. Sprint/jog stop
curves and deadlines match v11 tick-for-tick in forward/diagonal/side/backward
cases. Native Enforce compilation and animation behavior need the local test.
