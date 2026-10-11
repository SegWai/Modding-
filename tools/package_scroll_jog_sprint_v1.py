#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabScroll_JogSprint_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Scroll_Jog_Sprint_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Jog80/100, jog101 trigger to native sprint100, sprint99 trigger back to jog100; scroll sprint uses original turbo braking envelope; replaces previous110/130 comparison','checks':'actual translated controller and mission regression plus repeated jog/sprint switches, native sprint without Shift, exposure/full-stop/crouch and Ctrl clearing; schema/FPS/PBO/ZIP','limitations':'native DayZ compilation/animation/travel speed and Windows preparation require local test;101/99 are mode triggers not separate clips'}
if __name__=='__main__':packer.main()
