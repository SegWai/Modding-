#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v103'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Corpse_Momentum_v103.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v103 native prone/raised-arm starting-pose seeding with v102 confirmed momentum retained',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'v100 confirmed working by user; v103 native changes NOT RUN in cloud',
 'v101_runtime':'Both ragdolls activated with valid skeleton; speeds0 and0.215m/s. Second impulse included23Ns vertical gravity cancellation. User later confirmed standing or slow motion.',
 'v102_runtime':'User confirms running momentum; pelvis travels1.6-1.7m in0.3s. Default upright replacement loses raised-arm and crawling pose.',
 'purpose':'Prime a native prone or raised-arm/moving pose before ragdoll, preserving confirmed v102 momentum',
 'checks':'Prone/no-standing-fallback, raised-arm readiness, momentum/warmup/cleanup logic checks; PBO prefix/offset/source/hash checks and ZIP integrity',
 'limitations':'Exact limb pose at death is not cloned. Native stance/input priming, visual arm continuity and crawling handoff require local gameplay verification.'
}
if __name__=='__main__':packer.main()
