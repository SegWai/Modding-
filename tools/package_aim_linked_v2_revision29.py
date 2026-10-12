#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision29'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision29.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev29 Jog2->crouch6 native fast pose ->crouch5~87 momentum fade1.5s; synchronized smoothstep gait and pose; wheel locked; other Revision28 speeds/bindings unchanged','checks':'actual-controller crouch fade30/60/144FPS both orders; pose monotonic/gait/wheel bounds and entry exclusions; existing standing/aim/controller and source graph checks; PBO/ZIP','limitations':'Native compile/feel pending; native fast crouch and slow87 are different base animations; prior builds preserved'}
if __name__=='__main__':packer.main()
