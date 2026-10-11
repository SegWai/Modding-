#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabStandingScroll_ModeLinks_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Standing_Scroll_Mode_Links_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Walking fourth121% notch -> native jogging100% level2; jogging lowest99% notch -> walking120% level3; jogging130 retained as level3; single standing wheel reader, existing mode transition logic','checks':'actual translated controller boundary transitions, per-notch ownership,100 rapid alternation cycles/default/reset/idle/exclusions and inherited regressions; unchanged animation/preparer bytes; PBO/ZIP checks','limitations':'121/99 are immediate mode boundaries, not retimed clips; native DayZ compilation/animation/velocity require local test; standing walking default remains~85% and native sprint still uses Shift'}
if __name__=='__main__':packer.main()
