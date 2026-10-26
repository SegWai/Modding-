FIRST-PERSON / VERTICAL GRIP v60
Raised first-person camera now outputs explicit player-model coordinates instead
of sending the correction through a head-bound offset. Native ADS/optics camera
code is unchanged. Third-person camera and rifle pose settings are unchanged.
Vertical grip uses a weapon-relative left-hand target and the native arm IK2
solver; the unsuccessful extra weapon-IK pass is removed from the live path.
It adjusts only the support arm at vertical angles, not gun/trigger-hand settings.
Player and NPC use the same correction. Smooth lean transitions are retained.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Hold the gun raised, level, WITHOUT leaning for 2 seconds first. Then test Q/E
looking level and up/down, in first and third person. This records the actual
weapon-specific grip and first-person framing. F7 comparison, F9 measurements,
F10 NPC pause. If it still fails, close DayZ and Collect-Logs.cmd; new MLGRIP60
reports reference/weight and actual measured hand-to-target error.
Source/matrix/PBO checks are local only; Windows DayZ playback is not verified.
Only runtime essentials are included.
