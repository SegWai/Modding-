#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCrouch_Fast90_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Fast90_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'Six crouch levels restored; level6 fast crouch27FPS targets90% of nativefast velocity and animation pace; original native files untouched; standing logic unchanged','checks':'translated inherited controller regressions; only three custom fast clip mappings changed,27/30=.9 FPS-only retime; native schemas/graph/controller preserved; PBO/ZIP','limitations':'native DayZ compilation/playback/actual velocity and Windows preparation require local test; percentage is of fast crouch, not slow crouch'}
if __name__=='__main__':packer.main()
