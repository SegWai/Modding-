"""Regression for native v188 graph diagnostics: float expressions cannot be int constants."""
from pathlib import Path
import re,sys
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v188';b=a.with_name('MovementLab_ADS_Lean_Mosin_v189')
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());assert old.keys()==new.keys()
changed=[]
for n,value in old.items():
 if n.startswith('{'):continue
 expected=value
 if n=='ML187_PublishHeldLean':
  for field in ['WeaponDirLr','WeaponDirUd','WeaponRoll']:expected=expected.replace(field+' "0"',field+' "0.0"')
 if value!=new[n]:changed.append(n)
 assert new[n]==expected,n
assert changed==['ML187_PublishHeldLean']
# The precise type error reported natively must never pass the offline check again.
for n,node in new.items():
 if n.startswith('{'):continue
 for field,value in re.findall(r'\b(WeaponDirLr|WeaponDirUd|WeaponRoll) "([^"]+)"',node):
  assert not re.fullmatch(r'[+-]?\d+',value.strip()),(n,field,value)
for folder in ['LogicSource/Scripts','LogicSource/Presets','Missions']:
 for p in (a/folder).rglob('*'):
  if p.is_file():assert p.read_bytes()==(b/p.relative_to(a)).read_bytes(),p
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
print('PASS: exact 3 float-literal fixes in one node; no bare integer weapon float expressions;all scripts/mission/approved presets unchanged. Native graph reload NOT RUN.')
