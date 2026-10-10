#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v3'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v3_Turning_AB.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v3'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v3 turning A/B, based on Ctrl Modes v2; originals untouched',
    'controls':'Ctrl rising edge toggles walk/jog; held Shift temporarily sprints; release returns to saved mode',
    'brake_timer_source':'original v11 sprint/jog budgets and phase fractions; walking native stop retained',
    'mode_decreases':'sprint-to-walk shares v11 zero-target envelope down to gait 1, including partial sprint; original mission controls slowdown',
    'mocked_checks':'actual World/mission methods at 30/60/144 FPS and both callback orders; differential v11 stop and sprint-to-walk comparisons across directions, achieved speeds and exposure levels',
    'turning_comparison':'F8; starts original v2; responsive walk/jog direction and heading multipliers 1.6 versus 2.5; sprint filters unchanged',
    'native_compile_and_playtest':'pending local DayZ test',
}
if __name__=='__main__':packer.main()
