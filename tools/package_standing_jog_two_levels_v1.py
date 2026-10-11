#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabStandingJog_TwoLevels_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Standing_Jog_Two_Levels_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Jogging wheel100% default/130% (39FPS); combines with unchanged standing walking~85/100/120 and crouch wheel; healthy upright whole-branch selection; no new UI messages','checks':'actual translated controller baseline and jogging wheel defaults/clamps/input isolation/persistence, six combined profiles; schema/mapping/FPS-only and PBO/ZIP checks','limitations':'native DayZ compilation/playback/travel speed/Windows preparation require local test; walking v3 was awaiting native confirmation; jogging phases of blends inherit selected pace, timer constants and sprint clips unchanged'}
if __name__=='__main__':packer.main()
