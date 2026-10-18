#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v100'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Configured_Corpse_v100.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v100 infected-model Human-physics corpse configured at native creation; v93 baseline',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'NOT RUN: native rendering, class creation and ragdoll need user test',
 'purpose':'Native configured Human corpse representation with infected P3D, no generic bone writes or post-creation SetObject',
 'limitations':'Corpse replacement, not native infected-controller ragdoll. Configured full-body infected model with Human physics remains an experiment; class/model/runtime checks do not prove visible articulation.',
 'checks':'Configuration/asset/API inspection; replacement lifecycle tests; PBO source/prefix/offset/hash verification and ZIP integrity'
}
if __name__=='__main__':packer.main()
