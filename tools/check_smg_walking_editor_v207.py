"""SMG preview-only editor isolation and requested six-actor lineup."""
from pathlib import Path
import re
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v206';b=a.with_name('MovementLab_ADS_Lean_Mosin_v207')
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLPistolLeanPreset.json','MLBatLeanPreset.json','MLOneHandedLeanPreset.json','MLHeavyLeanPreset.json','MLPolearmLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['MLSMGWalkingLeanPreset.json','LogicSource/Presets/MLSMGWalkingLeanPreset.json','Profiles/LeanMosin/MLSMGWalkingLeanPreset.json']:assert(b/rel).read_bytes()==(a/'MLHeldLeanPreset.json').read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();items=re.findall(r'items.Insert\("([^"]*)"\)',m)
assert items==['MP5K','SledgeHammer','WoodAxe','Shovel','Pitchfork','Flashlight']
assert 'if (itemType == "MP5K")\n   actor.ML207EnableSmgEditor();'in m
assert 'if (items[index] == "MP5K")\n    MLADSLeanSettings.DemoActor = preview;'in m
helper=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text()
config=helper[helper.index(' bool ConfigureLineup('):helper.index(' void UpdatePlayer(')]
assert 'actor.ML207UsesSmgEditor() && kind == ItemBehaviorType.FIREARMS'in config
assert 'bool rifle = kind == ItemBehaviorType.FIREARMS && !smg;'in config
assert 'SmgWalkingEditor != smg'in config and 'SmgWalkingEditor = smg;'in config
assert 'leftValues ='not in helper[helper.index(' void Bind('):helper.index(' ML172Snapshot Capture(')]
assert 'leftValues = ML207WeaponState.LeftValues'in helper[helper.index(' void Update('):]
# Global player routing must remain byte-identical: no new SMG deployment.
old=(a/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();new=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
start='  bool sharedStanding = routingState.m_iStanceIdx';end=' protected void ML173UpdateGraph('
assert old[old.index(start):old.index(end)]==new[new.index(start):new.index(end)]
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):assert 'ML204WeaponState'not in p.read_text()
clock=(b/'LogicSource/Scripts/4_World/MLLineupClock206.c').read_text();assert clock.index('if (elapsed < 12000)')<clock.index('if (ML207WeaponState.Open)')
bank=(b/'LogicSource/Scripts/4_World/MLSMGWalkingPreset207.c').read_text();assert '$profile:MLSMGWalkingLeanPreset.json'in bank and 'MLHeldLeanPreset.json'not in bank
print('PASS:6requestedactors/bat excluded;SMG-only preview flag+bank/cache;10standingdefaults+globalplayerroute+graph untouched;independent save;editor warmup safe. Native compile/visible editor/grip/gait/FPS NOT RUN.')
