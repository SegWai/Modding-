"""Prevent novel expression functions; verify exact single-field startup candidate fix."""
from pathlib import Path
import sys,re,json
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v2';b=a.with_name('MovementLab_Ambidextrous_Lean_v3');base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v186';spec=json.loads((b/'Graph-Load-Fix-v3.json').read_text());old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());assert old.keys()==new.keys()
for n,v in old.items():
 if n=='ML166_FinalAimOnly':assert new[n]==v.replace(spec['old_expression'],spec['new_expression'])
 else:assert new[n]==v,n
cases=0
for active in [0,1]:
 for i in range(1001):
  gate=i/1000;assert max(active,gate)==max(0,min(1,active+gate));cases+=1
for folder in ['LogicSource/Scripts','LogicSource/Presets']:
 for p in(a/folder).rglob('*'):
  if p.is_file():assert p.read_bytes()==(b/p.relative_to(a)).read_bytes()
assert(a/'LogicSource/Inputs.xml').read_bytes()==(b/'LogicSource/Inputs.xml').read_bytes()
# New expression function names must be present in the original working graph.
def funcs(p):
 s=p.read_text();lines=re.findall(r'(?:Expression|BlendWeight|Condition|Value[XY]|Weight\w+|WeaponDir\w+|WeaponRoll) "([^\n"]+)"',s)
 return {f for line in lines for f in re.findall(r'\b([A-Za-z_]\w*)\s*\(',line)}
extra=funcs(b/'WorkspaceSource/locomotion.agf')-funcs(base/'WorkspaceSource/locomotion.agf');assert not extra,extra
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
print('PASS: 1 graph-field change; 2002 gate equivalence cases; no novel expression functions; all gameplay/data unchanged. Native cause/fix NOT confirmed.')
