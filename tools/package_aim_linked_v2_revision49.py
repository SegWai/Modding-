#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision49'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision49.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev49 restore nativefirstcamera and passivehip diagnostics; removes experimental46-48 cameraoverrides; allothercontrols/speeds/poses retained','checks':'actualWorld getter/movement30/60/144FPSbothorders; passivecamera observer cannotwriteoutput/angles/input; inheritedmovement/stanceblends30/60/144FPS; nativeIK/config/sourcechecks; native prototype names checked; sortedtemplate/graph/sourcechecks; PBO/ZIP','limitations':'Restores nativecamera; fullfixedweaponperspective remains unresolved and requires nativevisual/input data; priorversions preserved'}
if __name__=='__main__':packer.main()
