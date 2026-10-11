#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCrouch_Descent_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Descent_Test_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Separate corrected scroll v2 test: fast crouch->87% requested gait blends achieved3..2 over.28s, then2..1 over.10s; ascent/graph/clips/standing unchanged','checks':'actual translated controller descent monotonicity/duration/timer ownership/reversal/cancellation and inherited regressions30/60/144FPS both callback orders; unchanged graph/preparer/mission; PBO/ZIP','limitations':'native compilation/phase/actual animation continuity require local test; this isolates blend timing and does not guarantee walking phase preservation'}
if __name__=='__main__':packer.main()
