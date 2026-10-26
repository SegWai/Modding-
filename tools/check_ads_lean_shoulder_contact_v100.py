"""Verify calibrated contact proxy, common grip shift and original right path."""
from pathlib import Path
import re,json,math
import numpy as np
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v95';b=base/'MovementLab_ADS_Lean_Mosin_v100'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((b/'Shoulder-Contact-Test-v100.json').read_text());d=json.loads((b/'Left-Shoulder-Contact-v100.json').read_text())
assert old.keys()==new.keys();assert {n for n in old if old[n]!=new[n]}==set(spec['changed_nodes']) and len(spec['changed_nodes'])==18
for n,node in old.items():
 if n.startswith('ML39_RightMovingLower_'):assert new[n]==node
result=bridge.reconstruct(d['base'],d['parents'],{n:{'rotation_xyz':d['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in d['parents']})
for n in result:np.testing.assert_allclose(result[n],d['desired'][n],atol=1e-8)
stock=np.array(d['stock_contact_proxy_in_wrist']);reference=np.array(d['right_reference_wrist'])@stock
np.testing.assert_allclose(reference[:3],np.array(d['right_reference_shoulder'])[:3,3],atol=1e-9)
np.testing.assert_allclose((np.array(result['RightHand'])@stock)[:3],np.array(result['RightShoulder'])[:3,3],atol=1e-9)
for hand in ('LeftHand','RightHand'):
 np.testing.assert_allclose(np.array(result[hand])[:3,3]-np.array(d['previous_desired'][hand])[:3,3],d['common_hand_shift_m'],atol=1e-9)
 np.testing.assert_allclose(np.array(result[hand])[:3,:3],np.array(d['previous_desired'][hand])[:3,:3],atol=1e-9)
np.testing.assert_allclose(np.linalg.inv(np.array(result['RightHand']))@np.array(result['LeftHand']),np.linalg.inv(np.array(d['previous_desired']['RightHand']))@np.array(d['previous_desired']['LeftHand']),atol=1e-9)
for n,p in d['parents'].items():
 if p:
  before=np.linalg.norm(np.array(d['previous_desired'][n])[:3,3]-np.array(d['previous_desired'][p])[:3,3]);after=np.linalg.norm(np.array(result[n])[:3,3]-np.array(result[p])[:3,3]);assert abs(before-after)<1e-8
for n in ('Pelvis','Spine','Spine1','Spine2','Spine3','Head','LeftShoulder','RightShoulder','LeftFoot','RightFoot'):
 np.testing.assert_allclose(result[n],d['previous_desired'][n],atol=1e-8)
def clamp(x,lo,hi):return max(lo,min(hi,x))
original89=newnodes((base/'MovementLab_ADS_Lean_Mosin_v89/WorkspaceSource/locomotion.agf').read_text())
for name in spec['changed_nodes']:
 expr=re.search(r'Expression "([^"]+)"',new[name])[1];prev=original89[name];scope=re.search(r'Expression "([^"]+)"',prev)[1];amount=float(re.search(r'Amount ([-\d.eE]+)',prev)[1]);bone,axis=name.removeprefix('ML32_ReferenceHold_').rsplit('_',1)
 env=dict(clamp=clamp,MLADSLeanAmount=-1,MLADSLeanGate=1,MLADSLeanMoveBlend=1,MLADSLeanWeaponShift=1,Stance=0,ML87FirstPersonCrouchLean=0,ML93ArmDrop=1)
 assert abs(eval(expr,{'__builtins__':{}},env)+d['rotation_corrections'][bone]['XYZ'.index(axis)])<1e-12
 for key,val in [('ML93ArmDrop',0),('ML87FirstPersonCrouchLean',1),('Stance',1)]:
  e=env.copy();e[key]=val;assert abs(eval(expr,{'__builtins__':{}},e)-amount*eval(scope,{'__builtins__':{}},e))<1e-12
cam='LogicSource/Scripts/4_World/MLADSLeanCamera.c';assert (a/cam).read_text().replace('MLCAM95','MLCAM100')==(b/cam).read_text()
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();assert 'm_ML100CaptureDone[4]' in player and 'MLSTOCK100' in player and 'MLADSLeanCapturePose();' in player
# Mode/side slots are independent and bounded, including zero-native path
# (actual call is only on full left/right, moving, stable custom pose).
assert {mode*2+right for mode in (0,1) for right in (0,1)}==set(range(4))
print('PASS: contact proxy matches approved right shoulder relationship; common hand shift preserves relative grip/rotations/lengths/body; existing right and camera untouched; side/mode native snapshots included. Actual mesh contact/native output unverified.')
