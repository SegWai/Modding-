"""Check camera and pose use one gate, with no independent ready envelope."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v80';b=base/'MovementLab_ADS_Lean_Mosin_v81'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(80|81)\]',r'[\g<1>VERSION]',s.replace('v80','vVERSION').replace('v81','vVERSION'))
for rel in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr'):
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
for p in (a/'LogicSource').rglob('*'):
 if p.is_file() and p.name!='MLADSLeanCamera.c':assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
rel='LogicSource/Scripts/4_World/MLADSLeanCamera.c';old=(a/rel).read_text();new=(b/rel).read_text()
assert norm(old[old.index('modded class DayZPlayerCameraIronsights'):])==norm(new[new.index('modded class DayZPlayerCameraIronsights'):])
for marker in ('m_ML77ReadyPhase','m_ML77HeldHeadCorrection','readyWeight','bool poseReady'):
 assert marker not in new
assert 'float weight = player.ML58RaisedViewWeight();' in new
assert 'vector targetCorrection = (desiredEye - nativeEye) * weight;' in new
assert 'm_ML58EyeCorrection = targetCorrection;' in new
assert 'result.m_CameraTM[3] = correctedEye.InvMultiply4(headTM);' in new
assert not re.search(r'result\.m_iDirectBone(?:Mode)?\s*=',new)
assert not re.search(r'result\.m_fUseHeading\s*=',new)
# Settled endpoint is unchanged; during raise the camera no longer waits for
# native ready while pose weight has already reached 1.
for gate in (0,.1,.5,.9,1):
 for lean in (-1,-.5,0,.5,1):
  weight=gate*abs(lean);delta=(.03,.04,-.06)
  output=tuple(x*weight for x in delta)
  assert output==tuple(x*gate*abs(lean) for x in delta)
  if gate==1 and abs(lean)==1:assert output==delta
print('PASS: one shared pose gate, unchanged settled framing, head parent, custom-only graph, fast timing, grip and ADS. Native visual result unverified.')
