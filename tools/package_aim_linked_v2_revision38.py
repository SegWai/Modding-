#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision38'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision38.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev38 crouch3 enters aimingcro3; low tiers1/2 persist on entry/exit; higher aim exit returnsdefault4; priorHUD and speeds retained','checks':'actualWorld getter/movement30/60/144FPSbothorders; actualHUDInit/Update translatedwidgetmock:5cells/visibility/selection/auto/placement/duplicates/failure; sortedtemplate/graph/sourcechecks; PBO/ZIP','limitations':'Native compile/font/render/position stillneeds localtest; runtime widgets use nativeGUI APIs and no textures; priorbuilds preserved'}
if __name__=='__main__':packer.main()
