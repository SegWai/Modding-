#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v8'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v8_Fixed_Turning.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v8'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v8: v7 crouch rules with preferred responsive body rotation permanently enabled',
    'crouch_rules':'slow without Shift; native fast Shift+movement; fast exit selects jog and consumes existing Shift hold; slow exit preserves previous standing mode',
    'standing':'v7 movement/crouch methods unchanged; preferred F8-on body heading setting is now permanent; no F8 handler or flag; F7 retained',
    'mocked_checks':'actual filter method matches v7 responsive setting across braking/stamina/profile states; F8 has no custom effect; World and movement helpers byte-identical to tested v7',
    'native_compile_and_playtest':'pending local DayZ test; no native animation/physics measurement',
}
if __name__=='__main__':packer.main()
