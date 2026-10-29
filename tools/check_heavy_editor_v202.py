"""Heavy editor isolation plus approved one-handed default integrity."""
from pathlib import Path
import hashlib
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v201';b=a.with_name('MovementLab_ADS_Lean_Mosin_v202');digest='ba30dc20673f58534bf9e801dbde48cdd948543035faf7872e6863b128f4a1ca'
for rel in ['MLOneHandedLeanPreset.json','LogicSource/Presets/MLOneHandedLeanPreset.json','Profiles/LeanMosin/MLOneHandedLeanPreset.json']:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest
for rel in ['ads-lean-test/User-Presets/Current-MLOneHandedLeanPreset.json','ads-lean-test/User-Presets/MLOneHandedLeanPreset-Approved-20261029.json','artifacts/MLOneHandedLeanPreset.json']:assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==digest
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLPistolLeanPreset.json','MLBatLeanPreset.json','MLOneHandedLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();assert '"WoodenCrate"'in m and '"Flashlight"'not in m
assert 'actor.ML202StartHeavyComparison()'in m and m.count('= ML181CreatePreview(')==2
assert 'MLADSLeanSettings.DemoActor = m_ML202HeavyNPC'in m and 'ObjectDelete(m_ML202HeavyNPC)'in m
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'leftValues ='not in h[h.index(' void Bind('):h.index(' ML172Snapshot Capture(')]
assert 'leftValues = ML202WeaponState.LeftValues'in h[h.index(' void Update('):] and 'ReferenceOneHandBank != OneHandEditor'in h
bank=(b/'LogicSource/Scripts/4_World/MLHeavyPreset202.c').read_text();assert '$profile:MLHeavyLeanPreset.json'in bank
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):assert 'ML200WeaponState'not in p.read_text()
clock=(b/'LogicSource/Scripts/4_World/MLSharedPose181.c').read_text();assert 'ML202WeaponState.Open'in clock
cat=(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_text();assert 'behavior.m_iType == ItemBehaviorType.ONEHANDED'in cat
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'OneHandEditor = MLHeldCategory192.UsesOneHandedHolding(this)'in player
cfg=Path('/tmp/dayz-native162/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c').read_text()
line=next(l for l in cfg.splitlines()if 'AddItemInHandsProfileIK("WoodenCrate"'in l);assert 'heavyItemBehaviour'in line
for name in ['Flashlight','Compass','SodaCan_ColorBase','BandageDressing']:
 line=next(l for l in cfg.splitlines()if 'AddItemInHandsProfileIK("'+name+'"'in l);assert 'toolsOneHanded'in line
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
print('PASS:approved onehand6rawcopies/category+cache;8banks unchanged;heavy wooden-crate editor/blue2NPCscene/saveisolation/clock/nativecategory;graph/camera retained. Native compile/grip/pose NOT RUN.')
