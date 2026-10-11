#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabScroll_JogSprint_v2'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Scroll_Jog_Sprint_v2.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Jog79 boundary to defaultwalk85, defaultjog80 level2/native100 level3, jog101 level4 trigger to native sprint100, sprint99 trigger back to jog100; scroll sprint uses original turbo braking envelope; walking121 now enters defaultjog80','checks':'actual translated controller and mission regression plus repeated jog/sprint switches, native sprint without Shift, exposure/full-stop/crouch and Ctrl clearing; schema/FPS/PBO/ZIP','limitations':'native DayZ compilation/animation/travel speed and Windows preparation require local test;101/99 are mode triggers not separate clips'}
if __name__=='__main__':packer.main()
