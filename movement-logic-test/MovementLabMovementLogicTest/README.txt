MovementLab v11: more jogging, shorter walk in full-sprint stops

1. Close DayZ and leave Steam running.
2. Extract the entire v11 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

The tested walking-start PBO remains included. No packing/import is needed.
The game path remains D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + STARTS + BRAKING mode. F7 compares with vanilla.

From near/full sprint, release movement keys and Shift:
- The slowdown now requests more jogging before a shorter walking finish.
- The total requested stopping duration and deadline are unchanged.
- Try forward and diagonal sprint stops.
- Approved walking starts, jogging-only stops and sideways/backward finishes
  retain their settings. Shift-only sprint-to-jog easing is also retained.

Within the same near/full-sprint full-stop budget:
- First 18 percent: slow from current sprint gait to jogging.
- Next 44 percent: request jogging.
- Next 20 percent: ease from jog to walk.
- Next 10 percent: brief walking finish.
- Final 8 percent: ease to idle, releasing at the existing deadline.

This applies only to full-stop ramps starting at achieved gait 2.5 or higher.
Slower/partial stops keep the approved curve. The controller still handles
native blending and collisions; gait requests do not guarantee exact visible
clip lengths or physical stop time. The scheduling deadline is unchanged.

Tell me whether you see enough jogging followed by a short walking finish,
and whether the overall stopping time still feels right. V11 needs your
local mission compilation/playback test; the startup PBO is unchanged.
Logs are stored in Profiles\MovementLogic inside this extracted folder.
