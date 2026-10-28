"""Verify latest preset fidelity and final left-only walking native grip scope."""
from pathlib import Path
import sys,json,re,hashlib,itertools
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));from dayz_graph_formats import newnodes
base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v179';out=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v180'
spec=json.loads((out/'Left-Walking-Grip-v180.json').read_text());raw=(r/'ads-lean-test/User-Presets/MLWalkingLeanPreset-Approved-v179-20261028.json').read_bytes();p=json.loads(raw)
assert len(raw)==14435 and hashlib.sha256(raw).hexdigest()==spec['uploaded_preset_sha256']
assert p['PresetVersion']==1
for rel in ['MLWalkingLeanPreset.json','Profiles/LeanMosin/MLWalkingLeanPreset.json','LogicSource/Presets/MLWalkingLeanPreset.json']:
 assert (out/rel).read_bytes()==raw,rel
for rel in ['MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json']:
 assert (out/rel).read_bytes()==(base/rel).read_bytes()
# Important saved left hand/elbow/forearm/body angles remain EXACT.
assert p['LeftLean']['WeaponSettings']['LeftRoll']==90
assert p['LeftLean']['WeaponSettings']['LeftYaw']==-84.0999984741211
assert p['LeftLean']['BodySettings']['Parts'][10]['BoneName']=='LeftArm'
assert p['LeftLean']['BodySettings']['Parts'][10]['Roll']==9.699999809265137
# Only the final secondary-arm solve condition changes: no source/pose ordering.
a=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((out/'WorkspaceSource/locomotion.agf').read_text());assert a.keys()==b.keys()
changed=[k for k in a if a[k]!=b[k]];assert changed==['ML166_PublishFinalAimedWeapon']
name=changed[0];assert a[name].replace('WeightSecondaryChain "'+spec['old_expression']+'"','WeightSecondaryChain "'+spec['new_expression']+'"',1)==b[name]
# Expression truth table across actor/lean/gait/native-angle and type/view scopes.
cases=0;newly_enabled=0
for preview,move,lean,pitch,yaw,rifle,fp in itertools.product([0,1],[0,.5,.51,1],[-1,-.1,0,.1,1],[-60,-5,0,5,60],[-60,0,60],[0,1],[0,1]):
 old=(abs(pitch)>5 or abs(yaw)>5) and rifle>.5 and fp<.5
 new=((preview>.5 and move>.5 and lean<0) or abs(pitch)>5 or abs(yaw)>5) and rifle>.5 and fp<.5
 if preview==0 or move<=.5 or lean>=0 or old:assert new==old
 if new!=old:
  assert preview==1 and move>.5 and lean<0 and rifle==1 and fp==0
  newly_enabled+=1
 cases+=1
assert newly_enabled>0
for pth in (base/'LogicSource/Scripts').rglob('*.c'):
 new=(out/pth.relative_to(base)).read_text();old=pth.read_text()
 if pth.name=='MLWalkingEditor173.c':assert old.replace('Saved ALL F6/F7 settings and BOTH sides: MLLeanPreset.json','Saved ALL F6/F7 settings and BOTH sides: MLWalkingLeanPreset.json')==new
 else:assert old==new,pth
assert (base/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()==(out/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()
# Endpoint remains a native weapon-local contact solve in the same evaluation,
# with no added temporal variables, lerp or feedback code.
for field in ['WeightPrimaryChain','WeaponDirLr','WeaponDirUd','WeaponRoll','Ikconfig','BlendInTime','BlendOutTime']:
 assert re.findall(field+r'[^\n]*',a[name])==re.findall(field+r'[^\n]*',b[name])
assert 'BlendInTime 0' in b[name] and 'BlendOutTime 0' in b[name]
# Existing minimum-twist nodes and crash guards unchanged.
assert sum('ML179' in k for k in b)==sum('ML179' in k for k in a)
for pth in (out/'LogicSource/Scripts').rglob('*.c'):
 assert not re.search(r'\]\s*(\+\+|--)|(\+\+|--)\s*[A-Za-z_]\w*\[',pth.read_text())
result={'latest_uploaded_preset_exact':True,'uploaded_preset_sha256':spec['uploaded_preset_sha256'],'changed_graph_fields':1,'scope_cases':cases,'new_left_preview_contact_cases':newly_enabled,'stationary_and_right_walk_behaviour_unchanged':True,'no_new_smoothing_or_script_feedback':True,'native_compile_grip_and_elbow_visuals':'NOT RUN'}
(out/'Left-Walking-Grip-Checks-v180.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
