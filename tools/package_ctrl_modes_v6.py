#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v6'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v6_Fast_Crouch_Fix.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v6'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v6 restores native fast crouch after v5 cap; approved stable v4 untouched',
    'controls':'standing Ctrl toggles walk/jog; standing Shift sprints; crouch uses uncapped native Shift behavior; valid crouch exit selects persistent standing jog until Ctrl',
    'brake_timer_source':'original v11 sprint/jog budgets and phase fractions; walking native stop retained',
    'mode_decreases':'sprint-to-walk shares v11 zero-target envelope down to gait 1, including partial sprint; original mission controls slowdown',
    'mocked_checks':'actual World/mission methods at 30/60/144 FPS and both callback orders; differential v11 stop and sprint-to-walk comparisons across directions, achieved speeds and exposure levels',
    'turning_comparison':'F8; starts original v2; responsive walk/jog body heading multiplier 1.6 versus 2.5; direction and sprint filters unchanged',
    'direction_regression':'previous v3 reproduces repeated startup when achieved gait dips during held rear diagonals; v4 passes; no live steering angle lock or repeated mode brake',
    'prior_v5':'user reported fast crouch was lost; fixed by removing gait-2 cap',
    'crouch_checks':'actual translated methods, both callback orders at 30/60/144 FPS; no crouch speed/angle ownership each frame; v5 fails and v6 passes; raw native-input fallback, direction masks, idle, all Shift/stance release orders, brake interruption; filters unchanged from v4',
    'native_compile_and_playtest':'pending local DayZ test',
}
if __name__=='__main__':packer.main()
