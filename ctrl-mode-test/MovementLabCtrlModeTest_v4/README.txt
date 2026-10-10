MovementLab Ctrl Modes v4 - rear diagonal direction fix / body turning A/B

Close DayZ, keep Steam running, extract the WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing/import needed.

CONTROLS (same as Ctrl Modes v2):
- Starts in jogging mode. Tap Ctrl to toggle walking/jogging; it persists.
- Hold Shift to sprint, release it to return to the saved walk/jog mode.
- Release movement keys to stop using the existing directional slowdown.
- F8 toggles ORIGINAL BODY TURNING / MORE RESPONSIVE BODY TURNING.
  Starts with original body turning. B changes ONLY non-sprint body heading
  delay from 2.5 to 1.6. Direction response remains 2.5 in BOTH modes.
- F7 retains the separate whole-profile vanilla comparison. Keep custom
  movement enabled when testing F8. The on-screen message shows the choice.

FIXES:
- Continuous held input no longer restarts the startup walk/jog blend when
  native turning/backward movement lowers achieved speed. Only an actual
  idle start or a selected walk-to-jog/sprint mode change starts that blend.
- Ctrl jog-to-walk braking starts on a mode change, not repeatedly because
  native speed is still slightly above walking.
- A mode-return slowdown leaves steering to native held directional input;
  it does not pin an earlier forward angle or restart when steering changes.
  If you release movement mid-return, its stopping tail retains the most
  recently sampled direction. Fully released-input stops still own direction.
- A completed slowdown no longer holds a residual higher native gait forever.
- F8 no longer changes the movement-direction filter, only body heading.

TEST:
While jogging, hold W and slowly turn the mouse. Switch direction through
W+D, D, S+D, S, S+A, A, W+A, W without releasing all movement. Hold S+A
and S+D for several seconds. Repeat in Ctrl walking mode and both F8 states.
Then change to walk with Ctrl while in a rear diagonal, change directions
while it slows, and release keys to check stopping direction. Repeat sprint
and release-Shift tests to compare with v2's timing.

V2/v11 timers, startup curve, full-stop gait curves and sprint filter settings
are retained. No clip playback speed, direct position or physical velocity
writes. Native free-look/camera behavior is unchanged. The isolated jog/walk
blend experiment is not included. Old v2/v3 packages remain available.

New regression reproduces repeated startup in previous v3 and passes on v4.
Actual translated command/mission checks pass at 30/60/144 FPS and both callback
orders, with sustained native gait dips across rear diagonals and other inputs.
Original v11 full-stop and sprint-to-walk speed/deadline comparisons pass.
Filter/toggle tests verify only the body heading filter differs with F8.
These are mocked SDK tests. Native Enforce compilation, physical paths and
animation stability still require your in-game test. Logs: Profiles/MovementLogic.
