#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Speeds_v18'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Speeds_v18.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Fix aiming graph scope and offline inventory diagnostic plugin registration; V13 base; raised walking/jogging scroll tiers and five slow aimed crouch tiers; native aim/ADS/fire layers preserved','checks':'raised instance inheritance and source-specific retiming plans; template/graph references and bounds; controller regressions; PBO/ZIP','limitations':'Native aiming gait caps, ADS visual continuity and shooting require user test; no V cycle or wider camera changes'}
if __name__=='__main__':packer.main()
