#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCrouchWheel_SixLevels_v2'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Wheel_Six_Levels_v2.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'six unchanged crouch levels; shared L5 source at graph levels5/6 prevents immediate9FPS fallback while native gait filters','checks':'actual translated controller and structural source schema checks; native runtime pending','limitations':'native DayZ compilation/animation/Windows preparer unexecuted here; uses separate animation-table repair after v7 RPT'}
if __name__=='__main__':packer.main()
