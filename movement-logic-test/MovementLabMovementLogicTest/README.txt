MovementLab v10: command-level walking start (fixes v9 jog flash)

1. Close DayZ and leave Steam running.
2. Extract the entire v10 ZIP into a separate folder.
3. Open Launch-Movement-Test.cmd.

A small script-only PBO is already included. No Addon Builder, Blender or
Workbench step is required. Keep the @MovementLabStartGate folder with the
launcher and mission; the launcher loads it automatically.
The game path remains D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

Starts in HEAVIER + STARTS + BRAKING mode. F7 compares with vanilla.

From a complete stop, with empty hands and standing:
- Press W without Shift. The first visible moving gait should be walking,
  then jogging. Check that v9's jog -> walk -> jog flash is gone.
- Try W+Shift: walking -> jogging -> native sprint.
- Try A, D, S and diagonals from idle.
- Ctrl walking stays native walking.
- Release keys during the walking lead-in: acceleration must cancel promptly.
- Check the approved directional stopping still feels right.

V9 applied walking in a late mission-frame update. V10 applies startup before
the base PlayerBase.CommandHandler and primes persistent speed 0 while idle.
Idle gating does not move the character; it prevents unfiltered jogging from
getting through before the first walking request. Native keys choose direction.
Requested startup timing remains 0.10s walk, 0.18s walk-to-jog and 0.07s jog,
then handoff to native sprint where allowed. Other stopping formulas retain
their approved settings and explicitly own braking overrides separately.

Native loading/compilation of the new PBO and the first visible gait need your
local v10 test. If DayZ reports a script/config error, send its exact text.
Logs are stored in Profiles\MovementLogic inside this extracted folder.
