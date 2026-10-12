#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision2'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision2.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Separate v2 revision2: fast80/native100/120; slow30/47/default60/73/native100; existing crouch tiers and native gun pose preserved','checks':'numbered tier/Ctrl/boundary/source/schema/scope preservation and controller tests; PBO/ZIP','limitations':'Native velocity and firing need test; 60default nowlevel3 after user clarified ascending order; original v2/v21 untouched'}
if __name__=='__main__':packer.main()
