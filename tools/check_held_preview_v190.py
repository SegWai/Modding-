"""Offline isolation, scene, clock and native-camera regressions."""
from pathlib import Path
import sys,re,hashlib
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v189';b=a.with_name('MovementLab_ADS_Lean_Mosin_v190')
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['MLHeldLeanPreset.json','LogicSource/Presets/MLHeldLeanPreset.json','Profiles/LeanMosin/MLHeldLeanPreset.json']:assert(b/rel).read_bytes()==(a/'MLUnarmedLeanPreset.json').read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert 'Create(actor, "AK74", 0)'in mission and 'actor.ML190StartHeldComparison()'in mission
assert 'actor.ML183StartUnarmedComparison(false)'in mission and 'ML183StartUnarmedComparison(nativeReference)'not in mission
assert 'MLADSLeanSettings.DemoActor = m_ML182NativeNPC'in mission
assert 'right * 0.5'in mission
clock=(b/'LogicSource/Scripts/4_World/MLSharedPose181.c').read_text()
assert 'ML190WeaponState.Open'in clock and 'ML190WeaponState.EditLeft'in clock and 'elapsed / 1000'in clock
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text()
assert 'leftValues = ML190WeaponState.LeftValues'in h and 'leftBody = ML190BodyState.Left'in h
assert 'heldPose && !HeldEditor && armIndex < 6'in h
assert 'heldPose && !HeldEditor && partIndex >= 8'in h
assert 'ML190WeaponState.Bound = Bound'in h
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):
 s=p.read_text();assert 'ML183WeaponState'not in s and 'ML183BodyState'not in s
bank=(b/'LogicSource/Scripts/4_World/MLHeldPreset190.c').read_text()
assert 'MLUnarmedLeanPreset.json'not in bank and '$profile:MLHeldLeanPreset.json'in bank
assert 'data.LeftLean' in bank and 'data.RightLean'in bank
# Shared scene is never driven by independent actor timers.
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
assert 'm_MLADSLeanDemoSign = ML181CrouchCycle.Target(GetGame().GetTime())'in player
assert 'm_ML183UnarmedPose.HeldEditor = m_ML190HeldPreview'in player
# Preserve the native float-expression fix that previously blocked loading.
n=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())['ML187_PublishHeldLean']
for field in ['WeaponDirLr','WeaponDirUd','WeaponRoll']:assert field+' "0.0"'in n
print('PASS:armed red/unchanged blue scene,shared clock/editor side,isolated MLHeldLeanPreset/4 approved banks,native camera override removed,unchanged graph +float fix. Native compile/grip/UI/runtime NOT RUN.')
