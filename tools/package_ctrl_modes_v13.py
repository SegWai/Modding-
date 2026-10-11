#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v13'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Ctrl_Modes_v13_Lateral_Momentum.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_v13'
packer.VALIDATION_EXTRA={
 'variant':'Ctrl Modes v13: pure lateral jogging signed momentum',
 'resistance':'signed gait -2 to +2 slew at 9/second; temporary lateral angle override; no command restart or frozen pose',
 'preserved':'existing standing/crouch/toggle/start/stop logic; previous versions retained',
 'checks':'translated actual scripts at 30/60/144 FPS both callback orders; signed crossing delay, spam slew limit, recovery and release; mission helper/filter regressions',
 'native_compile_and_playtest':'pending local DayZ test',
}
if __name__=='__main__':packer.main()
