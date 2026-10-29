"""Two-item comparison, soda-only edit bank and untouched approved defaults."""
from pathlib import Path
import re
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v213';b=a.with_name('MovementLab_ADS_Lean_Mosin_v214')
for p in (a/'LogicSource/Presets').glob('*.json'):
 for rel in [p.name,'LogicSource/Presets/'+p.name,'Profiles/LeanMosin/'+p.name]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['MLSodaCanWalkingLeanPreset.json','LogicSource/Presets/MLSodaCanWalkingLeanPreset.json','Profiles/LeanMosin/MLSodaCanWalkingLeanPreset.json']:assert(b/rel).read_bytes()==(a/'MLOneHandedWalkingLeanPreset.json').read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();spawn=m[m.index(' void ML181SpawnCrouchPair()'):m.index(' override void OnMissionFinish()')]
assert re.findall(r'items.Insert\("([^"]*)"\)',spawn)==['SodaCan_Cola','BandageDressing']
assert spawn.count('ML213SpawnRow(')==1 and 'ML206CreatePreview('not in spawn
assert 'if (itemType == "SodaCan_Cola")\n   actor.ML214EnableCanEditor();'in m
assert 'if (walking && items[index] == "SodaCan_Cola")'in m
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();old=(a/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();start='  bool sharedStanding = routingState.m_iStanceIdx';end=' protected void ML173UpdateGraph('
assert player[player.index(start):player.index(end)]==old[old.index(start):old.index(end)]
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'leftValues ='not in h[h.index(' void Bind('):h.index(' ML172Snapshot Capture(')]
assert 'walkingPreview && actor.ML214UsesCanEditor() && kind == ItemBehaviorType.ONEHANDED'in h
assert 'kind == ItemBehaviorType.ONEHANDED && !flash && !can'in h
assert 'leftValues = ML214WeaponState.LeftValues'in h[h.index(' void Update('):]
assert 'CanWalkingEditor != can'in h
for p in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):assert 'ML211WeaponState'not in p.read_text()
assert 'ML214WeaponState.Open'in (b/'LogicSource/Scripts/4_World/MLLineupClock206.c').read_text()
bank=(b/'LogicSource/Scripts/4_World/MLSodaCanWalkingPreset214.c').read_text();assert '$profile:MLSodaCanWalkingLeanPreset.json'in bank and 'MLOneHandedWalkingLeanPreset.json'not in bank
print('PASS:only soda/bandage scene+clock;explicit soda-only editor/private save/mutuallyexclusive bank/cache;13prior raw defaults/playerroute/graph unchanged. Native compile/grip/gait/visuals NOT RUN.')
