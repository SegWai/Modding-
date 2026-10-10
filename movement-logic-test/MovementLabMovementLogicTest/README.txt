MovementLab v6: short jogging stop

1. Close DayZ and leave Steam running.
2. Extract the entire v6 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

No Blender, Workbench or Addon Builder steps are needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + BRAKING mode. F7 switches to vanilla and back.
The sprint slowdown you approved in v5 is retained, including diagonals.

Jog without Shift, then release all movement keys:
- Try W, then W+A and W+D.
- Jogging now gets a short easing tail (at most 0.42 seconds of input ramp),
  aimed at roughly one small settling step rather than an instant stop.
- Compare with a full-sprint stop: jogging should settle sooner.
- F7 compares with vanilla in the same session.

Only achieved jogging gait (1.75 to 2.05) gets this new short tail. Ordinary
walking remains unaffected. Jogging release does not require Shift or sprint
exposure. The start speed and movement angle come from the native command;
no sprint speed is forced into a jogging stop.
The 0.42 seconds is an input duration, not a guaranteed physical stopping
time or fixed number of steps. Native animation phase determines footfalls.
No new animation clips, peak speeds, turning or startup settings are added.

New movement input immediately returns control. Crouching, raised hands,
menus, death, leaving movement mode, F7 and mission exit also cancel braking.
Logs are stored in Profiles\MovementLogic inside this extracted folder.

Tell me whether the jog stop feels like one small settling step and still
finishes faster than full sprint. Native v6 compilation/playback need your PC.
