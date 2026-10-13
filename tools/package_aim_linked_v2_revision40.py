#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision40'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision40.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev40 restores native breathing/random sway and holdbreath; only ADS input-driven sight misalignment removed; movementbob/lean/recoil/rates retained','checks':'actualWorld getter/movement30/60/144FPSbothorders; actualADS dynamics fragment inputisolated and native bobretained; nativeaimfilter overrideabsent; nativecamera body equality afterpatch; native prototype names checked; sortedtemplate/graph/sourcechecks; PBO/ZIP','limitations':'Native compile/font/render/position stillneeds localtest; runtime widgets use nativeGUI APIs and no textures; priorbuilds preserved'}
if __name__=='__main__':packer.main()
