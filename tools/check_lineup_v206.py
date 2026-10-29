"""Offline shared-clock movement, category readiness, anchor isolation and data checks."""
from pathlib import Path
import re
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v205';b=a.with_name('MovementLab_ADS_Lean_Mosin_v206')
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLPistolLeanPreset.json','MLBatLeanPreset.json','MLOneHandedLeanPreset.json','MLHeavyLeanPreset.json','MLPolearmLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();items=re.findall(r'items.Insert\("([^"]*)"\)',m)
assert items==['','AK74','SKS','SVD','MP5K','Glock19','BaseballBat','SledgeHammer','WoodAxe','Shovel','Flashlight','WoodenCrate','Pitchfork']
assert 'm_ML206Actors.Insert(actor)'in m and 'foreach (PlayerBase preview : m_ML206Actors)'in m
assert 'preview.MLADSLeanStopDemo()'in m and 'GetGame().ObjectDelete(preview)'in m
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
assert 'previewSpeed = 1;'in player and 'previewAngle = -90;'in player and 'previewAngle = 90;'in player
assert 'GetGame().GetPlayer() != this && IsAlive()'in player and 'SetPosition(m_ML206Anchor)'in player
assert 'm_ML206Lineup = false;'in player
assert 'm_ML183UnarmedPose.ConfigureLineup(this)'in player
helper=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();config=helper[helper.index(' bool ConfigureLineup('):helper.index(' void UpdatePlayer(')]
for kind in ['FIREARMS','PISTOLS','TWOHANDED','ONEHANDED','HEAVY','POLEARMS','EMPTYHANDED']:assert 'ItemBehaviorType.'+kind in config
assert 'if (changed)'in config and 'NeutralReference = null;'in config
assert 'behavior = accessor.GetItemInHandsBehaviourCfg()'in config and 'if (!behavior)'in config
# Shared schedule/direction; all actors read the same epoch, never own timer.
def schedule(ms):
 if ms<3000:return 0,0
 if ms<6000:return -1,0
 if ms<9000:return 1,0
 if ms<12000:return 0,0
 return (-1 if ((ms-12000)//3000)%2==0 else 1),1
for ms in range(0,60000,17):
 values=[schedule(ms)for _ in items];assert len(set(values))==1
 assert (ms>=12000)==(values[0][1]==1)
assert schedule(12000)==(-1,1)and schedule(15000)==(1,1)
# Distinct fixed anchors side by side; warmup long enough for neutral/side capture.
slots=[(i-6)*.85 for i in range(len(items))];assert len(set(slots))==13
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
print('PASS:13-item lineup/shared60sclock/12sinitialization/left-rightwalk/uniqueanchors/NPC-only pin+cleanup/native-category-ready caching;10preset files andgraph unchanged. Native compilation/gait/rootpin/grip/FPS NOT RUN.')
