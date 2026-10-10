#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v7'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v7_Crouch_Rules.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v7'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v7 copied directly from approved v4, not v5/v6; stable v4 untouched',
    'crouch_rules':'slow without Shift; native fast Shift+movement; fast exit selects jog and consumes existing Shift hold; slow exit preserves previous standing mode',
    'standing':'v4 startup/stop/filter timings retained; Ctrl toggle and new Shift sprint retained; only crouch-exit rule changes mode',
    'mocked_checks':'actual command/mission at 30/60/144 FPS and both callback orders, all four rules, eight direction masks, prior walk/jog, Shift release order, idle, brake interruption and exclusions; standing regressions and v11 differential stops pass; filter code matches v4',
    'native_compile_and_playtest':'pending local DayZ test; no native animation/physics measurement',
}
if __name__=='__main__':packer.main()
