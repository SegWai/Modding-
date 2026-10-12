#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCamera_Toggle_v14'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Camera_Toggle_v14.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'V toggles wider third person: erect+.15m distance/+.05m height, crouch+.30m distance; v13 preserved','checks':'core movement, graphs, armed plan/preparation byte preservation; native camera API inspected; key press/release latch; PBO/ZIP','limitations':'Native camera collision/distance and Windows compilation require local test; current native V binding not changed; first person/sights unchanged'}
if __name__=='__main__':packer.main()
