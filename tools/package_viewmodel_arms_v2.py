#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True
import package_movement_logic_test as packer
packer.SOURCE = packer.ROOT / 'viewmodel-prototype/MovementLabArmsOnlyTest_v2'
packer.OUTPUT = packer.ROOT / 'artifacts/MovementLab_Arms_Only_Test_v2.zip'
packer.ARCHIVE_ROOT = packer.SOURCE.name
packer.VALIDATION_EXTRA = {
 'variant':'Revision49 movement plus static arms-only MLOD model and independent ItemPreview widgets; external installed SNAFU Weapons loadout',
 'checks':'Blender geometry isolation, MLOD export/reimport; unchanged movement controller regression; controller ownership/fallback mocks; package PBO bytes/footer',
 'limitations':'Not a complete animated viewmodel. Native compilation/rendering/model framing and gun alignment untested. Separate UI item cameras have independent depth. Native actions and ADS fall back. SNAFU classes discovered from installed config; role recognition depends on names. No SNAFU assets included.'
}
if __name__ == '__main__':
    packer.main()
