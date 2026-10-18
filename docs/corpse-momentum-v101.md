# v101 infected corpse momentum and initialization

The user confirmed v100 visibly renders the infected model with native ragdoll, but movement momentum is lost and initial poses sometimes appear on the floor. The supplied v100 logs show six creation/reveal events with the expected hermit model and PhysicsIsRagdoll=true. Each creation/reveal pair has the same timestamp: the prior build killed the new actor immediately, without waiting for its animated skeleton. No source velocity was transferred.

## Change

The living fixture slot samples world displacement at intervals of at least 20ms and at most 200ms, rejecting motion above 20m/s as a teleport/outlier. Before calling super.EEKilled, the tracked infected captures death position/orientation and native velocity. If native velocity is near zero or invalid, it uses the latest displacement velocity only if that sample is no older than 150ms. This keeps the moving body's direction and speed instead of sampling a corpse after native death processing.

The replacement is created hidden and collision-disabled at the captured location. It remains temporarily alive while native animation initializes its skeleton. A new frame and valid head/pelvis heights are required; initialization has a one-second timeout. No lookup failure is passed to a bone-position getter. Once ready, the original corpse is hidden/collision-disabled before the replacement is killed and ragdoll enabled. Its location is aligned once before activation, not teleported during physics. A half-second ragdoll activation timeout retains rollback to the original.

At activation, the replacement's collision layer is restored and a single impulse is applied: mass * (captured velocity - current velocity). This avoids both continuously pushing the corpse and adding velocity twice. If native mass is unusable, the verified human.ragdoll mass total73.9 is used. No fixed upward lift, random kick, or torque is added. The intent is to preserve the incoming motion, with subsequent movement left to native physics. Native propagation of this root impulse into the articulated body remains a gameplay check.

The one-zombie confirmed-death five-second respawn deadline is unchanged. Both warmup and active corpse representations are cleaned on respawn/shutdown. Failures restore the original collider/visibility. Existing human fixtures, player locomotion/camera, equipment and mission source are retained. Exact skeletal pose at death is not cloned; generic bone writers failed in the preceding tests. This addresses initialization and linear momentum, not complete animated limb-velocity/pose matching.

## Verification

Actual helper Start/Update/Stop and slot SampleMotion methods pass adapted C++ mocks: wait for a new initialized animation frame, no ragdoll during warmup, warmup timeout with untouched original, activation timeout rollback, one-shot mass-scaled delta-velocity, stationary target with zero added lift, subtraction of pre-existing velocity, no repeated impulses or teleports, cleanup idempotence, zero velocity after stopping and teleport rejection. These are logic checks, not native engine emulation or native Enforce compilation.

The packager verifies PBO entries, prefix, offsets, source bytes and SHA1 plus ZIP integrity. v100 native rendering is user-confirmed; v101's source and native impulse/warmup behavior still require the user's game run.

## Test

Extract MovementLab_Corpse_Momentum_v101.zip into a new folder and launch normally. Kill the infected while stationary, walking and running. Compare corpse travel direction/distance and whether it starts above ground normally. If anything remains wrong, run Collect-Logs.cmd after closing DayZ and send MovementLab-Corpse-v101-Logs.zip. New markers include death_capture, warming, activated, momentum and revealed; velocity, sample age, mass and impulse are recorded.
