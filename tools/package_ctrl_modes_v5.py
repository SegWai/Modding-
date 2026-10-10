#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v5'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v5_Crouch_Jog.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v5'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v5 crouch rule on approved v4; stable v4 untouched',
    'controls':'standing Ctrl toggles walk/jog; standing Shift sprints; crouched Shift requests jog; valid crouch exit selects persistent standing jog until Ctrl',
    'brake_timer_source':'original v11 sprint/jog budgets and phase fractions; walking native stop retained',
    'mode_decreases':'sprint-to-walk shares v11 zero-target envelope down to gait 1, including partial sprint; original mission controls slowdown',
    'mocked_checks':'actual World/mission methods at 30/60/144 FPS and both callback orders; differential v11 stop and sprint-to-walk comparisons across directions, achieved speeds and exposure levels',
    'turning_comparison':'F8; starts original v2; responsive walk/jog body heading multiplier 1.6 versus 2.5; direction and sprint filters unchanged',
    'direction_regression':'previous v3 reproduces repeated startup when achieved gait dips during held rear diagonals; v4 passes; no live steering angle lock or repeated mode brake',
    'crouch_checks':'actual translated methods, both callback orders at 30/60/144 FPS; direction masks, idle, Shift-release order, Ctrl held across stance change, brake interruption, prone/disabled paths; filters unchanged from v4',
    'native_compile_and_playtest':'pending local DayZ test',
}
if __name__=='__main__':packer.main()
