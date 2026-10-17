MovementLab v66 - DayZ 1.30 animation workspace migration

Uses the freshly extracted 1.30 workspace supplied by the user. Native player_main.agr, .ast and .asi files now use the 1.30 source schemas. Custom locomotion nodes have been ported to locomotion.agf, which the native 1.30 main graph references. Custom variables, speed groups and per-weapon clip mappings are merged into the new schemas, preserving new native content and IK bindings. The launcher copies nested workspace files and no longer runs the legacy .asi text patcher.

Preserved from v65: movement look-direction handoff, stationary head-only look and camera stops, idle shoulder correction, combat safeguards, locomotion speed/momentum logic, six stance icons and MMG/SNAFU loadout. No preview UI is added.

Extract into a fresh folder and launch Launch-Movement-Test.cmd. Current game animation clips must be extracted under D:\DayZProjects. Static migration/dependency/schema and PBO/ZIP checks passed; native DayZ compilation, graph loading and playback require local testing.
