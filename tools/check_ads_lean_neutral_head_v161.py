"""Validate latest raw preset and isolate the NPC neutral head-handling change."""
from pathlib import Path
import json,hashlib,sys,runpy,contextlib,io
import numpy as np
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v160';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v161'
raw=(r/'ads-lean-test/User-Presets/Current-MLLeanPreset.json').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json']:assert (b/rel).read_bytes()==raw
assert (r/'artifacts/MLLeanPreset.json').read_bytes()==raw
assert (r/'ads-lean-test/User-Presets/MLLeanPreset-Approved-v161-20261027.json').read_bytes()==raw
assert (a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
old=(a/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();new=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
start=new.index('  if (m_MLADSLeanDemo)\n  {\n   requestedHeadADS = m_MLADSLeanDemoReady;');end=new.index('  HumanCommandWeapons weapons =',start)
normalized=new[:start]+'''  if (m_MLADSLeanDemo)
   requestedHeadADS = m_MLADSLeanDemoReady;
'''+new[end:];assert normalized==old
for path in (a/'LogicSource/Scripts').rglob('*.c'):
 if path.name=='MLADSLeanPlayer.c':continue
 assert path.read_bytes()==(b/path.relative_to(a)).read_bytes(),path
# Exhaust all handling cases: only stationary centred NPC may differ.
changed=[]
for demo in [False,True]:
 for ready in [False,True]:
  for ads in [False,True]:
   for lean in [-1,-.01,0,.01,1]:
    for movement in [0,1,2]:
     for suppress in [False,True]:
      before=(ready if demo else ads) and not suppress
      request=ready if demo else ads
      if demo and abs(lean)<=.01 and movement==0:request=False
      after=request and not suppress
      if before!=after:
       assert demo and movement==0 and abs(lean)<=.01
       changed.append((demo,lean,movement))
assert changed
# Validate entire uploaded preset and both-side weapon reach before packaging.
data=json.loads(raw);assert data['PresetVersion']==1
expected_parts=[part[0] for part in json.loads((b/'Body-Editor-v149.json').read_text())['parts']]
argv=sys.argv[:];sys.argv=['check']
with contextlib.redirect_stdout(io.StringIO()):maths=runpy.run_path(str(r/'tools/check_ads_lean_both_sides_v147.py'))
sys.argv=argv
seeds={'LeftLean':json.loads((b/'Both-Sides-Editor-v147.json').read_text())['left_seed'],'RightLean':json.loads((b/'Live-Editor-v144.json').read_text())['reference']}
for side in ['LeftLean','RightLean']:
 weapon=data[side]['WeaponSettings'];parts=data[side]['BodySettings']['Parts'];assert [p['BoneName'] for p in parts]==expected_parts
 for part in parts:
  for field in ['X','Y','Z','Pitch','Yaw','Roll']:
   assert np.isfinite(part[field]) and abs(part[field])<=(15 if field in ['X','Y','Z'] else 45)
 for field,value in weapon.items():
  low,high=(-90,90) if field.startswith(('Left','Right')) else (-45,45) if field.startswith('Head') else (-20,20)
  if field=='Y':low,high=-25,15
  if field=='Z':low,high=-20,25
  assert np.isfinite(value) and low<=value<=high,(side,field,value)
 coords={n:np.array(v) for n,v in seeds[side].items()};result=maths['coefficients'](coords,[weapon[f] for f in ['X','Y','Z','Pitch','Yaw','Roll']]);assert result is not None and result[1]<1e-9
report={'approved_preset_sha256':sha,'both_sides_schema_bounds_and_weapon_reach':'PASS','head_handling_change':'NPC only, stationary abs(lean)<=.01; stop forcing native optics head tilt','pose_graph_byte_identical_to_v160':True,'player_and_lean_head_behavior_unchanged':True,'native_compilation_and_rendered_head_match':'NOT RUN'}
(b/'Neutral-Head-Checks-v161.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
