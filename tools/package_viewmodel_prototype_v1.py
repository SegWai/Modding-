#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'viewmodel-prototype/MovementLabViewmodelPrototype_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Viewmodel_Prototype_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'separate PlayerPreviewWidget dummy renderer, fixed local overlay pose/orientation; F9 toggle and F10 framing; based on49 without camera overrides','checks':'native API/source validation; existing movement regressions; ownership and visibility recovery with preview mocks; template and graph default branch preservation','limitations':'Native rendering/framing/transparency/dummy pose not executed; reload/fire actions fall back native; not complete production viewmodel; only offline test; other versions preserved'}
if __name__=='__main__':packer.main()
