MovementLab v100 — configured infected-model Human-physics corpse experiment

Close DayZ, extract the ENTIRE ZIP into a NEW folder, then run
Launch-Movement-Test.cmd. Kill the ONE zombie, 20m ahead, and watch its body.
Close DayZ and run Collect-Logs.cmd. Send MovementLab-Corpse-v100-Logs.zip and
say whether the visible corpse was the zombie, and whether its limbs fell freely.

This is a different implementation: a custom Human actor has the infected P3D
configured BEFORE native creation. On confirmed infected death, this actor is
created dead, and native Human ragdoll is enabled. If its actual mesh is the
infected mesh and ragdoll activates, the original corpse is hidden and its
collision disabled; the new infected-looking physics corpse is revealed.
Both are cleaned up before the ONE living infected respawns, 5s after death.
Living infected AI is unchanged. No extra living human target is added.

This is corpse replacement, not native ragdoll on the DayZInfected controller.
It does not copy/write bones or call SetObject after creation. The v94/v95
hidden Human driver, mesh swap and v96-99 bone probes are absent. It remains
an unverified native experiment; correct mesh and visible physics need your run.
If initialization/model checks fail, it retains the normal infected corpse.

Existing movement, human fixtures, gear, guns, grenades and Gunter are retained.
