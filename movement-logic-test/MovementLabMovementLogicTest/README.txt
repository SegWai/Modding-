MovementLab v2: slower sprint stopping with vanilla animations

1. Close DayZ and leave Steam running.
2. Extract this entire ZIP somewhere on your PC.
3. Open Launch-Movement-Test.cmd inside MovementLabMovementLogicTest.

No Blender, Workbench import or Addon Builder step is needed.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.
It loads a separate offline mission with an invulnerable test character.

Starts in HEAVIER + SPRINT BRAKING mode. F7 switches to VANILLA FILTERS and back.
The mode appears in the chat/status area and script log.
Compare these in one session, with empty hands:
- Hold W, then hold/release Shift while keeping W held.
- Turn the camera while moving; try A and D direction changes.
- Sprint straight forward for several seconds, then release W and Shift together.
- In heavier mode, a 0.85-second input ramp requests sprint -> jog -> walk -> idle.
- Repeat in vanilla mode to compare stopping.

Heavier turning from v1 is retained. Sprint braking is new and needs your
first in-game test. This ramp controls movement input, not physical velocity;
0.85 seconds is the requested ramp duration, not a guaranteed stopping time.
There are no new animation clips or maximum speed changes.
It targets straight forward, standing sprint release only. Jogging release,
sideways movement and idle-to-jog acceleration are unchanged.
The coast requests forward movement relative to your heading: keep looking
ahead for this initial test. It is not a world-space momentum simulation.
New W/A/S/D input, crouching, raised hands, leaving movement mode, menus,
death, F7 or mission exit cancel the ramp. No entity teleporting is used.

Tell me whether it takes extra steps to stop and whether those steps look
natural or slide. If a script error appears,
send the error text. Native compilation/playback still needs this PC test.

Logs and settings go into Profiles\MovementLogic within this extracted folder.
The previous arm-lift mod is not loaded by this launcher.
Extract v2 into its own folder so your working v1 test remains available.
