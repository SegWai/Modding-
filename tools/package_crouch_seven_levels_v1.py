#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCrouch_SevenLevels_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Seven_Levels_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Crouch30/~47/60(default)/~73/~87/~95(29FPS=96.67%)/nativefast level7; native Shift and sprint entry retargeted7; latest standing scroll rules preserved','checks':'translated actual controller and existing standing/crouch regression tests with seven levels; schema/mapping/PBO/ZIP','limitations':'native compile/playback/velocity and Windows preparation require local test;95% rounds to96.67%; native fast crouch separate gait'}
if __name__=='__main__':packer.main()
