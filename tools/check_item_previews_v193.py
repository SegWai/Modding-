"""Offline item preview scene, independent bank and native grip regression."""
from pathlib import Path
import json,re
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v192';b=a.with_name('MovementLab_ADS_Lean_Mosin_v193')
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
assert(a/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_bytes()==(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_bytes()
mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
for n in ['SVD','MP5K','Hoodie_Red','Hoodie_Green','m_ML192SMGNPC']:assert n not in mission,n
for n in ['Glock19','BaseballBat','SledgeHammer']:assert n in mission,n
for actor in ['m_ML193PistolNPC','m_ML193BatNPC','m_ML193SledgeNPC','m_ML182CustomNPC']:assert 'ObjectDelete('+actor+')'in mission
assert 'actor.GetHumanInventory().CreateInHands(weaponType)'in mission
assert 'actor.ML193StartOtherHeldComparison()'in mission
assert 'actor.ML183StartUnarmedComparison(false)'in mission
helper=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text()
# Bank data selection must be in Update, never in Bind (native compilation regression).
bind=helper[helper.index(' void Bind('):helper.index(' ML172Snapshot Capture(')]
assert 'leftValues ='not in bind and 'leftBody ='not in bind
update=helper[helper.index(' void Update('):];assert 'leftValues = ML193WeaponState.LeftValues'in update
assert 'heldPose && !HeldEditor && !OtherHeldEditor'in update
bank=(b/'LogicSource/Scripts/4_World/MLOtherHeldPreset193.c').read_text();assert '$profile:MLOtherHeldLeanPreset.json'in bank and 'MLUnarmedLeanPreset.json'not in bank
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):assert 'ML190WeaponState'not in p.read_text()
clock=(b/'LogicSource/Scripts/4_World/MLSharedPose181.c').read_text();assert 'ML193WeaponState.Open'in clock and 'elapsed / 1000'in clock
# Verify only arm seed is removed; keep custom torso/head/legs.
seed=json.loads((a/'MLUnarmedLeanPreset.json').read_text());new=json.loads((b/'MLOtherHeldLeanPreset.json').read_text())
for side in ['LeftLean','RightLean']:
 for k in ['LeftPitch','LeftYaw','LeftRoll','RightPitch','RightYaw','RightRoll']:seed[side]['WeaponSettings'][k]=0.0
 for part in seed[side]['BodySettings']['Parts']:
  if part['BoneName']in ['LeftShoulder','RightShoulder','LeftArm','RightArm','LeftForeArm','RightForeArm','LeftHand','RightHand']:
   for k in ['X','Y','Z','Pitch','Yaw','Roll']:part[k]=0.0
assert seed==new
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
sdk=Path('/tmp/dayz-native162/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c').read_text()
for name in ['SledgeHammer','BaseballBat']:assert re.search(r'AddItemInHandsProfileIK\("'+name+r'"[^\n]*twoHanded',sdk)
print('PASS:requested4NPCscene/items/cleanup/sharedclock;independent nonrifle bank/native arm seed;5approvedbanks+graph+playercategory/camera preserved;bank selection scope verified. Native compile/grip/visuals NOT RUN.')
