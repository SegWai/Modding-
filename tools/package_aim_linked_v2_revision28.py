#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision28'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision28.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev27 slow aim55/100/150 at17/30/45FPS; walking73 at22FPS; walk1->aim2 walk2->aim3; jog/sprint->walk1 smoothstep1.5s; AltADS anddoubleShiftaimexit retained; noNPCs','checks':'actual-controller mode/tier/momentum tests30/60/144FPS both orders; native ADS-body preservation/toggle checks; armed source mappings and PBO/ZIP','limitations':'Native compile/velocities/ADS camera/fire need local test; percentages rounded to whole FPS; prior versions preserved'}
if __name__=='__main__':packer.main()
