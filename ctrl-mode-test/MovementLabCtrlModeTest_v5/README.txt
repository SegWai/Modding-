MovementLab Ctrl Modes v5 - crouch Shift jog / persistent standing jog

Close DayZ, keep Steam running, extract the WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing/import needed.

NEW CROUCH RULE:
- In crouch, hold a movement direction and Shift to request native crouched
  jogging (gait 2). It never requests upright sprint while crouched.
- Shift without movement does not move the character.
- Release Shift while still crouched: movement returns to native crouch input.
- Standing up from crouch ALWAYS selects standing jog mode, even if Shift
  was released first or was never pressed during that crouch.
- Hold Shift when standing up: normal standing sprint, then release Shift
  to return to jogging. Tap Ctrl while standing to select walking again.
- Ctrl during crouch does not change the standing mode. A held Ctrl key
  does not become an extra toggle when you stand; release and tap it again.
- No scripted standing startup/stopping tail runs while crouched. Native
  crouch clips/steering/limits remain engine-owned.

STANDING CONTROLS (retained from approved v4):
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
blend experiment is not included. Approved stable v4 remains available unchanged as the fallback.

New regression reproduces repeated startup in previous v3 and passes on v4.
Actual translated command/mission checks pass at 30/60/144 FPS and both callback
orders, with sustained native gait dips across rear diagonals and other inputs.
Original v11 full-stop and sprint-to-walk speed/deadline comparisons pass.
Filter/toggle tests verify only the body heading filter differs with F8.
These are mocked SDK tests. Native Enforce compilation, physical paths and
animation stability still require your in-game test. Logs: Profiles/MovementLogic.

Test: select walking with Ctrl, crouch, hold W+Shift, release Shift, then stand
while holding W. Expect standing jogging until the next Ctrl tap. Repeat with
Shift still held when standing (sprint, then jog on release), and while idle.
Crouch tests pass in both callback orders at 30/60/144 FPS, including directional
masks, Ctrl held across stance changes, release order, active standing brake
interruption, and disabled/prone exclusions. Native crouch behavior still needs
your local DayZ test. The native filter method matches approved v4 exactly.
