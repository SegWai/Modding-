V114 — female movement recorder and quiet controls; weapon 5cm forward

The male NPC keeps his current patrol and custom poses. A second NPC, SurvivorF_Eva in a blue hoodie, spawns 10 metres to HIS own right (relative to his initial facing direction). Both use the same custom player/NPC graph. The female stands idle until playback starts. The current left-walking weapon hold has no sideways offset: both hands/weapon target move 5cm character-forward (+model Z) from the original reference. Left elbow target 20 degrees and right elbow 45 degrees outward from straight down are retained. Native visible angles/offsets remain reach-constrained and require testing.

CONTROLS
- Ctrl+F8: the only retained old test toggle; arm comparison ON/OFF.
- Tap L: start recording; tap L again: stop recording.
- Colon (:): replay the recorded sequence on the woman in a loop.
- Tap L during playback: stop the loop and hold her last pose; it does not start a new recording on that same tap.
- Hold L for 0.75 seconds: stop/clear the recording and return the woman to her starting spot. Release, then tap L to record again.

The colon key is accepted as semicolon/colon on US layouts, Shift+period on Portuguese layouts, or the native colon key code. Other added F5/F6/F7/F8/F9/F10 and Ctrl+F9 comparisons are removed. All added in-game notifications and timed distance-calibration prompts are removed; recorder state is written to logs instead. Controls are ignored while a game menu/text-entry menu is open. A short L tap is committed on release so a long hold can clear without accidentally starting another recording.

REPLAY
Recording samples actual movement at up to 20Hz, including turning, walk/run/sprint, standing/crouching/prone, lean, weapon raise and aim direction. Playback interpolates those samples and uses native locomotion. Relative paths rotate into the woman's starting facing direction. Every loop returns to her starting spot; paths ending elsewhere will visibly return at the loop boundary. Playback corrects positional drift over 25cm. Maximum 6000 samples (about 5 minutes); recordings are in memory for this game session.

At playback start she receives the weapon held when recording began, with its direct attachments and loaded ammunition. Weapon switching, reload/firing events, emotes, jumps/vaults, inventory and other interactions are not recorded. This is movement/pose replay, not full gameplay replay. Terrain/collisions and female proportions can affect native motion. Both NPCs retain ragdoll/one-second respawn handling; if she dies, playback stops and the recording remains available after respawn.

DEPENDENCIES / LAUNCH
Install/download Community Framework (1559212036) and AJs Weapons (3571685323) through Steam. Launcher loads CF, AJ, workspace, then logic. No Workshop files are redistributed. Extract the full ZIP and run Launch-Mosin-Lean-Test.cmd. Default game: D:\SteamLibrary\steamapps\common\DayZ; project root F:\DayZProjects. Run Collect-Logs.cmd after testing if replay fails. The ZIP contains runtime essentials only.

Local source, math and package checks do not establish native compilation or playback correctness. The female replay controller has not been run in Windows DayZ here. Previous versions remain separate rollback ZIPs.
