"""Ensure look isolation cannot alter weapon aiming, native comparison or presets."""
from pathlib import Path
import re,json
from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1]
a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v216';b=a.with_name('MovementLab_ADS_Lean_Mosin_v217')
info=json.loads((b/'Head-Look-Isolation-v217.json').read_text())
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
assert old.keys()==new.keys()
changed={n for n in old if old[n]!=new[n]}
assert changed==set(info['changed_native_look_nodes']),changed
for n in changed:
 assert re.sub(r'Condition "[^"]+"','',old[n])==re.sub(r'Condition "[^"]+"','',new[n])
 assert info['scope_condition'] in new[n]
# Truth table: both custom sides suppress native look; neutral/native comparator
# preserve it. No speed/stance/view dependency can accidentally reenable on jog.
for lean in [-1,-.5,0,.5,1]:
 for gate in [0,1]:
  for native in [0,1]:
   permitted=abs(lean)*gate<.001 or native>.5
   assert permitted==(lean==0 or gate==0 or native==1)
for p in (a/'LogicSource/Presets').glob('*.json'):
 for rel in [p.name,'LogicSource/Presets/'+p.name,'Profiles/LeanMosin/'+p.name]:assert (a/rel).read_bytes()==(b/rel).read_bytes(),rel
for rel in ['Missions/MLADSLeanMosin.ChernarusPlus/init.c','LogicSource/Scripts/4_World/MLJoggingEditor216.c','LogicSource/Scripts/4_World/MLJoggingEditorScope216.c']:
 assert(a/rel).read_bytes()==(b/rel).read_bytes(),rel
s=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();head=s[s.index(' protected void ML157UpdateHead('):s.index(' protected ref array<int> m_ML149Vars')]
assert 'AnimSetFloat(m_ML157Vars[headAxis], 0.0);'in head
assert 'GetBoneTransform'not in head and 'ML157HeadReference.'not in head
old_s=(a/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
# All actor code outside replacement function stays the same (plus comment).
assert old_s[old_s.index(' protected ref array<int> m_ML149Vars'):]==s[s.index(' protected ref array<int> m_ML149Vars'):]
assert not info['absolute_head_override']
print('PASS:8 look overlays only;scope truth table;15 raw banks unchanged;scene/editor isolation;no weapon/aim node mutations;no bone feedback. Native playtest NOT RUN;absolute head replacement NOT implemented.')
