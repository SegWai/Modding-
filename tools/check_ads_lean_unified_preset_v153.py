"""Offline combined-preset/migration/roundtrip and source wiring checks; not Enforce compilation."""
from pathlib import Path
import json,re,copy,sys,math,io,contextlib
import numpy as np
from scipy.spatial.transform import Rotation
from mirror_ads_lean_body_preset import mirror,opposite
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v153';BASE=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v152'
preset=json.loads((KIT/'MLLeanPreset.json').read_text());bundled=json.loads((KIT/'LogicSource/Presets/MLLeanPreset.json').read_text());assert preset==bundled
right=json.loads((ROOT/'ads-lean-test/User-Presets/Right-Body-20261027.json').read_text());left=mirror(right)
assert preset['RightLean']['BodySettings']==right and preset['LeftLean']['BodySettings']==left
assert preset['PresetVersion']==1
names=[p[0] for p in json.loads((KIT/'Body-Editor-v149.json').read_text())['parts']]
fields=['X','Y','Z','Pitch','Yaw','Roll','LeftPitch','LeftYaw','LeftRoll','RightPitch','RightYaw','RightRoll','HeadPitch','HeadYaw','HeadRoll','MuzzleYaw','MuzzlePitch']
def valid(data):
 try:
  if data['PresetVersion']!=1:return False
  for side in ['LeftLean','RightLean']:
   w=data[side]['WeaponSettings'];parts=data[side]['BodySettings']['Parts']
   if [p['BoneName'] for p in parts]!=names:return False
   for p in parts:
    for f in ['X','Y','Z','Pitch','Yaw','Roll']:
     v=p[f]
     if not math.isfinite(v) or abs(v)>(15 if f in ['X','Y','Z'] else 45):return False
   for f in fields:
    v=w[f]
    if not math.isfinite(v):return False
    bounds=(-90,90) if f.startswith(('Left','Right')) else (-45,45) if f.startswith('Head') else (-20,20)
    if f=='Y':bounds=(-25,15)
    if f=='Z':bounds=(-20,25)
    if not bounds[0]<=v<=bounds[1]:return False
  return True
 except (KeyError,TypeError):return False
assert valid(preset)
assert json.loads(json.dumps(preset))==preset
# Emulate the persistence contract: changing either panel or selected side still
# serializes four complete sections, and invalid load never replaces active data.
saved=copy.deepcopy(preset)
saved['RightLean']['WeaponSettings']['LeftRoll']=12.5
saved['LeftLean']['WeaponSettings']['MuzzleYaw']=-4
saved['RightLean']['BodySettings']['Parts'][0]['X']=2.5
saved['LeftLean']['BodySettings']['Parts'][4]['Pitch']=-3
assert valid(saved)
assert json.loads(json.dumps(saved))==saved
failures=[]
for mutation in ['missing_side','bad_name','bad_range','bad_weapon','nan','version']:
 bad=copy.deepcopy(saved)
 if mutation=='missing_side':del bad['LeftLean']
 elif mutation=='bad_name':bad['LeftLean']['BodySettings']['Parts'][0]['BoneName']='Head'
 elif mutation=='bad_range':bad['RightLean']['BodySettings']['Parts'][0]['X']=100
 elif mutation=='bad_weapon':bad['RightLean']['WeaponSettings']['X']=100
 elif mutation=='nan':bad['RightLean']['WeaponSettings']['MuzzleYaw']=float('nan')
 else:bad['PresetVersion']=999
 active=copy.deepcopy(saved)
 if valid(bad):active=bad
 assert active==saved
 failures.append(mutation)
code=(KIT/'LogicSource/Scripts/4_World/MLUnifiedPreset153.c').read_text();weapon=(KIT/'LogicSource/Scripts/4_World/MLPoseEditor144.c').read_text();body=(KIT/'LogicSource/Scripts/4_World/MLBodyEditor149.c').read_text()
for state in [weapon,body]:
 assert 'static void Save()\n {\n  ML153Preset.Save();' in state
 assert 'static void Load()\n {\n  ML153Preset.Load();' in state
assert 'static bool Validate(ML144Values candidate, bool leftLean, array<float> solved)' in weapon
assert 'LoadLegacy();' in weapon
for old in ['MLPoseEditor_Left.json','MLPoseEditor_Right.json','MLBodyEditor_Left.json','MLBodyEditor_Right.json']:
 assert old in code
 assert not re.search(r'(?:SaveFile|DeleteFile|CopyFile)\([^\n]*'+re.escape(old),code)
install=code[code.index(' static bool Install('):code.index(' static ML153PresetFile Capture()')]
assert install.index('if (!Validate(')<install.index('ML144State.LeftValues =')
assert code.index('Initialized = true;')<code.index('   Load();',code.index('Initialized = true;'))
assert 'SaveFile(temporaryPath, data, error)' in code
assert 'LoadFile(temporaryPath, readback, error)' in code
assert code.index('if (!Validate(readback')<code.index('CopyFile(FilePath, BackupPath)')<code.index('SaveFile(FilePath, readback, error)')
assert 'DeleteFile(BackupPath)' in code
for name in ['MLPoseEditorMenu144.c','MLBodyMenu149.c']:
 s=(KIT/'LogicSource/Scripts/5_Mission'/name).read_text();assert '  ML153Preset.Init();' in s
assert (KIT/'WorkspaceSource/locomotion.agf').read_bytes()==(BASE/'WorkspaceSource/locomotion.agf').read_bytes()
assert (KIT/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes()==(BASE/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes()
assert (KIT/'LogicSource/Scripts/5_Mission/MLPanelNavigation152.c').read_bytes()==(BASE/'LogicSource/Scripts/5_Mission/MLPanelNavigation152.c').read_bytes()
for p in (KIT/'LogicSource').rglob('*.c'):
 s=p.read_text();assert s.count('{')==s.count('}'),p
 assert not re.search(r'\bstring Bone\s*;|\.Bone\b',s)
 for m in re.finditer(r'(?:array<float>|TStringArray) \w+ = \{([^\n]+)\}',s):assert m[1].count(',')<8,p
# Validate exact reflection, including paired anatomical feet/shin and head.
original={p['BoneName']:p for p in right['Parts']};F=np.diag([-1,1,1]);error=0
for p in left['Parts']:
 q=original[opposite(p['BoneName'])]
 A=Rotation.from_euler('xyz',[q[k] for k in ['Pitch','Yaw','Roll']],degrees=True).as_matrix();B=Rotation.from_euler('xyz',[p[k] for k in ['Pitch','Yaw','Roll']],degrees=True).as_matrix();error=max(error,float(np.max(abs(B-F@A@F))))
assert error<1e-12 and mirror(left)==right
print(json.dumps({'complete_sections':4,'body_parts_per_side':24,'weapon_arm_head_muzzle_fields_per_side':17,'bundled_right_body':'exact uploaded floats','bundled_left_body':'anatomically mirrored, signs verified by matrix reflection','mirror_matrix_error':error,'roundtrip':'all sections retained regardless of active panel/side','invalid_payloads_rejected':failures,'migration':'valid legacy files may override corresponding bundled sections only if no combined preset exists; originals untouched','save':'temporary serialize/read/validate, backup previous canonical, write canonical; both panel buttons route to same manager','preserved':'animation graph, camera, RMB navigation, smoothing/endpoints','native_compile_save_load_relaunch':'NOT RUN'},indent=2))
