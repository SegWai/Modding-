Mosin lean v12 — offline demo controller revision

Extract into a new folder. Run Launch-Mosin-Lean-Test.cmd directly.
Project root: F:\DayZProjects (the Steam game directory is separate).
Only the vanilla Mosin is used.

F7: custom/native lean comparison. F8: third-person inspection.
F9: player and NPC joint measurements. F10: pause/resume NPC movement.

The previous demo incorrectly depended on a second spawned player's native raise input remaining active. Both v11 runs show a brief completed raise, followed by native_raise_input=false and stance=0. V12 removes the player-raise/stance forcing and gives only the offline demo an explicit private animation control. That control selects the same raised ADS locomotion branches, hand IK and custom lean nodes already used by the player. After 0.4 seconds of graph warmup, it patrols between +/-2m endpoints using native movement; no position teleports or animation playback speed multiplier. The warmup is an animation blend delay, not proof of native weapon-raise completion. Actual native state is logged separately.

The private control defaults to 0 for the player. Player expression behavior, authored pose targets, crouch legs, walking foot IK and shared weapon roll are preserved. Graph expressions now allow the demo to select those same branches without a working native player raise input. This is a new controller revision requiring a DayZ compile/playback test, not a verified in-game fix. Local graph/pose and archive checks do not replace game testing.

To report a problem: let the mission run for 15 seconds, close DayZ and run Collect-Logs.cmd. The collector labels new logs v12.
