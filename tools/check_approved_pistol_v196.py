"""Approved pistol data integrity, routing isolation and native category evidence."""
from pathlib import Path
import sys,hashlib,re,json
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v195';b=a.with_name('MovementLab_ADS_Lean_Mosin_v196');digest='4ac93abf222dc4b51e23983a63e14820b9e81f59c42970e0adaae2cfd8a9bdcb'
for rel in ['MLPistolLeanPreset.json','LogicSource/Presets/MLPistolLeanPreset.json','Profiles/LeanMosin/MLPistolLeanPreset.json']:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest
for rel in ['ads-lean-test/User-Presets/Current-MLPistolLeanPreset.json','ads-lean-test/User-Presets/MLPistolLeanPreset-Approved-20261029.json','artifacts/MLPistolLeanPreset.json']:assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==digest
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLBatLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
assert(a/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()==(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()
for p in (a/'LogicSource/Scripts/5_Mission').glob('*.c'):assert p.read_bytes()==(b/p.relative_to(a)).read_bytes()
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text()
assert 'ReferencePistolBank != PistolBank'in h
assert 'leftValues = ML196WeaponState.LeftValues'in h[h.index(' void Update('):]
assert 'leftValues ='not in h[h.index(' void Bind('):h.index(' ML172Snapshot Capture(')]
assert '!PistolBank && armIndex < 6'in h
cat=(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_text();pistol=cat[cat.index(' static bool UsesPistolHolding'):cat.index(' static bool UsesRifleHolding')]
assert 'ItemBehaviorType.PISTOLS'in pistol and 'IsKindOf'not in pistol
bank=(b/'LogicSource/Scripts/4_World/MLPistolPreset196.c').read_text();assert '$profile:MLPistolLeanPreset.json'in bank and 'MLBatLeanPreset'not in bank
cfg=Path('/tmp/dayz-native162/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c').read_text()
profiles=[]
for line in cfg.splitlines():
 if 'AddItemInHandsProfileIK('in line and 'pistolItemBehaviour'in line:profiles.append(re.search(r'AddItemInHandsProfileIK\("([^"]+)"',line)[1])
assert 'Flaregun_Base'in profiles and 'Magnum_Base'in profiles and 'Glock19_Base'in profiles
for n in ['Flashlight','Compass','SodaCan_ColorBase','BandageDressing']:
 line=next(l for l in cfg.splitlines()if 'AddItemInHandsProfileIK("'+n+'"'in l);assert 'toolsOneHanded'in line
print('PASS:6 exact approved pistol copies;5 prior approved+bat bank/scene/menus/graph unchanged;isolated player pistol-bank and reset;native pistol/nonpistol registrations. Pistol category:',', '.join(profiles))
print('Native compile/grip/render NOT RUN.')
