"""Check baseline+delta preserves uploaded effective inputs and save semantics."""
from pathlib import Path
import copy,hashlib,json,re,random
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v173';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v174';w=b/'LogicSource/Scripts/4_World'
u=json.loads((r/'ads-lean-test/User-Presets/MLWalkingLeanPreset-Uploaded-v173-20261028.json').read_text());p=json.loads((b/'MLWalkingLeanPreset.json').read_text())
targets={'LeftShoulder','LeftArm','LeftForeArm','LeftHand'};wf=('LeftPitch','LeftYaw','LeftRoll');pf=('X','Y','Z','Pitch','Yaw','Roll')
def effective(data):
 out=copy.deepcopy(data)
 for side,key in [('LeftLean','LeftArmZero'),('RightLean','RightArmZero')]:
  for f in wf:out[side]['WeaponSettings'][f]+=data[key]['WeaponSettings'][f]
  for i,part in enumerate(out[side]['BodySettings']['Parts']):
   if part['BoneName'] in targets:
    for f in pf:part[f]+=data[key]['BodySettings']['Parts'][i][f]
 return {k:out[k] for k in ('LeftLean','RightLean')}
assert p['PresetVersion']==2
assert effective(p)=={k:u[k] for k in ('LeftLean','RightLean')}
for side,key in [('LeftLean','LeftArmZero'),('RightLean','RightArmZero')]:
 assert p[key]==u[side]
 for f in wf:assert p[side]['WeaponSettings'][f]==0
 for part in p[side]['BodySettings']['Parts']:
  if part['BoneName'] in targets:assert all(part[f]==0 for f in pf)
# Apply random offsets, simulate save/reload and confirm add/subtract inversion.
rng=random.Random(174)
for _ in range(200):
 q=copy.deepcopy(p)
 for side in ('LeftLean','RightLean'):
  for f in wf:q[side]['WeaponSettings'][f]=rng.uniform(-90,90)
  for part in q[side]['BodySettings']['Parts']:
   if part['BoneName'] in targets:
    for f in pf:part[f]=rng.uniform(-15,15) if f in ('X','Y','Z') else rng.uniform(-45,45)
 loaded=json.loads(json.dumps(q));assert effective(q)==effective(loaded)
 out=effective(q)
 for side,key in [('LeftLean','LeftArmZero'),('RightLean','RightArmZero')]:
  for f in wf:assert abs(out[side]['WeaponSettings'][f]-p[key]['WeaponSettings'][f]-q[side]['WeaponSettings'][f])<1e-12
# Both relative files and bundle identical. Approved stationary bytes untouched.
for rel in ['LogicSource/Presets/MLWalkingLeanPreset.json','Profiles/LeanMosin/MLWalkingLeanPreset.json']:
 assert (b/rel).read_bytes()==(b/'MLWalkingLeanPreset.json').read_bytes()
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json']:
 assert (b/rel).read_bytes()==(a/rel).read_bytes()
assert (b/'WorkspaceSource/locomotion.agf').read_bytes()==(a/'WorkspaceSource/locomotion.agf').read_bytes()
# Explicit helper fields implement only requested anatomical left arm rebasing.
helper=(w/'MLArmZero174.c').read_text()
for f in u['LeftLean']['WeaponSettings']:
 assert f'result.{f} = input.{f};' in helper
 assert (f'result.{f} = result.{f} + basis.WeaponSettings.{f} * direction;' in helper)==(f in wf)
for f in pf:assert f'part.{f} = part.{f} + armBase.{f} * direction;' in helper
scope=(w/'MLWalkingEditorScope173.c').read_text();leave=scope.split(' void Leave()')[1]
for f in ['Values','LeftValues','RightValues']:assert f'ML173WeaponState.{f} = ML144State.{f}' not in leave
for f in ['Left','Right']:assert f'ML173BodyState.{f} = ML149State.{f}' not in leave
for f in ['Bound','ArmsReady','Status']:assert f'ML173WeaponState.{f} = ML144State.{f};' in leave
assert 'if (WeaponRevision != ML173WeaponState.ValuesRevision)' in scope
assert 'if (BodyRevision != ML173BodyState.GeometryRevision)' in scope
assert 'ML144State.Values = EffectiveLeftWeapon;' in scope and 'ML149State.Right = EffectiveRightBody;' in scope
preset=(w/'MLWalkingEditor173.c').read_text();assert 'if (!ML174ArmZero.Prepare(data))' in preset
assert 'ML174ArmZero.LeftBase = data.LeftArmZero;' in preset
assert 'data.LeftArmZero = ML174ArmZero.LeftBase;' in preset
assert 'data.PresetVersion != 2' in preset and 'MLADSLeanLogic/Presets/MLWalkingLeanPreset.json' in preset
assert 'if (data.PresetVersion != 1' in helper and 'data.PresetVersion = 2;' in helper
# Original source and every other preset remain available as backups.
assert hashlib.sha256((b/'LogicSource/Presets/MLWalkingArmBaseline.json').read_bytes()).hexdigest()=='fc02c504287f1895891b01e40f7dffebb230eb3da605c88b887c7534c79921d0'
# All unchanged native scripts/camera/menu input paths retain v173 bytes.
for tree in ['LogicSource/Scripts/5_Mission','LogicSource/GUI']:
 for f in (a/tree).rglob('*'):
  if f.is_file():assert f.read_bytes()==(b/f.relative_to(a)).read_bytes()
for f in (a/'LogicSource/Scripts/4_World').glob('*.c'):
 if f.name not in ['MLWalkingEditor173.c','MLWalkingEditorScope173.c','MLADSLeanPlayer.c']:
  assert f.read_bytes()==(w/f.name).read_bytes()
for f in (b/'LogicSource/Scripts').rglob('*.c'):
 text=re.sub(r'//[^\n]*|"(?:\\.|[^"\\])*"','',f.read_text());assert text.count('{')==text.count('}')
# Native pose unchanged follows from identical graph plus EXACT effective inputs,
# but actual compilation/engine rendering still requires the Windows game.
result={'uploaded_effective_settings_exactly_preserved':True,'left_arm_controls_zero_both_sides':True,'roundtrip_offset_cases':200,'graph_and_stationary_preset_unchanged':True,'native_compile_and_render':'NOT RUN'}
(b/'Arm-Zero-Checks-v174.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
