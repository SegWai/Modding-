# v97 result and correction

The supplied runtime logs show that POSTFRAME ran successfully: each recorded corpse received hundreds of callback frames, both write phases were reached and each probe finished. The user's observation is native death animation only, with no head marker.

Every captured transform position and readback was zero. SetBoneMatrix returned false and GetBoneMatrix returned false. SetBoneGlobal has no success return; its execution is not evidence of success.

Two test defects prevent treating this as proof that infected skeletal writes are impossible:

1. v97 used Entity.GetBoneIndex, documented as the skeleton bone index of a named **proxy selection**. DayZInfected inherits DayZCreatureAI, which inherits DayZCreature. DayZCreature declares GetBoneIndexByName in dayzanimal.c. Earlier investigation missed that inherited method. v98 uses this proper skeletal lookup and logs the proxy index only for comparison. The returned indexes may or may not differ; that is a native test, not an assumed result.
2. v97 passed a matrix read into zero-initialized storage even though its basis was zero. A rejected invalid matrix does not test whether a valid transform would be accepted. v98 checks all three basis lengths. If matrix reading fails but GetBonePositionMS supplies a nonzero position, it uses an identity basis at that skeletal position for the temporary marker. If neither is available, it aborts without writes. Identity is intentionally a calibration pose, not preserved head orientation or a ragdoll pose.

The corrected test still separates SetBoneMatrix and SetBoneGlobal phases, uses a bounded nonaccumulating head offset, leaves simulation enabled and introduces no human proxy. Source declarations/guards and unchanged fixture hooks have been checked. PBO and ZIP bytes/structure are verified by packaging. Native v98 compilation and visible skinning remain untested in the cloud.

Extract v98 to a new folder, launch, kill the one zombie, watch the head for four seconds and report any unusual head movement. Close DayZ and use Collect-Logs.cmd to create MovementLab-Bone-v98-Logs.zip. This is a correction of the experiment's invalid inputs, not a claim of a working infected ragdoll.
