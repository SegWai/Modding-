MovementLab v5: diagonal sprint braking

1. Close DayZ and leave Steam running.
2. Extract the entire v5 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

No Blender, Workbench or Addon Builder steps are needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + SPRINT BRAKING mode. F7 switches to vanilla and back.
Forward startup, turning and the braking curve approved in v4 are retained.

Compare these with empty hands, standing and looking ahead:
- Sprint with W + Shift, then release all movement keys and Shift.
- Sprint with W + A + Shift, then release all movement keys and Shift.
- Repeat with W + D + Shift.
- Also release only Shift while retaining W + A or W + D: it should ease
  down to jogging in the direction you were moving.

V4 discarded braking while A or D was held. V5 includes diagonal input and
captures the current movement angle so a diagonal stop stays diagonal.
The same speed/exposure formula applies in every direction. If native DayZ
limits a direction to jogging, the mod does not force sprint speed into it.
A genuinely slower gait can still have a shorter stop than achieved sprint.

Changing movement keys or resuming sprint during Shift-only braking returns
control immediately. During a full-stop coast, any new movement input returns
control. Crouching, raised hands, menus, death, leaving movement mode, F7 and
mission exit also cancel braking.

The 0.18-1.15s stop and 0.12-0.45s Shift-only ranges are input-ramp durations,
not guaranteed physical stopping times. Direction remains relative to current
heading, not a world-space momentum simulation. No new animation clips or
maximum speed changes are included.

Tell me whether diagonal stops now match forward stops at a similar speed,
and whether he stays on the correct diagonal rather than veering straight.
Native compilation and gameplay of v5 still need your PC test.
Logs are stored in Profiles\MovementLogic inside this extracted folder.
