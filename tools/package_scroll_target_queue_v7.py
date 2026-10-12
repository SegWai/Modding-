#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabScroll_TargetQueue_v7'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Immediate_Scroll_Targets_v7.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Walking80/native100 with level3 transition to jog80; former120 removed; v6 pose easing and momentum retained; preserve frame wheel capture; count raw wheel deltas, process all notches against selected target across standing/crouch boundaries; animations independently catch up; confirmed broad smoothing graph unchanged','checks':'actual translated raw notch/120-unit burst/clamp/dedup/menu/queued target and no-more-input settle tests plus inherited movement/pose regressions30/60/144FPS both orders; byte preservation/PBO/ZIP','limitations':'native wheel sign/units/capture/compilation and visuals require local test; default PoseExitv2 preserved; prior corrected v2 downward jog80->walk85 rule retained'}
if __name__=='__main__':packer.main()
