Lean range v34 — final grip solver type correction

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects.

V33 failed to load the animation graph: its three solver-enable fields used floats where DayZ expects booleans. V34 sets WeightAim=false and enables both hand chains with the existing reference-hold expression compared against0.001. No pose/position changes. Native solver blend times, final attachment publication, current arm hold, body/head/legs, gait, equipment, ammo, ragdoll and respawn are unchanged. Same shared graph for player and NPC.

Starts enabled. F5 reference hold comparison; F6 head comparison; F7 native/custom; F8 inspection; F9 diagnostics; F10 pause.

The type correction needs native compilation/visual verification. Check both hands from the side. If needed, close DayZ, run Collect-Logs.cmd and send the v34 ZIP. Included authoring PNGs are v32 pose previews and do not validate the native grip solve.
