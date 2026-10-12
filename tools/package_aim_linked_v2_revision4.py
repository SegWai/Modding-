#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision4'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Aim_Linked_v2_Revision4.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'v2rev4 slowaim73/default andoriginal native source atlevel2; fast80/native100/120; F8 native/custom standing aim speed comparison; crouchaim unchanged','checks':'controller tiers/native comparison/persistence/Ctrl/crouch tests; unchanged graph and clip plans; PBO/ZIP','limitations':'Native velocities and aiming/fire still need local test; no on-screen messages; earlier revisions preserved'}
if __name__=='__main__':packer.main()
