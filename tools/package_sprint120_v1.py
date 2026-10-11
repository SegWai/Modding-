#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabSprint120_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Sprint120_Test_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Corrected scroll v2 plus sprintlevel3 120%(36FPS); native100level2 and99 boundary tojog100 retained; six crouch levels unchanged','checks':'actual translated controller sprint limits/three walking profile combinations/100 repeated boundary cycles and inherited regressions; mapping/FPS/PBO/ZIP','limitations':'native compilation/playback/physical velocity and Windows preparation require in-game test; existing timer formulas unchanged'}
if __name__=='__main__':packer.main()
