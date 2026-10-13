#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision31'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision31.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev31 animtemplate alphabetical group index fixed; hiddencrouch7 nominal95% retimedfastcrouch viaequal28/29FPS blend; jog2/fullsprintraised-to-crouch entry only;1.5s momentumfade tolevel5;wheelmax6; prior speeds/bindings retained','checks':'actual-controller entry/fade/pose/gait/wheel tests30/60/144FPS both orders; graph scope and correctarmed/nativefastcrouch mappings; PBO/ZIP','limitations':'Native playback/velocity/compile pending;95% isblendedretimednativefastcrouch;level5relative toslowcrouchbase; prior builds preserved'}
if __name__=='__main__':packer.main()
