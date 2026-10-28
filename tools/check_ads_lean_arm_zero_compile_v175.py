"""Check the native compiler fix is strictly a helper-name/call-site change."""
from pathlib import Path
import re,json,subprocess,sys
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v174';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v175';changed=[]
for p in (a/'LogicSource').rglob('*'):
 if not p.is_file() or p.name=='config.cpp':continue
 q=b/p.relative_to(a)
 if p.read_bytes()==q.read_bytes():continue
 assert p.name in ['MLArmZero174.c','MLWalkingEditorScope173.c'],p
 original=p.read_text();expected=re.sub(r'\bWeapon\(', 'BuildArmWeaponValues(',original);expected=re.sub(r'\bBody\(', 'BuildArmBodyValues(',expected)
 if p.name=='MLArmZero174.c':
  expected=expected.replace('= BuildArmWeaponValues(', '= ML174ArmZero.BuildArmWeaponValues(').replace('= BuildArmBodyValues(', '= ML174ArmZero.BuildArmBodyValues(')
 assert expected==q.read_text(),q
 assert not re.search(r'\b(?:Weapon|Body)\(',q.read_text())
 changed.append(p.name)
assert len(changed)==2
for rel in ['WorkspaceSource/locomotion.agf','MLLeanPreset.json','MLWalkingLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','Profiles/LeanMosin/MLWalkingLeanPreset.json','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes(),rel
# Re-run original baseline/effective-value and save roundtrip checks against v175.
script=(r/'tools/check_ads_lean_arm_zero_v174.py').read_text().replace("b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v174'", "b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v175'").replace('Arm-Zero-Checks-v174.json','Arm-Zero-Checks-v175.json')
exec(compile(script,str(r/'tools/check_ads_lean_arm_zero_v174.py'),'exec'),{'__file__':str(r/'tools/check_ads_lean_arm_zero_v174.py')})
result={'compile_failure_from_logs':'MLArmZero174.c102/103 Method Object is private','fix':'Distinct helper names, explicitly qualified migration calls','changed_gameplay_scripts':changed,'pose_graph_and_preset_bytes_unchanged':True,'native_recompilation':'NOT RUN'}
(b/'Compile-Fix-Checks-v175.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
