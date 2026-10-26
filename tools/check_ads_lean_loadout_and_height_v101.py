"""Check vertical-only arm correction, stable right path and SDK loadout wiring."""
from pathlib import Path
import re,json,math
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v95';b=base/'MovementLab_ADS_Lean_Mosin_v101'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());d=json.loads((b/'Left-Shoulder-Height-v101.json').read_text())
assert old.keys()==new.keys()
changed={n for n in old if old[n]!=new[n]};assert len(changed)==18 and all(n.startswith('ML32_ReferenceHold_') for n in changed)
for name,node in old.items():
 if name.startswith('ML39_RightMovingLower_'):assert node==new[name]
assert abs(d['common_hand_shift_m'][0])<1e-12 and abs(d['common_hand_shift_m'][2])<1e-12
result=bridge.reconstruct(d['base'],d['parents'],{n:{'rotation_xyz':d['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in d['parents']})
for n in result:np.testing.assert_allclose(result[n],d['desired'][n],atol=1e-8)
for hand in ('LeftHand','RightHand'):
 np.testing.assert_allclose(np.array(result[hand])[:3,3]-np.array(d['previous_desired'][hand])[:3,3],d['common_hand_shift_m'],atol=1e-9)
 np.testing.assert_allclose(np.array(result[hand])[:3,:3],np.array(d['previous_desired'][hand])[:3,:3],atol=1e-9)
height_new=result['RightHand'][1][3]-result['RightShoulder'][1][3];height_right=d['right_reference_wrist'][1][3]-d['right_reference_shoulder'][1][3];assert abs(height_new-height_right)<1e-9
for n in ('Pelvis','Spine','Spine1','Spine2','Spine3','Head','LeftShoulder','RightShoulder','LeftFoot','RightFoot'):
 np.testing.assert_allclose(result[n],d['previous_desired'][n],atol=1e-8)
# Existing camera remains byte-identical except version diagnostics.
cam='LogicSource/Scripts/4_World/MLADSLeanCamera.c';assert (a/cam).read_text().replace('MLCAM95','MLCAM101')==(b/cam).read_text()
mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();ammo=(b/'LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c').read_text()
assert 'CreateAttachment("Mosin9130")' not in mission
for weapon in ('AK74','MP5K','FNX45','SVD'):assert '"'+weapon+'"' in mission and 'IsKindOf("'+weapon+'")' in ammo
for entity,index in [('ak',0),('mp5',1),('pistol',2),('sniper',3)]:assert 'SetQuickBarEntityShortcut('+entity+', '+str(index)+', true)' in mission
for name in ('MP5k_StockBttstck','MP5_RailHndgrd','ReflexOptic','UniversalLight','FNP45_MRDSOptic','TLRLight','PSO1Optic','AK_Suppressor','PistolSuppressor','Mag_MP5_30Rnd','Mag_FNX45_15Rnd','Mag_SVD_10Rnd'):
 assert '"'+name+'"' in ammo
# Names are checked against actual official SDK debug loadouts/classes.
sdk=Path('/tmp/dayz-lean-sdk/scripts/4_world/entities/firearms')
for relative,names in [('smg/mp5.c',['MP5k_StockBttstck','MP5_RailHndgrd','ReflexOptic','UniversalLight','Mag_MP5_30Rnd']),('pistol/fnx45.c',['PistolSuppressor','FNP45_MRDSOptic','TLRLight','Mag_FNX45_15Rnd']),('rifle/svd.c',['PSO1Optic','AK_Suppressor','Mag_SVD_10Rnd'])]:
 source=(sdk/relative).read_text()
 for name in names:assert '"'+name+'"' in source
assert 'AttachPart(part, "Battery9V")' in ammo
assert 'GetCurrentModeAutoFire' in ammo and 'SetAutomatic(weapon)' in ammo
assert 'CreateObjectEx(weaponType, groundPosition, ECE_PLACE_ON_SURFACE)' in ammo
assert 'AliceBag_Green' in mission
# NPC remains the same AK74, not one of the new player weapons.
npc=mission[mission.index(' void MLADSLeanSpawnTarget()'):mission.index(' void MLADSLeanOnDemoKilled')]
assert 'CreateInHands("AK74")' in npc
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'MLSTOCK101' in player and 'm_ML101CaptureDone[4]' in player
assert 'KC_F8 && m_ML71ControlDown' in (b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
print('PASS: vertical-only left target shift, stable right/body/camera and native capture retained; MP5/FNX/SVD names/attachments match SDK, quickbar, storage fallback and ammo support wired. Native compilation/inventory/arm retention unverified.')
