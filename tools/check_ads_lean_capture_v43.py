"""Regression checks for signed bone identifiers and read-only capture."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v42';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v43'
c=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
a=(A/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
# Every original runtime method remains byte-identical after removing diagnostics.
start=c.index(' // Read-only export helpers');end=c.index(' protected void MLADSLeanMeasureChain(',start)
oldstart=a.index(' // Read-only F9 snapshot');oldend=a.index(' protected void MLADSLeanMeasureChain(',oldstart)
assert (c[:start]+c[end:]).replace('MLADSLEAN43','MLADSLEAN42')==a[:oldstart]+a[oldend:]
export=c[start:end]
assert 'captureIndex <' not in export and 'captureIndex >' not in export and 'captureIndex ==' not in export
names=json.loads((B/'Pose-Snapshot.json').read_text())['parents']
for name in names:assert '"'+name+'"' in export
assert len(names)==114
for term in ('AnimSet','SetPosition','SetTransform','OverrideMovement','OverrideRaise'):assert term not in export
assert 'GetBoneTransformMS(captureIndex, boneTM)' in export
assert 'bones=" + capturedCount' in export
keys=(B/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
assert keys.count('override void OnUpdate(float timeslice)')==1
assert 'super.OnUpdate(timeslice);' in keys
assert 'm_MLADSPoseStable < 0.4' in keys
assert 'm_MLADSPoseLeftDone && m_MLADSPoseRightDone' in keys
assert 'm_MLADSPoseElapsed > 30' in keys
for f in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo'):assert (A/f).read_bytes()==(B/f).read_bytes()
for f,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():assert hashlib.sha256((B/f).read_bytes()).hexdigest()==h
print('PASS: 114 named bone queries without signed-ID rejection; pose runtime and workspace unchanged; auto-capture guards; PBO hashes')
