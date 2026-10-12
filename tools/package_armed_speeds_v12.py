#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabArmedSpeeds_v12'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Armed_Speeds_v12.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Weapon/item instance overrides propagated into custom speed groups; source-specific retimed clips and armed crouch level1 native fallback correction','checks':'129 instance inheritance resolution,11 override providers,294 clip variant plans; per-row native pose source preservation; World/mission byte preservation; PBO/ZIP','limitations':'Native Windows clip preparation and weapon grip/playback require user test; raised-aim graph branches remain native; original game files read only; earlier versions preserved'}
if __name__=='__main__':packer.main()
