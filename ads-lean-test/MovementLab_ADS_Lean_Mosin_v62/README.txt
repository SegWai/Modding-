LEAN TEST v62
v61 compiled, but grip correction was mostly inactive: 2/63 player samples,
never full weight. Its trigger used rifle elevation instead of native aim pitch.
v62 uses HumanCommandWeapons.GetBaseAimingAngleUD() in degrees. Grip calibration
now requires a stable level NEUTRAL raised hold, then freezes until weapon change.
The camera returns to native head binding whenever its correction is inactive.
Third-person gun, graph, pose geometry, ADS/optic camera and smoothing unchanged.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Raise the gun LEVEL, without leaning or moving, for 2 seconds. Then test both
lean sides while looking up/down, in first and third person. Hold each vertical
aim for 2 seconds. F7 comparison, F9 diagnostics, F10 NPC pause.
Close DayZ and Collect-Logs.cmd if needed: MLGRIP62 now includes native pitch,
weight and measured hand-target error. The previous native crash is recorded
but its cause is not established. Local checks passed; native test still needed.
