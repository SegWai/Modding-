#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v9'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v9_Jog_Walk_Momentum.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v9'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v9: v8 plus Ctrl jog-to-walk smoothstep momentum at existing deadline',
    'crouch_rules':'slow without Shift; native fast Shift+movement; fast exit selects jog and consumes existing Shift hold; slow exit preserves previous standing mode',
    'standing':'Ctrl jog-to-walk curve only changed; same timers and endpoints; permanent responsive body heading and no F8 toggle retained',
    'mocked_checks':'actual translated World/mission checks at 30/60/144 FPS; jog-to-walk versus v8 has higher early gait, monotonic easing and same completion tick/deadline; standing/crouch/full-stop/sprint-return regressions pass; filters unchanged from v8',
    'native_compile_and_playtest':'pending local DayZ test; no native animation/physics measurement',
}
if __name__=='__main__':packer.main()
