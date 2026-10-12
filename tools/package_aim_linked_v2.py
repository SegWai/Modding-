#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Separate v2; native slow/fast aim modes, slow10/native100, fast30/native100; linked101/99 boundaries; existing crouchaim tiers preserved','checks':'controller boundary/Ctrl/raised stance tests; upper-body/source/mapping/scope checks; PBO/ZIP','limitations':'Native gait/velocity and aim/firing need user validation; percentages interpret90/70 slower as10/30 native; v21 untouched'}
if __name__=='__main__':packer.main()
