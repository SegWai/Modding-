# v96 native results and v97 bone-write experiment

The user's 18 October 2026 runtime upload contains 35 complete probe snapshots, no unfinished probe stages, five active-human-ragdoll death snapshots and five dead-infected snapshots. All five Human samples report PhysicsIsRagdoll=true. GetNumBones returns zero for both throughout. Root physics was present in both; both root flags report dynamic=true and kinematic=true. These flags must not be treated as mutually exclusive indicators of an articulated rig.

The v96 probe compiled and ran on the user's game. Its *inspection route* did not discriminate the working human ragdoll from the infected. This is not evidence that the infected has no internal bodies or that ragdoll is impossible. Repeating enumeration or trying to enable the nonexistent returned bone handles is not justified. The analyzer now explicitly recognizes this actual result; eight regression checks pass.

## Next test: v97

A custom jointed ragdoll needs two working components: a physical simulation and a visible mesh whose bones follow that simulation. v94 failed to establish the latter. Its animation-copy attempt used mission-update timing and disabled simulation on the infected. v97 isolates mesh writing with simulation left enabled and writes in the entity's POSTFRAME callback. This is a different timing/ownership test, not a repetition of the hidden-human proxy.

The one tracked zombie is unchanged while alive. After confirmed death, v97 enables POSTFRAME and finds the Head bone. Between 300–1800ms it tries SetBoneMatrix; between 1800–3300ms it tries SetBoneGlobal. Each mode is separate. The cached baseline plus a bounded sinusoidal 0–0.35-model-unit vertical offset prevents cumulative drift. The write returns/readbacks and frame count are logged. Writes stop at 3300ms; normal five-second corpse replacement remains unchanged. It does not add a human body, forces, a guessed physics resource or a new death animation.

This is an intentionally obvious head-movement calibration, **not** a ragdoll implementation. A write return/readback alone does not establish visible skinning; the user must report whether the head visibly moves in either phase. If accepted writes remain invisible, joint simulation would not solve the rendering problem and should not be built on that assumption. If writes visibly work, the next implementation can drive an infected visual from custom physical joints without relying on the unavailable Human ragdoll entry point. That path still needs its own native tests.

## User steps

Extract MovementLab_Bone_Probe_v97.zip into a new folder, launch normally, kill the one zombie and watch its head for four seconds. Close DayZ and run Collect-Logs.cmd. Send MovementLab-Bone-v97-Logs.zip and whether the head visibly moved/stretched upward. If native compilation fails, send the error/logs; no native compilation or rendering success is claimed in advance.

## Validation

Native signatures checked against the same official SDK revision used for v96. Code keeps simulation enabled, has no human proxy and only acts on the dead offline fixture. Existing player movement, human targets, loadout and respawn source remain inherited. PBO source/prefix/offset/footer verification and ZIP integrity run during packaging. This is source/package validation, not an engine playtest. Raw user logs are kept private; the committed JSON contains only relevant diagnostic fields.
