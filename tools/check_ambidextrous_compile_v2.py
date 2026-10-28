"""Regression for the native compiler's Weapon type-name collision."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[1];a=root/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v1';b=a.with_name('MovementLab_Ambidextrous_Lean_v2');rel=Path('LogicSource/Scripts/4_World/MLAShoulderPose.c');old=(a/rel).read_text();new=(b/rel).read_text()
assert len(re.findall(r'\bWeapon\b',old))==3
assert new==re.sub(r'\bWeapon\b','HeldWeapon',old)
assert not re.search(r'\bWeapon\b',new)
for directory in ['LogicSource/Scripts','LogicSource/Presets']:
 for p in (a/directory).rglob('*'):
  if p.is_file() and p.relative_to(a)!=rel:assert p.read_bytes()==(b/p.relative_to(a)).read_bytes()
for path in ['WorkspaceSource/locomotion.agf','LogicSource/Inputs.xml']:assert(a/path).read_bytes()==(b/path).read_bytes()
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for p in [n,'Profiles/LeanMosin/'+n]:assert(a/p).read_bytes()==(b/p).read_bytes()
print('PASS: only3 Weapon field tokens renamed; all gameplay/pose/input/graph data unchanged. Native compilation NOT RUN.')
