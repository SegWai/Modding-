"""Read-only standing-right calibration; preserve all approved animation code."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v43';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v44'
a=(A/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();b=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
x=a.index(' // Read-only export helpers');y=a.index(' // Read-only F9 snapshot',x)
u=b.index(' // Read-only calibration');v=b.index(' // Read-only F9 snapshot',u)
normalized=(b[:u]+b[v:]).replace('MLADSLEAN44','MLADSLEAN43').replace('MLPOSE44','MLPOSE43')
normalized=normalized.replace('  header += " gate=" + m_MLADSLeanGate;\n  header += " raised=" + IsRaised();\n','')
assert normalized==a[:x]+a[y:]
helpers=b[u:v]
for token in ('m_MLADSLeanAmount < 0.98','m_MLADSLeanMoveBlend > 0.02','m_MLADSLeanGate < 0.98','!IsRaised()','exportState.m_iMovement != 0','STANCEIDX_ERECT','STANCEIDX_RAISEDERECT','GetGame().GetPlayer() != this'):
 assert token in helpers
for token in ('AnimSet','SetPosition','SetTransform','Override'):assert token not in helpers
assert 'STATIC_RIGHT_REFERENCE_COMPLETE' in helpers
keys=(B/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
assert 'm_MLADSPoseStable < 0.5' in keys and 'm_MLADSPoseElapsed > 60' in keys
assert 'MLADSLeanExportStaticReference();' in keys
assert 'm_MLADSPoseDirection' not in keys
for f in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo'):
 assert (A/f).read_bytes()==(B/f).read_bytes()
target=json.loads((B/'Requested-Standing-Right-Pose.json').read_text())
assert target['desired_capture_id']=='67091_true' and len(target['desired_capture']['bones'])==114
for f,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():assert hashlib.sha256((B/f).read_bytes()).hexdigest()==h
assert 'F:\\DayZProjects' in (B/'Launch-Test.ps1').read_text()
print('PASS: native runtime and workspace unchanged; stationary raised anatomical-right-only capture gate; complete preserved target; PBO hashes')
