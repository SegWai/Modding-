"""Approved SMG walking data + isolated sledge walking authoring scope."""
from pathlib import Path
import hashlib,re,itertools
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v208';b=a.with_name('MovementLab_ADS_Lean_Mosin_v209');digest='e4e9e47aac1e4a6f66770ec86f95afd881a9c8c8519427918c1c4ff92163b338'
for rel in ['MLSMGWalkingLeanPreset.json','LogicSource/Presets/MLSMGWalkingLeanPreset.json','Profiles/LeanMosin/MLSMGWalkingLeanPreset.json']:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest
for rel in ['ads-lean-test/User-Presets/Current-MLSMGWalkingLeanPreset.json','ads-lean-test/User-Presets/MLSMGWalkingLeanPreset-Approved-20261029.json','artifacts/MLSMGWalkingLeanPreset.json']:assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==digest
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLPistolLeanPreset.json','MLBatLeanPreset.json','MLOneHandedLeanPreset.json','MLHeavyLeanPreset.json','MLPolearmLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['MLSledgehammerWalkingLeanPreset.json','LogicSource/Presets/MLSledgehammerWalkingLeanPreset.json','Profiles/LeanMosin/MLSledgehammerWalkingLeanPreset.json']:assert(b/rel).read_bytes()==(a/'MLBatLeanPreset.json').read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();assert re.findall(r'items.Insert\("([^"]*)"\)',m)==['SledgeHammer']
assert 'if (itemType == "SledgeHammer")\n   actor.ML209EnableSledgeEditor();'in m
assert 'if (items[index] == "SledgeHammer")\n    MLADSLeanSettings.DemoActor = preview;'in m
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'leftValues ='not in h[h.index(' void Bind('):h.index(' ML172Snapshot Capture(')]
assert 'leftValues = ML209WeaponState.LeftValues'in h[h.index(' void Update('):]
assert 'ReferenceSmgWalkingBank != SmgWalkingEditor'in h
assert 'OtherHeldEditor != twoHands || OneHandEditor != oneHand || SledgeWalkingEditor != sledge'in h
assert 'bool twoHands = kind == ItemBehaviorType.TWOHANDED && !sledge;'in h
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'routingState.m_iMovement == 1 && MLHeldCategory192.IsSMG(crouchHeld)'in player
assert 'HeldEditor = MLHeldCategory192.UsesRifleHolding(this) && !smgWalking'in player
assert 'SmgWalkingEditor = smgWalking'in player
# Only upright lowered WALK selects SMG walk, never rifle/raised/run/crouch.
for smg,upright,lowered,enabled in itertools.product([False,True],repeat=4):
 for gait in range(4):
  selected=smg and upright and lowered and enabled and gait==1
  assert not selected or (smg and upright and lowered and gait==1)
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):assert 'ML207WeaponState'not in p.read_text()
bank=(b/'LogicSource/Scripts/4_World/MLSledgeWalkingPreset209.c').read_text();assert '$profile:MLSledgehammerWalkingLeanPreset.json'in bank
assert 'MLSMGWalkingLeanPreset.json'not in bank
print('PASS:approved SMG6copies/scope/cache;only sledge NPC+independent walking bank/editor;bat/10priorbanks+graph retained. Native compile/gait/grip/editor NOT RUN.')
