#!/usr/bin/env python3
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabLocomotion_v107'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Corpse_Momentum_v107.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'v107 command-handler submission and native-tick acknowledgement correction',
 'official_script_revision':'e3dda95b2b9730bdc0dba931abb35304b484bbfc',
 'native_compile_and_playtest':'v106 compiled and captured 91 bones in user test; v107 native changes NOT RUN in cloud',
 'v106_runtime':'3 captures/bindings/applies succeeded but all readbacks failed: position error0.813-1.484m and basis error1.879-2.000; all hit1500ms fallback; no ragdoll activated',
 'root_cause_found':'v106 called AnimSetFloat outside CommandHandler, contrary to documented DayZPlayer API context',
 'changes':'Queue all graph writes, submit from custom corpse CommandHandler every tick, await revision acknowledgement plus another command tick; reduce handoff timeout to350ms; core-joint readback diagnostics',
 'checks':'3 command-context regression tests including compiled C++ adaptation of actual queue/ack methods; existing6 pose-math and5 graph integration checks; package source/offset/prefix/hash and ZIP checks',
 'limitations':'No native engine/compiler. Fixes a confirmed API-context violation, not proof native graph semantics match. Guarded fallback may still occur; no claim of seamless pose or per-limb velocity transfer.'
}
if __name__=='__main__':packer.main()
