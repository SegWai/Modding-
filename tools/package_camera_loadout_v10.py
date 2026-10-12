#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCamera_Loadout_v10'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Camera_Loadout_v10.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Third-person fast-crouch movement height for slow crouch; military loadout,90-slot two-weapon backpack and four loaded weapons with spare mags/ammo','checks':'movement/graph/preparation byte preservation and mission brake/input method preservation; inspected native camera and inventory API; PBO/ZIP verification','limitations':'Native DayZ compilation, backpack attachment acceptance, item availability and camera collision/visuals require user test; no MMG dependency; prior versions preserved'}
if __name__=='__main__':packer.main()
