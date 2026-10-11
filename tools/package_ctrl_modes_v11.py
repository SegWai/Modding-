#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v11'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v11_Reversal_Resistance.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v11'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v11: v10 plus jogging lateral reversal resistance; not historical Movement Logic v11',
    'resistance':'native non-sprint direction multiplier 2.5 to 7.0 after jogging opposite A/D inputs; 0.50s smooth decay; short neutral gaps covered',
    'exclusions':'walk, sprint request, crouch, startup, braking, aiming/gestures/UI; no speed/angle override or clip restart added',
    'preserved':'v10 permanent responsive heading, Ctrl jog-walk lead, crouch rules, full-stop/sprint-return timers',
    'mocked_checks':'actual tracker/movement at 30/60/144 FPS in both callback orders; side/diagonal/spam/neutral-gap/decay tests and standing/crouch regressions; actual filter output differential changes direction only',
    'native_compile_and_playtest':'pending local DayZ test; no native animation/path/physics measurement',
}
if __name__=='__main__':packer.main()
