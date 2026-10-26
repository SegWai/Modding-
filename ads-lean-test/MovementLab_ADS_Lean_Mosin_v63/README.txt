LEAN TEST v63 — SUPPORT HAND AT EVERY AIM ANGLE
v62 loaded without mod script errors, but grip activation stayed low: only 2/22
player samples positive, none at full weight. A 6.7cm error occurred while off.
v63 removes the pitch threshold: attachment weight now follows only the shared
custom-lean gate/amount, at every aim angle. Neutral reference stays frozen.
This can adjust the support arm during level lean too, to maintain grip.
Gun/trigger-hand/third-person pose settings and first-person camera code unchanged.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Raise the gun LEVEL without moving/leaning for 2 seconds to record its grip.
Then test both lean sides looking level/up/down; hold each for 2 seconds.
F7 comparison, F9 diagnostics, F10 NPC pause. Close DayZ, Collect-Logs.cmd.
MLGRIP63 reports weight and hand-target error. Visual/native solve not verified
locally. v62 also crashed after ~DayZGame() teardown; cause is not established.
