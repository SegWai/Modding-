#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v10'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v10_Later_Walk_Blend.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v10'
packer.VALIDATION_EXTRA={
    'variant':'Ctrl Modes v10: v9 plus later walk entry: moving jog lead then smoothstep at existing deadline',
    'crouch_rules':'slow without Shift; native fast Shift+movement; fast exit selects jog and consumes existing Shift hold; slow exit preserves previous standing mode',
    'standing':'Ctrl jog-to-walk curve only changed: 0.12s moving jog then 0.30s blend within same 0.42s full-jog budget; permanent responsive body heading and no F8 toggle retained',
    'mocked_checks':'actual translated World/mission checks at 30/60/144 FPS; jog-to-walk versus v9 retains initial jog, then has higher early gait, monotonic easing and same completion tick/deadline; standing/crouch/full-stop/sprint-return regressions pass; filters unchanged from v8',
    'native_compile_and_playtest':'pending local DayZ test; no native animation/physics measurement',
}
if __name__=='__main__':packer.main()
