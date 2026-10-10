MovementLab v3: longer sprint braking with vanilla animations

1. Close DayZ and leave Steam running.
2. Extract the entire v3 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

No Blender, Workbench or Addon Builder steps are needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + SPRINT BRAKING mode. F7 switches to vanilla and back.
The heavier turning and normal startup from the previous test are retained.

With empty hands, standing and looking straight ahead:
- Hold W + Shift until fully sprinting.
- Release Shift while keeping W held: requests a gradual 1.6-second slowdown
  into jogging. Holding W means you continue moving, rather than stop.
- Sprint again, then release both W and Shift: requests a 2.2-second full-stop
  ramp. It holds a faster pace longer before easing down through slower gaits.
- You can also release W during the Shift-only slowdown; braking continues
  from its current request rather than snapping back to sprint.
- F7 lets you compare with vanilla in the same session.

The durations describe input ramps, not guaranteed physical stopping times.
No animation clips, top speeds, or normal acceleration settings are changed.
Jog-release braking is unchanged outside an active sprint slowdown.
The native engine still controls gait blending and collision. This is not a
physics momentum simulation; stopping follows your current heading.
New direction input, resuming sprint, crouching, raised hands, menus, death,
leaving the move command, F7 and mission exit cancel the override.

Tell me whether the full-sprint stop is now long enough and whether Shift-only
release feels smooth. Native compilation and playback of v3 need your PC test.
Logs are stored in Profiles\MovementLogic in this extracted folder.
