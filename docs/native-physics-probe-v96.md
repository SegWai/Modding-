# Native physics probe v96

The XOB comparison found effectively identical transforms for all 11 shared physical bones. The unresolved question is whether the native infected instance exposes physical bone bodies. v96 makes that question testable without asking the user to operate Workbench/debuggers.

## Run

Extract MovementLab_Physics_Probe_v96.zip to a fresh folder, launch with Launch-Movement-Test.cmd, kill the jogging male human and the one infected 20m ahead. Wait at least four seconds after each death, close DayZ, run Collect-Logs.cmd and upload MovementLab-Physics-v96-Logs.zip. Compile-error/crash logs are also useful because each native inspection stage has a marker.

The package uses v93's native infected baseline. v94/v95 hidden-human/model-swap experiments are absent. Existing human targets, loadout, movement, grenade/car rules and confirmed-death respawn timers are unchanged. Only the new read-only probe and its calls at human/infected spawn/death differ in gameplay source. No arbitrary simulation toggles or guessed ragdoll config properties were added.

Snapshots run immediately and at 100, 300, 1000 and 3000ms. They log entity type/life state, Human.PhysicsIsRagdoll (human only), root GetPhysics, GetNumBones, and up to 32 physical bone handles with dynamic/kinematic flags. Counts outside 0–256 are rejected. Multiplayer is excluded. GetBone enumeration has no proven correspondence to animation bone indexes; the code does not assume one.

The new APIs are declared in the official current SDK. Their availability/meaning in the actual game executable remains an in-game test; the cloud has no native compiler/runtime. No successful native compilation or ragdoll result is claimed by the package checks.

## Interpret evidence

Run `python tools/analyze_physics_probe.py MovementLab-Physics-v96-Logs.zip --output physics-report.json`.

- Human ragdoll exposes multiple physical bones, infected exposes zero: existing-bone activation is not supported by this observation. Investigate creation/loading of a separate articulated physics object and visible skinning ownership. Do not repeat a Human cast on an infected or fake impulse death animation.
- Infected exposes multiple physical bones: inspect their dynamic/kinematic states and animation ownership. This supports a focused activation experiment, not a claim that changing simulation state alone will work.
- Human positive control absent, calls unavailable or snapshots incomplete: fix the instrumentation/API compatibility first. No conclusion about an infected rig is justified.

If the last marker stops before GetPhysics/GetNumBones/GetBone, identify that operation from the logs before attempting further native calls. A returned zero only describes this API's exposed instance; it does not prove that the closed engine can never instantiate another physics representation.

## Validation

Seven checks pass: missing/incomplete data, required positive human control, absent versus multiple infected bodies, no false ragdoll success, read-only native API declaration checks, unchanged baseline files and removal of diagnostic call lines restoring original fixture source. Packaging independently verifies PBO entries/prefix/offsets/source bytes/SHA1 and ZIP integrity. These checks do not substitute for the user's native run.
