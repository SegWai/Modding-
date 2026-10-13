#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabHUDIcons_v2'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_HUD_Icons_v2.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'fix v1 native Mission compile failure:24 individual PAA resources; no SetUV or multidimensional UV arrays',
 'checks':'actual read-only accessor and HUD C++ mock tests;24 native PAA headers/mip chains; independent decode; movement/mission identity; PBO bytes/footer',
 'limitations':'DayZ Enforce compiler and native renderer unavailable in cloud. Previous C++ validation failed to predict v1 native SetUV type rejection; that interface is completely removed, not claimed verified by the mocks.'
}
if __name__=='__main__':packer.main()
