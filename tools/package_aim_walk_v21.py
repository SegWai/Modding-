#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Walk_v21'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Walk_v21.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Fix native raised stance3/4 eligibility and crouch classification; same scoped walking tiers and native gun pose layers','checks':'actual raised3/4 controller tests30/60/144FPS both orders; graph/clip/mission preservation; PBO/ZIP','limitations':'Native effect of clip retiming, gun orientation and firing still require local test; debug logging retained'}
if __name__=='__main__':packer.main()
