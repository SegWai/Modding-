#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAllPoseSmoothing_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_All_Pose_Smoothing_Test_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Broad locomotion smoothing test from confirmed PoseExitv2: walk/jog/sprint weights, independent walking/jog/crouch wheel profile blends, all crouch fast exits, lateral poses, stance/direction/start/stop graph edges','checks':'translated actual controllers and pose variable bounds/monotonic profile/lateral/crouch cases plus inherited regressions30/60/144FPS;99 graph changes and schema/PBO/ZIP','limitations':'native compile/visuals/phase/root-motion effects require local test; unrelated combat/actions/vehicles unchanged; F7 input comparison does not undo every graph window; confirmed default artifact preserved'}
if __name__=='__main__':packer.main()
