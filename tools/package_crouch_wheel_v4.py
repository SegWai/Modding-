#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCrouchWheel_v4'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Wheel_Test_v4.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'timed graph pose blends at 0.18s; 5 levels/sec downward pace; v1 upward selection retained','evidence':'v3 RPT original unarmed clips missing under shared-prefix package','checks':'translated actual wheel/controller checks passed at 30/60/144 FPS both orders; graph/group/path consistency and resource brace balance checked','limitations':'Windows PowerShell preparer and DayZ native playtest unexecuted here; original source assets required locally'}
if __name__=='__main__':packer.main()
