"""Standalone alternate mod: only runtime essentials, unique PBO prefixes."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import package_ads_lean_runtime as runtime
runtime.FILES=tuple(n.replace('MLADSLeanLogic','MLAmbidextrousLogic').replace('MLADSLeanWorkspace','MLAmbidextrousWorkspace')for n in runtime.FILES)
if __name__=='__main__':
 r=Path(__file__).resolve().parents[1];runtime.package(r/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v1',r/'artifacts/MovementLab_Ambidextrous_Lean_v1.zip')
