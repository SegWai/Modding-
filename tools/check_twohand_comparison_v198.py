"""User-authorized TWOHANDED scope and actual native/custom preview separation."""
from pathlib import Path
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v197';b=a.with_name('MovementLab_ADS_Lean_Mosin_v198')
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLPistolLeanPreset.json','MLBatLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
cat=(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_text();scope=cat[cat.index(' static bool UsesTwoHandedHolding'):cat.index(' static bool UsesPistolHolding')]
assert 'return behavior.m_iType == ItemBehaviorType.TWOHANDED'in scope
assert 'DebugGetItemAnimInstance'not in cat and 'IsKindOf'not in scope
mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert 'BaseballBat'not in mission and mission.count('= ML181CreatePreview(')==3
assert '"Hoodie_Grey", true, "SledgeHammer", true)'in mission
assert '"Hoodie_Black", true, "SledgeHammer", false)'in mission
assert 'actor.ML183StartUnarmedComparison(true)'in mission and 'actor.ML193StartOtherHeldComparison()'in mission
assert 'MLADSLeanSettings.DemoActor = m_ML198CustomHammer'in mission
for actor in ['m_ML198NativeHammer','m_ML198CustomHammer','m_ML182CustomNPC']:assert 'ObjectDelete('+actor+')'in mission
helper=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();branch=helper[helper.index('  if (nativeReference)\n  {',helper.index(' void Update(')):];assert branch.startswith('  if (nativeReference)\n  {\n   actor.AnimSetFloat(ActiveVar, 0);\n   return;')
for n in ['MLUnarmedPose183.c','MLSharedPose181.c','MLOtherHeldPreset193.c']:assert(a/'LogicSource/Scripts/4_World'/n).read_bytes()==(b/'LogicSource/Scripts/4_World'/n).read_bytes()
assert 'UsesTwoHandedHolding(this)'in (b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
cfg=Path('/tmp/dayz-native162/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c').read_text()
for n in ['BaseballBat','SledgeHammer','Shovel','FirefighterAxe','WoodAxe']:
 lines=[l for l in cfg.splitlines()if 'AddItemInHandsProfileIK("'+n+'"'in l]
 for line in lines:assert 'twoHanded'in line
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
print('PASS:explicit TWOHANDED category;native/custom sledge scene and bypass;editor targets custom only;all7rawbanks/graph/helper/clock/nativecamera unchanged. Native compile/appearance/grip NOT RUN.')
