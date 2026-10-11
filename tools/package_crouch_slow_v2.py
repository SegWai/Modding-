#!/usr/bin/env python3
"""Package a separate original-v11 Ctrl/Shift mode test."""
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_CrouchSlow_v2'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Slow_Test_v2.zip'
packer.ARCHIVE_ROOT='MovementLabCtrlModeTest_CrouchSlow_v2'
packer.VALIDATION_EXTRA={
 'variant':'Stable v10 Strafe v2 plus slow-crouch physical horizontal translation scale 0.20; normal gait retained',
 'resistance':'pure A/D reversal gait 0.15; repeated switches keep slow; steady direction >0.30s then 0.08s smooth recovery; no angle override',
 'checks':'actual translated scripts, v10 regression, spam/stable-hold/release and Shift at 30/60/144 FPS both callback orders',
 'native_compile_and_playtest':'pending local DayZ test; physical callback displacement reduced 80% in mock; native callback semantics and game velocity unverified',
}
if __name__=='__main__':packer.main()
