"""Verify exact uploaded settings are active/default in the preservation test."""
from pathlib import Path
import json,hashlib,io,contextlib,runpy,sys,re
from zipfile import ZipFile
import numpy as np
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v155';BASE=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v154'
raw=(ROOT/'ads-lean-test/User-Presets/Current-MLLeanPreset.json').read_bytes();data=json.loads(raw)
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json']:assert (KIT/rel).read_bytes()==raw
assert data['PresetVersion']==1
parts=[p[0] for p in json.loads((KIT/'Body-Editor-v149.json').read_text())['parts']]
# Reuse the independently checked forward-kinematics verifier for weapon reach.
argv=sys.argv[:];sys.argv=['check']
with contextlib.redirect_stdout(io.StringIO()):math_checks=runpy.run_path(str(ROOT/'tools/check_ads_lean_both_sides_v147.py'))
sys.argv=argv
source=json.loads((KIT/'Both-Sides-Editor-v147.json').read_text());right=json.loads((KIT/'Live-Editor-v144.json').read_text());report={}
for side,seed in [('LeftLean',source['left_seed']),('RightLean',right['reference'])]:
 weapon=data[side]['WeaponSettings'];body=data[side]['BodySettings']['Parts'];assert [p['BoneName'] for p in body]==parts
 for p in body:
  for field in ['X','Y','Z','Pitch','Yaw','Roll']:
   value=p[field];assert np.isfinite(value) and abs(value)<=(15 if field in ['X','Y','Z'] else 45)
 for field,value in weapon.items():
  assert np.isfinite(value)
  low,high=(-90,90) if field.startswith(('Left','Right')) else (-45,45) if field.startswith('Head') else (-20,20)
  if field=='Y':low,high=-25,15
  if field=='Z':low,high=-20,25
  assert low<=value<=high,(side,field,value)
 coords={n:np.array(v) for n,v in seed.items()};values=[weapon[f] for f in ['X','Y','Z','Pitch','Yaw','Roll']]
 result=math_checks['coefficients'](coords,values);assert result is not None,side
 assert result[1]<1e-9
 report[side]={'weapon_fields':len(weapon),'body_parts':len(body),'weapon_target_reconstruction_error':result[1]}
with ZipFile(ROOT/'artifacts/MovementLab_ADS_Lean_Mosin_v155.zip') as z:
 assert z.testzip() is None
 assert z.read(KIT.name+'/MLLeanPreset.json')==raw
 assert z.read(KIT.name+'/Profiles/LeanMosin/MLLeanPreset.json')==raw
assert (KIT/'WorkspaceSource/locomotion.agf').read_bytes()==(BASE/'WorkspaceSource/locomotion.agf').read_bytes()
for p in (BASE/'LogicSource/Scripts').rglob('*.c'):
 if p.name=='MLUnifiedPreset153.c':continue
 assert p.read_bytes()==(KIT/p.relative_to(BASE)).read_bytes(),p
code=(KIT/'LogicSource/Scripts/4_World/MLUnifiedPreset153.c').read_text();init=code[code.index(' static void Init()'):code.index(' static void Save()')];assert 'ImportLegacy(bundled);' not in init
print(json.dumps({'preset_sha256':hashlib.sha256(raw).hexdigest(),'exact_copies_verified':['approved source','ZIProot','ZIPactiveprofile','PBOpresetinput'],'sides':report,'runtime':'samev154posegraph/UI/performance/smoothing, approved preset values applied without alteration','native_visual_confirmation':'NOT RUN'},indent=2))
