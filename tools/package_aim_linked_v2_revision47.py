#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision47'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision47.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev47 experimental firstpersonhipIK numeric response pair0.04/0.04; nativebranch/ADS/thirdperson/freelook/reload preserved; Rev46 camera retained','checks':'actualWorld getter/movement30/60/144FPSbothorders; actualhipIK selection gate/state guards; nativeIK exactbranch and onlynumericpair changed; camera/sway/ADS byte-identical; inheritedmovement harness excludes separatelytested gate; graph/sortedtemplate/sourcechecks; native prototype names checked; sortedtemplate/graph/sourcechecks; PBO/ZIP','limitations':'Native IK numeric parameter semantics/units not exposed; 0.04/0.04 response effectiveness and gun/hand alignment require game test; no speedup claim from static checks; priorRevision46 preserved'}
if __name__=='__main__':packer.main()
