#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabScroll_TargetQueue_v9'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Immediate_Scroll_Targets_v9.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Limit downward pose handoff rate when entering walking; single Mission frame action-edge wheel capture; no raw polling/simulation fallback; v7 levels and smoothing retained','checks':'one edge one level; persistent raw state ignored; rapid event queue; momentum retarget and inherited controller regressions30/60/144FPS both callback orders; graph preservation/PBO/ZIP','limitations':'native action-edge delivery during fast bursts and native compilation require local test; confirmed default preserved'}
if __name__=='__main__':packer.main()
