#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCrouchWheel_SixLevels'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Wheel_Six_Levels.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v1 controller with six crouch levels:9/14/18/22/26FPS and native fast','checks':'actual translated controller and structural source schema checks; native runtime pending','limitations':'native DayZ compilation/animation/Windows preparer unexecuted here; uses separate animation-table repair after v7 RPT'}
if __name__=='__main__':packer.main()
