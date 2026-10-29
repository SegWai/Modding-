from pathlib import Path
import package_ads_lean_runtime as p
r=Path(__file__).resolve().parents[1];original=p.runtime_files
p.runtime_files=lambda kit:original(kit)+('MLHeldLeanPreset.json','Profiles/LeanMosin/MLHeldLeanPreset.json','MLBatLeanPreset.json','Profiles/LeanMosin/MLBatLeanPreset.json')
if __name__=='__main__':p.package(r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v195',r/'artifacts/MovementLab_ADS_Lean_Mosin_v195.zip')
