#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCrouch_PoseExit_v2'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_PoseExit_Test_v2.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Video-guided fast->87 direct pose blend weight fade.55s, independent of native gait request; clips forward/native ascent/velocity/standing rules unchanged','checks':'actual translated controller and independent animation-variable binding/monotonic blend/timer/cancel tests30/60/144FPS, inherited regressions; mapping/schema/PBO/ZIP','limitations':'native compilation/graph-expression evaluation/foot phase and visible transition need in-game test; no guaranteed phase transfer, speed requests unchanged'}
if __name__=='__main__':packer.main()
