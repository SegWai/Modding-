MovementLab v7: sideways walking finish for A/D-only jog stops

1. Close DayZ and leave Steam running.
2. Extract the entire v7 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

No Blender, Workbench or Addon Builder steps are needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + BRAKING mode. F7 switches to vanilla and back.
Jog/sprint stop durations, startup and turning retain the approved settings.

With empty hands, standing and looking ahead:
- Jog using only A, then release it. The settling phase now requests a
  left-side walking gait before idle, aiming to match Ctrl+A's movement.
- Repeat using only D, aiming for a right-side walk like Ctrl+D.
- Compare with manually holding Ctrl+A or Ctrl+D as a visual reference.
- Also check a forward/diagonal stop still feels as it did in v6.

Pure A/D stops explicitly request -90/+90 degrees and keep gait at 1 (walk)
during the final portion of the existing short jogging tail. The override
is released at the same deadline to return to idle. It does not simulate
Ctrl or change your key bindings, and does not import new animation clips.
Native animation selection and the final transition to idle need your test.

New movement input immediately returns control. Crouching, raised hands,
menus, death, leaving movement mode, F7 and mission exit also cancel braking.
Logs are stored in Profiles\MovementLogic inside this extracted folder.

Tell me whether the final step stays sideways on both A and D, rather than
changing to a forward walk. Native v7 compilation/playback need your PC test.
