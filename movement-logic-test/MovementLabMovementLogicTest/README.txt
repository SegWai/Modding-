MovementLab v9: brief walking start in every direction

1. Close DayZ and leave Steam running.
2. Extract the entire v9 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

No Blender, Workbench or Addon Builder steps are needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + STARTS + BRAKING mode. F7 switches to vanilla and back.
The stopping settings you approved in v8 are retained.

From a full stop, with empty hands and standing:
- Press W, A, D or S without Shift. Each should briefly walk in that direction,
  then ease into jogging.
- Try W+A, W+D and backward diagonals too.
- Hold W+Shift from idle. It should walk, ease into jogging, then let the
  existing native sprint transition accelerate into full sprint.
- Ctrl walking remains walking. Pure A/D/S is not forced into full sprint.
- Releasing keys early cancels the startup; there is no automatic continued
  acceleration after you let go.

Requested startup: 0.10s walking, 0.18s smooth walk-to-jog, 0.07s jogging,
then return control to the native input. Direction remains live from your keys.
The startup does not replay merely because you turn while already moving.
It arms again after reaching idle, rather than restarting during braking.
These durations describe input requests, not guaranteed animation timing.

New direction input, mode changes and the existing cancellation guards retain
control. Crouching, raised hands, menus, death, leaving movement mode, F7 and
mission exit also cancel overrides. No new animation clips are imported.
Logs are stored in Profiles\MovementLogic inside this extracted folder.

Tell me whether the brief walk is visible and feels natural in all directions,
and whether holding Shift gives a smooth walk -> jog -> sprint progression.
Native v9 compilation and playback still need your PC test.
