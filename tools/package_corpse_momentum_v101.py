#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v101'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Corpse_Momentum_v101.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v101 v100 confirmed infected-model corpse with pre-death motion sampling, skeleton warmup and one-shot momentum transfer',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'v100 confirmed working by user; v101 native changes NOT RUN in cloud',
 'purpose':'Carry movement into corpse physics and avoid activating ragdoll on an uninitialized skeleton',
 'checks':'Momentum/warmup/cleanup logic checks; PBO prefix/offset/source/hash checks and ZIP integrity',
 'limitations':'Exact limb pose at death is not cloned. Native impulse propagation, sampling and warmup thresholds require local gameplay verification.'
}
if __name__=='__main__':packer.main()
