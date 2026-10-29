"""Regression: remove one saved head roll without disturbing authored pose."""
from pathlib import Path
import json,copy
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v217';b=a.with_name('MovementLab_ADS_Lean_Mosin_v218')
raw=(r/'ads-lean-test/User-Presets/Uploaded-20261029-MLJoggingLeanPreset.json').read_bytes()
assert(b/'MLJoggingLeanPreset-OriginalUpload.json').read_bytes()==raw
expected=json.loads(raw);head=next(p for p in expected['RightLean']['BodySettings']['Parts']if p['BoneName']=='Head');assert head['Roll']==20.0;head['Roll']=0.0
for rel in ['MLJoggingLeanPreset.json','LogicSource/Presets/MLJoggingLeanPreset.json','Profiles/LeanMosin/MLJoggingLeanPreset.json']:
 assert json.loads((b/rel).read_bytes())==expected,rel
assert (b/'WorkspaceSource/locomotion.agf').read_bytes()==(a/'WorkspaceSource/locomotion.agf').read_bytes()
for p in(a/'LogicSource/Presets').glob('*.json'):
 if p.name=='MLJoggingLeanPreset.json':continue
 for rel in [p.name,'LogicSource/Presets/'+p.name,'Profiles/LeanMosin/'+p.name]:assert(a/rel).read_bytes()==(b/rel).read_bytes(),rel
for p in(a/'LogicSource/Scripts').rglob('*.c'):
 rel=p.relative_to(a);assert p.read_text().replace('v217','v218')==(b/rel).read_text(),rel
assert(a/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()==(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()
print('PASS:one semantic change from uploaded JSON: right body Head Roll20->0;left/pitch/yaw/arms/weapon intact;original raw archived;14 other banks/graph/scene/code unchanged except build label. Native visual result NOT RUN.')
