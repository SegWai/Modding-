#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision45'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision45.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev45 RMBtap release<=200ms directADS; holding remainsnativehipfire; scopes/poses/speeds retained','checks':'actualWorld getter/movement30/60/144FPSbothorders; actualRMBmission taprelease<=200ms/holds/duplicatepress/UI/nativecallbacks; actualraiselatch/cancel/cleanup/stanceguards/sprintescape; actualzoomhandler and nativeopticswheelblock; standingcroaim blend1..4at30/60/144FPSbothorders; graph/sortedtemplate/sourcechecks; native prototype names checked; sortedtemplate/graph/sourcechecks; PBO/ZIP','limitations':'Native compile/font/render/position stillneeds localtest; runtime widgets use nativeGUI APIs and no textures; priorbuilds preserved'}
if __name__=='__main__':packer.main()
