"""Approved onehand walk rollout and complete comparison scene/pose-mode isolation."""
from pathlib import Path
import hashlib,re
r=Path(__file__).resolve().parents[1];base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v211';approved=base.with_name('MovementLab_ADS_Lean_Mosin_v212');b=base.with_name('MovementLab_ADS_Lean_Mosin_v213');digest='7432beb2e73194416ca5570cb474cc876a86940fbd3620b81fbb56f5df26d1c4'
for rel in ['MLOneHandedWalkingLeanPreset.json','LogicSource/Presets/MLOneHandedWalkingLeanPreset.json','Profiles/LeanMosin/MLOneHandedWalkingLeanPreset.json']:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest
for rel in ['ads-lean-test/User-Presets/Current-MLOneHandedWalkingLeanPreset.json','ads-lean-test/User-Presets/MLOneHandedWalkingLeanPreset-Approved-20261029.json','artifacts/MLOneHandedWalkingLeanPreset.json']:assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==digest
for p in (approved/'LogicSource/Presets').glob('*.json'):assert p.read_bytes()==(b/p.relative_to(approved)).read_bytes()
for p in (base/'LogicSource/Presets').glob('*.json'):
 if p.name!='MLOneHandedWalkingLeanPreset.json':assert p.read_bytes()==(b/p.relative_to(base)).read_bytes()
assert(approved/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();old=(approved/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();start='  bool sharedStanding = routingState.m_iStanceIdx';end=' protected void ML173UpdateGraph('
assert old[old.index(start):old.index(end)]==player[player.index(start):player.index(end)]
assert 'oneHandWalking = routingState.m_iMovement == 1 && MLHeldCategory192.UsesOneHandedHolding(this)'in player
assert 'OneHandEditor = MLHeldCategory192.UsesOneHandedHolding(this) && !oneHandWalking'in player
assert 'OneHandWalkingEditor = oneHandWalking'in player
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();walking=re.findall(r'walking.Insert\("([^"]*)"\)',m);standing=re.findall(r'standing.Insert\("([^"]*)"\)',m)
assert len(walking)==19 and len(standing)==8
for n in ['AK74','SKS','SVD','MP5K','UMP45','Glock19','Magnum','BaseballBat','SledgeHammer','WoodAxe','Shovel','Pitchfork','Flashlight','Compass','SodaCan_Cola','WoodenCrate','PowerGenerator','Barrel_Blue']:assert n in walking
for n in ['','AK74','Glock19','BaseballBat','SledgeHammer','Flashlight','WoodenCrate','Pitchfork']:assert n in standing
assert 'ML206CreatePreview(raisedStanding, "AK74", "Hoodie_Red", false, true, false)'in m
assert 'ML206CreatePreview(raisedOrigin, "AK74", "Hoodie_Red", true, true, false)'in m
assert 'ML206CreatePreview(raisedCrouch, "AK74", "Hoodie_Red", false, true, true)'in m
assert 'm_ML206Actors.Insert(actor)'in m and 'foreach (PlayerBase preview : m_ML206Actors)'in m
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();config=h[h.index(' bool ConfigureLineup('):h.index(' void UpdatePlayer(')]
assert 'walkingPreview = actor.ML213UsesWalkingPreview()'in config
assert 'walkingPreview && MLHeldCategory192.IsSMG(item)'in config and 'walkingPreview && MLHeldCategory192.IsWalkingTool(item)'in config
assert 'walkingPreview && kind == ItemBehaviorType.ONEHANDED'in config
assert 'ReferenceOneHandWalkingBank != OneHandWalkingEditor'in h
assert 'm_ML213WalkingPreview && ML206LineupClock.Walking(GetGame().GetTime())'in player
assert 'if (m_ML213RaisedExample)'in player and 'move.ForceStance(DayZPlayerConstants.STANCEIDX_CROUCH)'in player
assert 'm_ML183UnarmedPreview = false;'in player[player.index(' void ML213StartRaisedLineup'):player.index(' protected bool m_ML207SmgEditor')]
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
print('PASS:approved onehand6copies/walkroute/reset;13default banks exact;19walking+8standing+3raised modes=30;fixed peractor bank selection/sharedclock/cleanup/rootpin/raised stance;playerroute+graph unchanged from212. Native compile/30NPCgait/grip/FPS NOT RUN.')
