"""Approved tool walking scope with bat exclusion and isolated flashlight editor."""
from pathlib import Path
import hashlib,re
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v210';b=a.with_name('MovementLab_ADS_Lean_Mosin_v211');digest='4276edbb8a47c6fad0567b732d480dff929129178f1df2ab2cebbfff1bf48521'
for rel in ['MLSledgehammerWalkingLeanPreset.json','LogicSource/Presets/MLSledgehammerWalkingLeanPreset.json','Profiles/LeanMosin/MLSledgehammerWalkingLeanPreset.json']:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest
for rel in ['ads-lean-test/User-Presets/Current-MLSledgehammerWalkingLeanPreset.json','ads-lean-test/User-Presets/MLSledgehammerWalkingLeanPreset-Approved-20261029.json','artifacts/MLSledgehammerWalkingLeanPreset.json']:assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==digest
for p in (a/'LogicSource/Presets').glob('*.json'):assert p.read_bytes()==(b/p.relative_to(a)).read_bytes()
for rel in ['MLOneHandedWalkingLeanPreset.json','LogicSource/Presets/MLOneHandedWalkingLeanPreset.json','Profiles/LeanMosin/MLOneHandedWalkingLeanPreset.json']:assert(b/rel).read_bytes()==(a/'MLOneHandedLeanPreset.json').read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
cat=(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_text();group=cat[cat.index(' static bool IsWalkingTool('):cat.index(' static bool IsSMG(')]
families=re.findall(r'IsKindOf\("([^"]+)"\)',group);assert set(families)=={'SledgeHammer','Shovel','WoodAxe','FirefighterAxe','Pitchfork'}
assert all(n not in families for n in ['BaseballBat','NailedBaseballBat','BarbedBaseballBat','XmasBaseballBat','Flashlight','FieldShovel'])
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'routingState.m_iMovement == 1 && MLHeldCategory192.IsWalkingTool(crouchHeld)'in player
assert 'SledgeWalkingEditor = toolWalking'in player
assert 'OtherHeldEditor = MLHeldCategory192.UsesTwoHandedHolding(this) && !toolWalking'in player
assert 'PolearmEditor = MLHeldCategory192.UsesPolearmHolding(this) && !toolWalking'in player
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'ReferenceToolWalkingBank != SledgeWalkingEditor'in h
assert 'leftValues ='not in h[h.index(' void Bind('):h.index(' ML172Snapshot Capture(')]
assert 'leftValues = ML211WeaponState.LeftValues'in h[h.index(' void Update('):]
assert 'OneHandWalkingEditor != flash'in h and 'actor.ML211UsesFlashEditor() && kind == ItemBehaviorType.ONEHANDED'in h
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();assert re.findall(r'items.Insert\("([^"]*)"\)',m)==['Flashlight']
assert 'actor.ML211EnableFlashEditor()'in m and 'if (items[index] == "Flashlight")\n    MLADSLeanSettings.DemoActor = preview;'in m
bank=(b/'LogicSource/Scripts/4_World/MLOneHandWalkingPreset211.c').read_text();assert '$profile:MLOneHandedWalkingLeanPreset.json'in bank
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):assert 'ML209WeaponState'not in p.read_text()
assert 'ML211WeaponState.Open'in (b/'LogicSource/Scripts/4_World/MLLineupClock206.c').read_text()
print('PASS:approved tool6copies/explicit5family/noBatFlashlightScope/walk-only/cache;onlyFlashlight+independent walkingeditor;all prior presets+graph retained. Native compile/gait/grip/UI NOT RUN.')
