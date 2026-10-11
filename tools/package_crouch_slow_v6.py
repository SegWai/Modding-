#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_CrouchSlow_v6'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Slow_Test_v6.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'stable controller plus local complete unarmed folder repack; six FPS 30 to 6 changes','evidence':'v3 RPT original unarmed clips missing under shared-prefix package','limitations':'Windows PowerShell preparer and DayZ native playtest unexecuted here; original source assets required locally'}
if __name__=='__main__':packer.main()
