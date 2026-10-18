#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v104'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Corpse_Momentum_v104.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v104 freeze source death pose, keep replacement hidden, wait for settled native prone stance',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'v100 confirmed working by user; v104 native changes NOT RUN in cloud',
 'v101_runtime':'Both ragdolls activated with valid skeleton; speeds0 and0.215m/s. Second impulse included23Ns vertical gravity cancellation. User later confirmed standing or slow motion.',
 'v102_runtime':'User confirms running momentum; pelvis travels1.6-1.7m in0.3s. Default upright replacement loses raised-arm and crawling pose.',
 'v103_crawl_runtime':'Crawling detected; ragdoll activated at pelvis0.537m/head0.591m, with user-observed standing flash and no visible ragdoll.',
 'purpose':'Block intermediate crawl poses, freeze original during handoff, and guard replacement visibility',
 'checks':'Logged intermediate-pose rejection, stable-low-prone readiness, frozen-source failure restoration, prior momentum/lifecycle checks; PBO prefix/offset/source/hash checks and ZIP integrity',
 'limitations':'Exact limb pose at death is not cloned. Native stance/input priming, visual arm continuity and crawling handoff require local gameplay verification.'
}
if __name__=='__main__':packer.main()
