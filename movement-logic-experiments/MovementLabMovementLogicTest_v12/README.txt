MovementLab v12 EXPERIMENT: shorter smooth sprint stop and A/D reversal brake

V11 remains the stable version. Extract this experiment separately and keep
v11 available. This experiment does not replace your v11 folder or assets.

1. Close DayZ and leave Steam running.
2. Extract the entire v12 ZIP into a new folder.
3. Open Launch-Movement-Test.cmd. The experimental script PBO is included;
   no Addon Builder, Blender or Workbench steps are needed.

Starts in the heavier experimental mode. F7 compares with vanilla.
Game path: D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Test 1: fully sprint forward/diagonally, then release movement and Shift.
- Maximum requested sprint-stop budget is 0.92 seconds, down from 1.15 in v11.
- Sprint -> jog -> walk -> idle is a continuous gait ramp without fixed holds.
- Native blending chooses the animation; this is not a new/reversed clip.

Test 2: jog left holding A, then switch straight to D. Repeat D -> A.
- Also try Shift+A -> Shift+D and W+A -> W+D while moving fast enough.
- He should brake in his OLD direction, settle to idle, pause about 0.12s,
  then use the walking lead-in before moving in the currently held direction.
- Repeated opposite-key taps during the sequence do not skip its stop/pause.
- Releasing all keys should leave him stopped, not restart automatically.
- Keeping both A and D held should not create forward creeping.
- Deliberate Ctrl walking bypasses the jog reversal restriction.

A jogging reversal uses the established short directional jogging stop. An
achieved faster gait uses the shorter sprint stop envelope. The timer waits
for native gait to reach idle before its brief pause; a bounded 0.60s idle
wait returns control if that confirmation fails, with a diagnostic log.
Turning the camera can still change world-relative heading. This experiment
restricts opposite lateral input, not every possible zigzag technique.

Crouching, raised hands, menus, death, leaving movement mode, F7 and mission
exit clear the experiment's overrides. This is an offline test, not a
multiplayer-ready movement controller. Native compilation/playback is pending.
Logs: Profiles\MovementLogic inside this extracted folder.

Tell me whether sprint stopping is now short/smooth enough, and whether
A/D reversals brake, pause and restart without snapping or getting stuck.
