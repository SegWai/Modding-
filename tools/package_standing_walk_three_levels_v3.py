#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabStandingWalk_ThreeLevels_v3'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Standing_Walk_Three_Levels_v3.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'V3 full healthy upright branch selection (59 cloned nodes) replaces six leaf selectors; walking UI messages removed and log diagnostics added; Standing walking wheel~85% target (26/30=86.67%), native100%,120% (36 FPS); default and crouch-exit walk selection~85%; F8 removed; existing gait mode rules and crouch wheel preserved','checks':'translated actual controller standing tier clamps/default/reset/independent crouch input and baseline regressions; schema and FPS-only mutation; PBO and ZIP validation','limitations':'native DayZ compilation, Windows preparation and actual root-motion velocity/animation require local test; FPS is integer so first tier approximates85%; walk level reset does not force previously jogging mode to walk'}
if __name__=='__main__':packer.main()
