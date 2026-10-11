#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabStandingWalk_HalfSpeed_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Standing_Walk_Half_Speed_Test_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Approved Six Levels v4 plus F8 standing walk comparison: native 30FPS versus separate 15FPS variants; original clips preserved; root-motion retiming targets 50% pace and velocity','checks':'actual translated variant controller regressions and F8 graph selection at 30/60/144 FPS; schema/mapping/byte-retiming checks; package validation','limitations':'native DayZ compilation/animation/travel velocity and Windows preparation require local test; toggle can produce a one-time phase switch; healthy standing walk only'}
if __name__=='__main__':packer.main()
