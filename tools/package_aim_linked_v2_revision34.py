#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision34'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision34.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev34 crouch30/47/60/87default4/nativefast100level5; aimcrouch30/47/60/87default4; selectable73removed; stationarydefault4; hiddenfadesend4; nativeShiftADS/camerafallback blocked,AltADSretained','checks':'actual-controller default/wheel/aim/fade30/60/144FPS both orders; ADS nativebody/toggle and camera wrapper checks; sortedtemplate/graph/source checks; PBO/ZIP','limitations':'Native compile/feel/Shiftcamera validation needs user test; transitionalposeclips retained for smooth blending; earlierbuilds preserved'}
if __name__=='__main__':packer.main()
