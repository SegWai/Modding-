"""Heavy approved rollout plus isolated pitchfork authoring preview."""
from pathlib import Path
import hashlib
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v203';b=a.with_name('MovementLab_ADS_Lean_Mosin_v204');digest='4c236a08839f3d8e03490e722a74619dce5cdba74587fb4aaba49bdd15cd1616'
for rel in ['MLHeavyLeanPreset.json','LogicSource/Presets/MLHeavyLeanPreset.json','Profiles/LeanMosin/MLHeavyLeanPreset.json']:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest
for rel in ['ads-lean-test/User-Presets/Current-MLHeavyLeanPreset.json','ads-lean-test/User-Presets/MLHeavyLeanPreset-Approved-20261029.json','artifacts/MLHeavyLeanPreset.json']:assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==digest
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLPistolLeanPreset.json','MLBatLeanPreset.json','MLOneHandedLeanPreset.json','MLHeavyLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();assert '"Pitchfork"'in m and '"WoodenCrate"'not in m
assert m.count('= ML181CreatePreview(')==2 and 'actor.ML204StartPolearmComparison()'in m
assert 'MLADSLeanSettings.DemoActor = m_ML204PolearmNPC'in m and 'ObjectDelete(m_ML204PolearmNPC)'in m
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'leftValues ='not in h[h.index(' void Bind('):h.index(' ML172Snapshot Capture(')]
assert 'leftValues = ML204WeaponState.LeftValues'in h[h.index(' void Update('):] and 'ReferenceHeavyBank != HeavyEditor'in h
bank=(b/'LogicSource/Scripts/4_World/MLPolearmPreset204.c').read_text();assert '$profile:MLPolearmLeanPreset.json'in bank
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):assert 'ML202WeaponState'not in p.read_text()
clock=(b/'LogicSource/Scripts/4_World/MLSharedPose181.c').read_text();assert 'ML204WeaponState.Open'in clock
category=(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_text();assert 'behavior.m_iType == ItemBehaviorType.HEAVY'in category
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'HeavyEditor = MLHeldCategory192.UsesHeavyHolding(this)'in player
cfg=Path('/tmp/dayz-native162/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c').read_text()
line=next(l for l in cfg.splitlines()if 'AddItemInHandsProfileIK("Pitchfork"'in l);assert 'poleArms'in line
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
print('PASS:heavy approved6copies/category/reset;9approvedbanks unchanged;pitchfork POLEARMS native evidence/scene/editor/save/menu scope;graph/native camera retained. Native compile/grip/visuals NOT RUN.')
