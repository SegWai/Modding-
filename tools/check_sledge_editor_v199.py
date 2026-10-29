"""Verify frozen approved bat reference and separately editable sledge preview."""
from pathlib import Path
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v198';b=a.with_name('MovementLab_ADS_Lean_Mosin_v199')
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLPistolLeanPreset.json','MLBatLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['MLSledgehammerLeanPreset.json','LogicSource/Presets/MLSledgehammerLeanPreset.json','Profiles/LeanMosin/MLSledgehammerLeanPreset.json']:assert(b/rel).read_bytes()==(a/'MLBatLeanPreset.json').read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
assert(a/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_bytes()==(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_bytes()
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert '"Hoodie_Grey", true, "BaseballBat", false)'in m
assert '"Hoodie_Black", true, "SledgeHammer", true)'in m
assert 'vanillaLean'not in m and 'ML183StartUnarmedComparison(true)'not in m
assert 'actor.ML199StartSledgeComparison()'in m and 'actor.ML193StartOtherHeldComparison()'in m
assert m.count('= ML181CreatePreview(')==3
assert 'MLADSLeanSettings.DemoActor = m_ML198CustomHammer'in m
for n in ['m_ML199BatReference','m_ML198CustomHammer','m_ML182CustomNPC']:assert 'ObjectDelete('+n+')'in m
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'leftValues ='not in h[h.index(' void Bind('):h.index(' ML172Snapshot Capture(')]
assert 'leftValues = ML199WeaponState.LeftValues'in h[h.index(' void Update('):]
assert 'leftValues = ML193WeaponState.LeftValues'in h and 'if (SledgeEditor)'in h
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):
 assert 'ML193WeaponState'not in p.read_text() and 'ML193BodyState'not in p.read_text()
bank=(b/'LogicSource/Scripts/4_World/MLSledgePreset199.c').read_text();assert '$profile:MLSledgehammerLeanPreset.json'in bank and 'MLBatLeanPreset.json'not in bank
clock=(b/'LogicSource/Scripts/4_World/MLSharedPose181.c').read_text();assert 'ML199WeaponState.Open'in clock and 'ML199WeaponState.EditLeft'in clock
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
print('PASS:custom bat reference + isolated sledge editor + blue;native sledge removed;independent save/menus/clock;7approved banks+graph+player category unchanged. Native compile/appearance NOT RUN.')
