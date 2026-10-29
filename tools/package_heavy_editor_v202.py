from pathlib import Path
import package_ads_lean_runtime as p
r=Path(__file__).resolve().parents[1];original=p.runtime_files
p.runtime_files=lambda kit:original(kit)+tuple(s for name in ['MLHeldLeanPreset.json','MLBatLeanPreset.json','MLPistolLeanPreset.json','MLOneHandedLeanPreset.json','MLHeavyLeanPreset.json']for s in [name,'Profiles/LeanMosin/'+name])
if __name__=='__main__':p.package(r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v202',r/'artifacts/MovementLab_ADS_Lean_Mosin_v202.zip')
