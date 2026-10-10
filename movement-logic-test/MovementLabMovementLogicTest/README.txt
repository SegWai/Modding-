MovementLab v8: quick backward walking finish for S-only jog stops

1. Close DayZ and leave Steam running.
2. Extract the entire v8 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

No Blender, Workbench or Addon Builder steps are needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + BRAKING mode. F7 switches to vanilla and back.
The approved forward, diagonal and sideways stops are retained.

With empty hands, standing and looking ahead:
- Jog backward using only S, then release S.
- The brief settling tail now immediately requests a backward walking gait,
  aiming to match Ctrl+S, then returns to idle.
- This tail lasts at most 0.18 seconds of requested input, versus up to 0.42
  seconds for A/D-only jogging stops. It aims for a quick half-step back.
- Compare visually with Ctrl+S and with the longer A/D jogging stops.

S-only achieved jogging gets the new short tail. Ordinary walking is unchanged.
The backward direction is explicitly 180 degrees and the settling gait is 1
(walk). No Ctrl key simulation, binding changes or imported clips are used.
A specific footfall count or frame-exact transition cannot be guaranteed:
native animation timing still needs this local v8 test.

New movement input returns control immediately. Crouching, raised hands,
menus, death, leaving movement mode, F7 and mission exit also cancel braking.
Logs are stored in Profiles\MovementLogic inside this extracted folder.

Tell me whether he finishes with a tiny backward walk rather than forward,
and whether the backward stop is quick enough compared with A/D.
