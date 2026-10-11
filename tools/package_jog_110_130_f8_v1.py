#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabJog_110_130_F8_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Jog_110_130_F8_Test_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Top jogging level110% default(F8 OFF,33FPS) vs130%(F8 ON,39FPS); native jogging and linked walk/jog boundaries retained','checks':'translated actual controller F8 selection combinations plus inherited linked wheel regressions, schema/mapping/FPS and PBO/ZIP checks','limitations':'native compile/animation/velocity/Windows preparation require local test; mid-step F8 switching may reset clip phase once'}
if __name__=='__main__':packer.main()
