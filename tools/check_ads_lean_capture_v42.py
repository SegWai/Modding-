"""Read-only native pose capture: ensure the approved runtime code is unchanged."""
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v41'
NEW=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v42'
p='LogicSource/Scripts/4_World/MLADSLeanPlayer.c'
a=(OLD/p).read_text();b=(NEW/p).read_text()
start=b.index(' // Read-only F9 snapshot');end=b.index(' protected void MLADSLeanMeasureChain(',start)
capture=b[start:end]
stripped=(b[:start]+b[end:]).replace('  MLADSLeanCapturePose();\n','').replace('MLADSLEAN42','MLADSLEAN41')
assert stripped==a, 'Runtime animation, controls and range must remain identical'
assert 'GetBoneTransformMS(captureIndex, boneTM)' in capture
for call in ('AnimSet','SetPosition','Override','SetOrientation','SetTransform','CallLater'):assert call not in capture
names=json.loads((OLD/'Pose-Snapshot.json').read_text())['parents']
for name in names:assert '"'+name+'"' in capture
assert 'GetTransform(actorTM)' in capture and 'capturedWeapon.GetTransform(weaponTM)' in capture
for file in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo'):
 assert (NEW/file).read_bytes()==(OLD/file).read_bytes()
for name,h in json.loads((NEW/'validation.json').read_text())['pbo_sha256'].items():
 assert hashlib.sha256((NEW/name).read_bytes()).hexdigest()==h
assert '[MLPOSE42] END' in capture
print('PASS: original runtime logic and workspace unchanged; complete bone list; read-only capture; both PBO hashes verified')
