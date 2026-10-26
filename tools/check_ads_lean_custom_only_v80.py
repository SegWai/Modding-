"""Verify supported raised paths bypass legacy lean, preserving v79 endpoints."""
from pathlib import Path
import re,json,hashlib
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v79';b=base/'MovementLab_ADS_Lean_Mosin_v80'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(79|80)\]',r'[\g<1>VERSION]',s.replace('v79','vVERSION').replace('v80','vVERSION'))
for p in (a/'LogicSource').rglob('*'):
 if p.is_file() and p.name!='MLADSLeanKeys.c':assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());s=(b/'WorkspaceSource/locomotion.agf').read_text();new=newnodes(s);manifest=json.loads((b/'Custom-Only-v80.json').read_text())
changes={x['native_chain']:x['node'] for x in manifest['bypasses']}
assert set(new)-set(old)==set(changes.values())
for name,block in old.items():
 expected=block
 for src,dst in changes.items():expected=expected.replace('"'+src+'"','"'+dst+'"')
 # Native right nodes themselves are untouched (only their consumers reroute).
 assert expected==new[name],name
for entry in manifest['bypasses']:
 n=new[entry['node']];native=new[entry['native_chain']]
 assert 'BlendWeight "MLADSLeanSmoothLow"' in n
 assert 'Child0 "'+entry['native_chain']+'"' in n
 assert 'Child1 "'+entry['unleaned_base']+'"' in n
 assert 'OptimizeMin 1' in n and 'OptimizeMax 1' in n
 # At gate=1, legacy left/right transforms have expression factor zero:
 # bypassing them preserves settled custom pose mathematically.
 for suffix in ('Left','Right'):
  block=new[entry['native_chain'][:-5]+suffix]
  assert '*(1.0-MLADSLeanGate)' in re.search(r'Expression "([^"]+)"',block)[1]
 # Legacy right chain can be reached only through the inactive native input
 # of its dedicated selector; never directly from another consumer.
 consumers=[name for name,block in new.items() if re.search(r'\bChild\d* "'+entry['native_chain']+'"',block)]
 assert consumers==[entry['node']],consumers
keys=(b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
assert not re.search(r'MLADSLeanSettings\.(Enabled|Inspection)\s*=',keys)
assert 'MLADSLeanLocomotion_v80.agf' in (b/'WorkspaceSource/player_main.agr').read_text()
backup=ROOT/manifest['backup']['file'];assert hashlib.sha256(backup.read_bytes()).hexdigest()==manifest['backup']['sha256']
print('PASS: all four supported raised contexts bypass legacy lean at optimized endpoint; custom transforms, v79 camera/timing and backup intact; native/off switches removed. Native gameplay not run.')
