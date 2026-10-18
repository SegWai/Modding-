#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v106'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Corpse_Momentum_v106.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v106 first native captured-transform graph bridge; approximate stance preparation removed',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'v100 confirmed working by user; v106 native changes NOT RUN in cloud',
 'v101_runtime':'Both ragdolls activated with valid skeleton; speeds0 and0.215m/s. Second impulse included23Ns vertical gravity cancellation. User later confirmed standing or slow motion.',
 'v102_runtime':'User confirms running momentum; pelvis travels1.6-1.7m in0.3s. Default upright replacement loses raised-arm and crawling pose.',
 'v103_crawl_runtime':'Crawling detected; ragdoll activated at pelvis0.537m/head0.591m, with user-observed standing flash and no visible ragdoll.',
 'v104_runtime':'Both crawling deaths timed out at repeatable head0.59/pelvis0.537; rollback resumed native death. Hard model-space height cutoff was not a valid ground-clearance test.',
 'v105_runtime':'User reports unchanged arm snap/clunky motion; native ragdoll flag alone does not establish pose continuity.',
 'purpose':'Capture/readback-verify actual infected joint transforms through an instance-gated procedural graph before physics',
 'checks':'6 pose-math tests plus 5 graph/source integration checks; graph references/spec/bindings; PBO prefix/offset/source/hash checks and ZIP integrity',
 'limitations':'First native graph experiment. Axis/pivot/parent semantics and native compilation unverified; 546-node branch/performance unverified; per-limb velocity not transferred; activation is gated on actual pose error.'
}
if __name__=='__main__':packer.main()
