#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision41'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision41.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev41 existing lookzoom action toggles ironsight/attachedscope onlywhileADS; debounced hold; native optics API; movement and Revision40 swaybehavior retained','checks':'actualWorld getter/movement30/60/144FPSbothorders; actualzoomhandler iron/scope/holddebounce/memory/magnification/UI/weapon gates; othermodule byteequality; priorADS correction retained; native prototype names checked; sortedtemplate/graph/sourcechecks; PBO/ZIP','limitations':'Native compile/font/render/position stillneeds localtest; runtime widgets use nativeGUI APIs and no textures; priorbuilds preserved'}
if __name__=='__main__':packer.main()
