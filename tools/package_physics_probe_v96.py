#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v96'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Physics_Probe_v96.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v96 read-only physics probe; v93 one-infected baseline without failed v94/v95 proxy',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'NOT RUN: no native DayZ compiler/runtime in cloud',
 'purpose':'Automatic snapshots of human/infected fixture root and bone physics at spawn/death, now/100/300/1000/3000ms; does not implement zombie ragdoll',
 'limitations':'Physics introspection is declared in current SDK but native availability and bone enumeration meaning must be verified in-game. Counts alone do not establish articulated physics.',
 'checks':'Read-only probe source/API declaration checks; inherited fixture/movement bytes except the diagnostic call sites; PBO file/prefix/offset/hash verification and ZIP integrity'
}
if __name__=='__main__':packer.main()
