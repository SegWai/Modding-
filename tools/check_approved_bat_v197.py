"""Approved raw bat preset and exact holding-family scope, not all TWOHANDED."""
from pathlib import Path
import hashlib,re
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v196';b=a.with_name('MovementLab_ADS_Lean_Mosin_v197');digest='d55bf37cbc5a93729c7474a633e6c40a1c184fb17cecd63b27b631cc90dda98e'
for rel in ['MLBatLeanPreset.json','LogicSource/Presets/MLBatLeanPreset.json','Profiles/LeanMosin/MLBatLeanPreset.json']:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest
for rel in ['ads-lean-test/User-Presets/Current-MLBatLeanPreset.json','ads-lean-test/User-Presets/MLBatLeanPreset-Approved-20261029.json','artifacts/MLBatLeanPreset.json']:assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==digest
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json','MLHeldLeanPreset.json','MLPistolLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
assert(a/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()==(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()
cat=(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_text();assert 'behavior.m_iType != ItemBehaviorType.TWOHANDED'in cat and 'animationInstance.Contains("player_main_2h_bat")'in cat
h=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'ReferenceBatBank != OtherHeldEditor'in h
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'OtherHeldEditor = MLHeldCategory192.UsesBatHolding(this)'in player
# Verify native API declaration and actual registrations, rather than treating
# visually similar two-handed tools as the same animation.
human=Path('/tmp/dayz-native162/scripts/3_game/human.c').read_text();assert 'DebugGetItemAnimInstance()'in human
cfg=Path('/tmp/dayz-native162/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c').read_text()
for n in ['BaseballBat','NailedBaseballBat','BarbedBaseballBat','XmasBaseballBat']:
 line=next(l for l in cfg.splitlines()if 'AddItemInHandsProfileIK("'+n+'"'in l)
 assert 'player_main_2h_bat.asi'in line and 'twoHanded'in line
for n in ['SledgeHammer','Shovel','FirefighterAxe','WoodAxe']:
 matches=[l for l in cfg.splitlines()if 'AddItemInHandsProfileIK("'+n+'"'in l]
 for line in matches:assert 'player_main_2h_bat.asi'not in line
for p in (a/'LogicSource/Scripts/5_Mission').glob('*.c'):assert p.read_bytes()==(b/p.relative_to(a)).read_bytes()
print('PASS:6 exact bat copies;6 prior approved banks unchanged;native bat family/API and unrelated tool exclusion;player bank cache invalidation;scene/menus/graph unchanged. Native compile/instance availability/grip NOT RUN.')
