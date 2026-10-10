MovementLab v4: immediate, speed-dependent sprint braking

1. Close DayZ and leave Steam running.
2. Extract the entire v4 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

No Blender, Workbench or Addon Builder steps are needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + SPRINT BRAKING mode. F7 switches to vanilla and back.
Startup and heavier turning retain their previous settings.

With empty hands, standing and looking straight ahead:
- Fully sprint with W + Shift, then release both. Braking starts immediately
  instead of holding near full sprint. Maximum requested stop ramp: 1.15s.
- Fully sprint, then release Shift while keeping W held. Sprint-to-jog
  slowdown begins immediately; maximum requested ramp: 0.45s.
- Jog, tap Shift briefly, then release W + Shift. A partial/brief sprint
  gets a much shorter stop, using its sampled gait instead of forcing sprint.
- Releasing W during Shift-only slowdown continues from the current request.
- Press F7 to compare with vanilla in the same session.

Braking duration scales with achieved gait and time spent sprinting.
The 0.18-1.15s stop and 0.12-0.45s Shift ranges are input-ramp durations,
not guaranteed physical stopping times. The sprint filter is shortened only
while braking to avoid resisting the immediate slowdown.
No animation clips or maximum speed changes are included.
Jog-release braking outside an active/achieved sprint is unchanged.
The engine controls gait blending and collision; movement follows your
current heading rather than retained world-space momentum.
New direction input, resumed movement/sprint, crouching, raised hands, menus,
death, leaving movement mode, F7 and mission exit cancel the override.

Tell me whether the full-sprint stop is now smoother without that long sprint
hold, and whether a brief Shift tap stops promptly without speeding you up.
Native compilation and playback of v4 still need your PC test.
Logs are stored in Profiles\MovementLogic inside this extracted folder.
