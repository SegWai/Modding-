#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Walk_v19'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Walk_v19.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'V13 base; aimed walking only, scoped leaf retiming preserving native gun aim/ADS layers; standing65/75/85/native100 targets; crouch30/47/60/73/87','checks':'native upper-body and all other graph node preservation; structural scope and slot mapping tests; controller tests; PBO/ZIP','limitations':'integer FPS means standing66.7/76.7/86.7 actual ratios; native playback/gun orientation/shooting must be tested'}
if __name__=='__main__':packer.main()
