#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision48'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision48.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev48 firsthip worldyaw bodyorientation+baseLR appliedonce; no engineheadingdoubleaddition; nativeIK restored; sway/recoil/ADS retained','checks':'actualWorld getter/movement30/60/144FPSbothorders; actualhipworldyaw sameasnativeweapon construction; negativecontrolpreviousdoubleheading; bodylagtargettests30/60/144FPS; shake/gates; nativeIK restored; inheritedmovement/stanceblend checks; native prototype names checked; sortedtemplate/graph/sourcechecks; PBO/ZIP','limitations':'Camera coordinate correction verified in mocks; native rendering/gunprojection/aimfeel/shooting alignment require game confirmation; original IK and priorversions preserved'}
if __name__=='__main__':packer.main()
