MovementLab: vanilla-animation movement filter test

1. Close DayZ and leave Steam running.
2. Extract this entire ZIP somewhere on your PC.
3. Open Launch-Movement-Test.cmd inside MovementLabMovementLogicTest.

No Blender, Workbench import or Addon Builder step is needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.
It loads a separate offline mission with an invulnerable test character.

Starts in HEAVIER FILTERS mode. F7 switches to VANILLA FILTERS and back.
The mode appears in the chat/status area and script log.
Compare these in one session, with empty hands:
- Hold W, then hold/release Shift while keeping W held.
- Turn the camera while moving; try A and D direction changes.
- Release W. Observe whether stopping changes in either mode.

This first experiment increases native sprint and direction filter spans
and body-heading lag. It keeps vanilla animations and does not change
maximum movement speeds. It does not implement a new locomotion graph,
custom stop clips, or force the character to coast after releasing W.
Idle-to-jog acceleration and stopping changes are not established yet.

Tell me which mode feels better, whether turning has more weight, and
whether releasing W behaves differently. If a script error appears,
send the error text. Native compilation/playback still needs this PC test.

Logs and settings go into Profiles\MovementLogic within this extracted folder.
The previous arm-lift mod is not loaded by this launcher.
