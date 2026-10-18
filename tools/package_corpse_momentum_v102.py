#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v102'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Corpse_Momentum_v102.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v102 v100 confirmed infected-model corpse with world-motion priority, 80ms sampling, gravity-preserving horizontal momentum and followthrough logs',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'v100 confirmed working by user; v102 native changes NOT RUN in cloud',
 'v101_runtime':'Both ragdolls activated with valid skeleton; speeds0 and0.215m/s. Second impulse included23Ns vertical gravity cancellation. Visible running state unknown from logs.',
 'purpose':'Carry movement into corpse physics and avoid activating ragdoll on an uninitialized skeleton',
 'checks':'Momentum/warmup/cleanup logic checks; PBO prefix/offset/source/hash checks and ZIP integrity',
 'limitations':'Exact limb pose at death is not cloned. Native impulse propagation, sampling and warmup thresholds require local gameplay verification.'
}
if __name__=='__main__':packer.main()
