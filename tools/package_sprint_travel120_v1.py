#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabSprint_Travel120_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Sprint_Travel120_Test_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Corrected scroll v2 plus level3 physical horizontal displacement boost120% via OnPhysMove and CollisionMoveTest; native animations unchanged to isolate speed','checks':'actual translated callback120% arithmetic/height/collision/eligibility gates at30/60/144FPS; inherited actual controller regressions and unchanged clip/mission/graph bytes; PBO/ZIP','limitations':'native callback semantics/compilation/physical speed require local test; native animation pace retained so foot sliding possible; grounded offline fully achieved sprint only, boost disabled during braking'}
if __name__=='__main__':packer.main()
