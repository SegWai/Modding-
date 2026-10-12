#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Walk_v20'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Walk_v20.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Diagnostic only v19; aiming tier/eligibility/profile/bindings/actual gait and velocity logging; no visual or speed changes','checks':'v19 controller regression and graph/clip/mission byte preservation; PBO/ZIP','limitations':'Requested aimspeed still unconfirmed; native logs required to locate missing effect; no on-screen messages'}
if __name__=='__main__':packer.main()
