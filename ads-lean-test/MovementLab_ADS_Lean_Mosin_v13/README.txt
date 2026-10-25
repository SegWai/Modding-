Mosin lean v13 — graph load correction

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd directly.
Project root: F:\DayZProjects; Steam game directory is separate.
Only vanilla Mosin. F7 custom/native comparison; F8 third-person inspection;
F9 player/NPC measurements; F10 pause/resume NPC movement.

V12 failed before NPC creation. Logs show unrecognized custom controls and invalid HasVariableChanged expression arguments. V13 restores player_main.agr BYTE-FOR-BYTE from v11, whose native logs confirmed successful distinct bindings. It declares no new variables and reuses the existing, unused-as-output MLADSLeanCanary float: default 0.731 keeps player behavior; 1 enables only the designated offline NPC's raised ADS graph routing. On stop it resets to 0.731. Change-detection functions retain their original variable arguments.

The NPC controller still selects the shared raised ADS and custom lean nodes, with a 0.4-second graph blend warmup before native movement between +/-2m endpoints. This warmup is not native weapon-raise verification. Native telemetry remains logged separately. No position teleports or animation playback speed multiplier. Default native walk gait is 1; it remembers the player's latest moving ADS gait. Authored pose targets, player graph behavior at the default canary, foot IK and shared gun cant are preserved.

Validation here checks expression structure, known-good controls, player expression identity, pose preservation and packed PBO contents. Native DayZ graph compilation and playback are NOT available here and still require a game test.

If there is a problem, close DayZ and run Collect-Logs.cmd. New archives are labeled v13.
