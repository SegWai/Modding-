#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCamera_Cycle_v15'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Camera_Cycle_v15.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'V cycles default/wider third and first person: erect+.15m distance/+.05m height, crouch+.30m distance; v13 preserved','checks':'core movement, graphs, armed plan/preparation byte preservation; native camera API inspected; key press/release latch; PBO/ZIP','limitations':'Native camera collision/distance and Windows compilation require local test; native UAPersonView disabled during offline mission and restored on exit; first person/sights unchanged'}
if __name__=='__main__':packer.main()
