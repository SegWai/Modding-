#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision46'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision46.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev46 experimental firstpersonhipview baseaimLR/UD alignment; no sway/recoil cancellation; ADS/freelook/thirdperson native; Revision45 retained','checks':'actualWorld getter/movement30/60/144FPSbothorders; actualhipcamera hook baseaimLR/UD/shake/state guards; previousmodules byte-identical; inheritedWorldmovement/stanceblends30/60/144FPSbothorders; graph/sortedtemplate/sourcechecks; native prototype names checked; sortedtemplate/graph/sourcechecks; PBO/ZIP','limitations':'Experimental camera direction follows gunbaseaim; native projectedweaponangle, mousefeel and shootingalignment stillneed gamevalidation; not a separate viewmodel or guaranteed fixed handpose; Revision45 preserved'}
if __name__=='__main__':packer.main()
