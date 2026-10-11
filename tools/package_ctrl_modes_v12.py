#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v12'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v12_Strafe_Resistance.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v12'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v12: v11 plus pure-strafe gait resistance; not historical Movement Logic v11',
    'resistance':'pure A/D jogging reversals use continuous gait request toward 1.1 with bounded 5 down / 3.5 up per second; 0.50s resistance decay; no forward-speed threshold',
    'exclusions':'walk, sprint request, crouch, startup, braking, aiming/gestures/UI; continuous pure-strafe speed request; no angle override or clip restart',
    'preserved':'v10 permanent responsive heading, Ctrl jog-walk lead, crouch rules, full-stop/sprint-return timers',
    'mocked_checks':'actual tracker/movement at 30/60/144 FPS in both callback orders; side/diagonal/spam/neutral-gap/decay tests and standing/crouch regressions; actual filter output differential changes direction only',
    'native_compile_and_playtest':'pending local DayZ test; no native animation/path/physics measurement',
}
if __name__=='__main__':packer.main()
