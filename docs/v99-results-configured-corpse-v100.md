# v99 result and configured-corpse experiment v100

The user's v99 logs contain three completed probes (417, 397 and 431 frames). All used a nonzero animated head transform and the compact model index41 for the generic writer. SetBoneMatrix and GetBoneMatrix still returned false in each attempt. The user observed no head movement. SetBoneGlobal's void return cannot be described as acceptance; model readbacks did not match requested positions. Together with v98, neither tested identifier establishes generic bone writes on the native infected. No more variation of that approach is built here.

## Different route

v100 bases gameplay on v93, removing the v94/v95 driver/model-swap experiments and v96–99 probes. It declares a new CfgVehicles class derived from SurvivorM_Denis, with the infected hermit P3D, selections, texture and material configured **before native creation**. The accompanying script class derives from SurvivorBase. This selects Human simulation through normal class inheritance and the infected model through its configured model field.

This is justified as an experiment by the supplied assets: human and infected compiled skeleton tables match, and all 11 physical bone transforms agree closely. It remains unknown whether native creation/animation/physics will skin the full infected model correctly. It is not enough to assume that a shared skeleton guarantees success.

After a confirmed zombie death, the manager attempts one configured corpse creation, calls the already-working Human ragdoll API and checks the actual GetShapeName plus ragdoll state. Only a hermit model with active ragdoll is revealed. The original infected is then hidden and collision-disabled; the configured corpse is visible. No hidden human is used as a bone driver, no SetObject or generic skeletal writes are called, and no extra living NPC fixture is added. Native living infected AI remains unchanged.

This is **corpse replacement**, not articulated physics activated on DayZInfected. The visual model, motion and seamlessness require local testing. The native pose at death is not copied because those bone writers failed; an initial pose change remains a possible limitation. No corpse loot transfer is implemented in this range experiment. Appearance matching alone is not evidence of complete production-ready replacement behavior.

Creation/cast failure, a native model mismatch or activation timeout leaves the original corpse. Cleanup removes the configured corpse and restores the original before the normal manager deletes it and respawns the one living infected five seconds after confirmed death. There is one attempt per death and no periodic orphan spawning. Mission/player movement, existing human fixtures, loadout, grenades and car code are retained from v93.

## Test

Extract MovementLab_Configured_Corpse_v100.zip into a new folder, launch normally, kill the one zombie and observe whether the visible zombie model falls with independently moving limbs. Close DayZ and run Collect-Logs.cmd. Send MovementLab-Corpse-v100-Logs.zip and the visible result, including if a human/naked body appears or no replacement occurs. Shape/ragdoll log checks alone cannot certify the visible result.

## Verification

The actual helper Start/Update/Stop/Visibility methods pass adapted C++ lifecycle mocks for successful activation, wrong mesh, activation timeout, null/wrong-class creation, living/multiplayer guards and repeated cleanup. These test ownership/rollback logic only; they do not compile Enforce or emulate native model loading. Configuration references match the supplied hermit model/selection assets, dependencies include DZ_Characters and DZ_Characters_Zombies, and the mission file is byte-identical to v93. Packaging checks PBO entries/prefix/offsets/source bytes/SHA1 and ZIP integrity. Native compilation, rendering and Human-physics binding of the configured model remain unverified until the user's game run.
