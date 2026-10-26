"""Confirm exact frame-15 selection and isolated read-only left calibration."""
from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v46';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v47'
a=(A/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();b=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
x=b.index(' // Read-only native baseline');y=b.index(' // Read-only calibration',x);helper=b[x:y]
rest=(b[:x]+b[y:]).replace('MLADSLEAN47','MLADSLEAN46').replace('MLPOSE47','MLPOSE46').replace('MLWALK47','MLWALK46')
assert rest==a, 'Existing body runtime, FP roll, NPC and walking capture must remain unchanged'
for f in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo','LogicSource/Scripts/4_World/MLADSLeanCamera.c'):
 assert (A/f).read_bytes()==(B/f).read_bytes(),f
for needed in ('m_MLADSLeanAmount > -0.98','m_MLADSLeanMoveBlend > 0.02','m_MLADSLeanGate < 0.98','!IsRaised()','leftReferenceState.m_iMovement != 0','STANCEIDX_ERECT','STANCEIDX_RAISEDERECT','GetGame().GetPlayer() != this','STATIC_LEFT_FRAME15_REFERENCE_COMPLETE'):assert needed in helper
for forbidden in ('AnimSet','SetPosition','Override','SetADS'):assert forbidden not in helper
keys=(B/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
assert keys.index('ML47UpdateLeftStandingReference(timeslice);')<keys.index('if (!m_MLADSPoseRecording ||')
assert 'm_ML47LeftReferenceStable < 0.5' in keys and 'm_ML47LeftReferenceWaiting = true' in keys
assert 'protected bool m_MLADSPoseRecording = false;' in keys
spec=json.loads((B/'Frame15-Standing-Left-Target.json').read_text())
assert spec['requested_blender_frame']==15 and spec['desired_native_capture']['index']==14
assert spec['desired_native_capture']['id']=='33626_true' and len(spec['desired_native_capture']['bones'])==114
assert spec['source_session']=='32901'
selection=json.loads((B/'BlenderTarget/Selection-Validation.json').read_text())
assert selection['source_blender_frame']==15 and selection['reopened_frozen_target_max_joint_error_m']<.00002
for p,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
assert 'Mosin-Lean-v47-Logs' in (B/'Collect-Logs.ps1').read_text()
print('PASS: frame15 exact native source index14; frozen .blend reopened; all114 joints verified; existing body/camera unchanged; left-only read-only collector; PBO hashes')
