"""Verify approved raw preset rollout and synchronized weapon comparison scene."""
from pathlib import Path
import hashlib,re
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v191';b=a.with_name('MovementLab_ADS_Lean_Mosin_v192');digest='f4522bf7f9a4b153373f129c88d7353b7b316927ff409fde9a64e958cdd57ad4'
for rel in ['MLHeldLeanPreset.json','LogicSource/Presets/MLHeldLeanPreset.json','Profiles/LeanMosin/MLHeldLeanPreset.json']:
 assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest,rel
for rel in ['ads-lean-test/User-Presets/Current-MLHeldLeanPreset.json','ads-lean-test/User-Presets/MLHeldLeanPreset-Approved-20261029.json','artifacts/MLHeldLeanPreset.json']:
 assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==digest
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
category=(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_text()
assert 'behavior.m_iType == ItemBehaviorType.FIREARMS'in category and 'GetItemInHandsBehaviourCfg()'in category
assert 'IsKindOf'not in category and 'Weapon_Base.Cast'not in category
sdk=Path('/tmp/dayz-native162/scripts/3_game/humanitems.c').read_text();assert 'GetItemInHandsBehaviourCfg()'in sdk and 'm_iType'in sdk
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
assert 'HeldEditor = MLHeldCategory192.UsesRifleHolding(this)'in player
helper=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text();assert 'ReferenceHeldBank != HeldEditor'in helper
mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert 'string weaponType = "SVD"'in mission and '"Hoodie_Green", true, "MP5K"'in mission
assert 'm_MLADSLeanTargetPosition - right * 0.5'in mission and 'm_MLADSLeanTargetPosition + right * 0.5'in mission
assert 'actor.ML190StartHeldComparison()'in mission and 'actor.ML183StartUnarmedComparison(false)'in mission
assert 'ObjectDelete(m_ML192SMGNPC)'in mission
assert(a/'LogicSource/Scripts/4_World/MLSharedPose181.c').read_bytes()==(b/'LogicSource/Scripts/4_World/MLSharedPose181.c').read_bytes()
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
# SDK evidence: native SMG, rifle and sniper registrations share FIREARMS behavior.
cfg=Path('/tmp/dayz-native162/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c').read_text()
for name in ['AK74_Base','MP5K_Base','SVD_Base']:
 line=next(line for line in cfg.splitlines()if 'AddItemInHandsProfileIK("'+name+'"'in line)
 assert 'fireArmsItemBehaviour'in line
print('PASS:6 exact approved held-preset copies;4 old banks unchanged;native behavior API/category and SMG/rifle/sniper registrations;player bank invalidation;3-NPC shared clock/scene/cleanup;graph/native camera unchanged. Native compile/fit NOT RUN.')
