#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v99'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Bone_Probe_v99.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v99 infected head render-bone write calibration; no human proxy',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'NOT RUN: user native visual test required',
 'v96_runtime':'User logs confirm complete human/infected death snapshots. Human PhysicsIsRagdoll=true, but GetNumBones=0 for both. Enumeration not a useful articulated-rig discriminator.',
 'purpose':'Read valid animated transform with skeletal identifier, test generic bone writes with compiled-model index, then check visible head bone writes in POSTFRAME with native simulation enabled before implementing custom infected physics',
 'v97_runtime':'Bone callback ran 209-428 frames per corpse; proxy index41, all-zero transforms, SetBoneMatrix=false, GetBoneMatrix=false. Test had invalid inputs; cannot infer bone-control impossibility.',
 'v98_runtime':'Valid animated head transform with skeletal identifier2090324343; model lookup41. SetBoneMatrix/GetBoneMatrix reject animation identifier. Generic writer identifier contract not established.',
 'checks':'Bounded-offset/cached-baseline tests; SDK signature inspection; source/package checks; PBO prefix/file bytes/offsets/SHA1 and ZIP integrity',
 'limitations':'SetBoneMatrix/GetBoneMatrix success and readback do not guarantee visible skinning. Inferred matrix semantics and native render timing require visual validation; not a finished ragdoll.'
}
if __name__=='__main__':packer.main()
