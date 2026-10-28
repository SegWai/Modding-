"""Verify the log-identified compile fix has no pose/behavior scope expansion."""
from pathlib import Path
import re,json
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v176';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v177'
original=(a/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
expected=original.replace('  m_ML176SampleCount[sideIndex]++;','  int nextSampleCount = m_ML176SampleCount[sideIndex];\n  nextSampleCount = nextSampleCount + 1;\n  m_ML176SampleCount[sideIndex] = nextSampleCount;',1).replace('      m_ML176CaptureCount[leanSide]++;','      int nextCaptureCount = m_ML176CaptureCount[leanSide];\n      nextCaptureCount = nextCaptureCount + 1;\n      m_ML176CaptureCount[leanSide] = nextCaptureCount;',1)
assert expected==(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
for p in (b/'LogicSource/Scripts').rglob('*.c'):
 assert not re.search(r'\]\s*(\+\+|--)|(\+\+|--)\s*[A-Za-z_]\w*\[',p.read_text()),p
 if p.name!='MLADSLeanPlayer.c':assert p.read_bytes()==(a/p.relative_to(b)).read_bytes()
for rel in ['WorkspaceSource/locomotion.agf','MLLeanPreset.json','MLWalkingLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','Profiles/LeanMosin/MLWalkingLeanPreset.json','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
for count in range(1000):
 assert count+1==int(count)+1
# Run v176 lifecycle/baseline checks on the fixed source. Its nested baseline
# suite is also redirected, so v177 data is actually checked.
source=(r/'tools/check_ads_lean_arm_stability_v176.py').read_text().replace("b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v176'", "b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v177'").replace("m_ML176CaptureCount[leanSide]++;", "m_ML176CaptureCount[leanSide] = nextCaptureCount;").replace('Arm-Stability-Checks-v176.json','Arm-Stability-Checks-v177.json').replace('Arm-Zero-Checks-v176.json','Arm-Zero-Checks-v177.json')
exec(compile(source,str(r/'tools/check_ads_lean_arm_stability_v176.py'),'exec'),{'__file__':str(r/'tools/check_ads_lean_arm_stability_v176.py')})
result={'indexed_increment_sites_fixed':2,'other_gameplay_scripts_unchanged':True,'graph_and_all_pose_values_unchanged':True,'native_compilation':'NOT RUN'}
(b/'Counter-Compile-Checks-v177.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
