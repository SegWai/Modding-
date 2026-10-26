"""Check camera-only scope and transient eye-target isolation; no native playback."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test'
a=base/'MovementLab_ADS_Lean_Mosin_v76';b=base/'MovementLab_ADS_Lean_Mosin_v77'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(76|77)\]',r'[\g<1>VERSION]',s.replace('v76','vVERSION').replace('v77','vVERSION'))
for rel in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr'):
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
for p in (a/'LogicSource').rglob('*'):
 if p.is_file() and p.name!='MLADSLeanCamera.c':assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text())
rel='LogicSource/Scripts/4_World/MLADSLeanCamera.c';old=(a/rel).read_text();new=(b/rel).read_text()
assert norm(old[old.index('modded class DayZPlayerCameraIronsights'):])==norm(new[new.index('modded class DayZPlayerCameraIronsights'):])
assert 'm_ML58EyeCorrection = targetCorrection * readyWeight;' in new
assert 'm_ML58EyeCorrection = m_ML77HeldHeadCorrection.Multiply3(headTM) * readyWeight;' in new
assert not re.search(r'result\.m_fUseHeading\s*=',new)
# Exercise the same phase/filter policy: arbitrary rifle target while lowering
# must not change eye output, and no settled-view delay is introduced.
for fps in (30,60,144):
 dt=1/fps;phase=0;held=0
 def step(ready,target):
  global phase,held
  phase=min(1,phase+min(dt,.05)/.1) if ready else max(0,phase-min(dt,.05)/.1)
  if ready:held=target
  weight=phase*phase*(3-2*phase)
  return (target if ready else held)*weight
 for _ in range(20):assert step(False,1000)==0
 for _ in range(fps):value=step(True,.08)
 assert abs(value-.08)<1e-12
 assert abs(step(True,.045)-.045)<1e-12 # fully raised look remains synchronous
 output=step(False,1000)
 assert 0<=output<=.045
 previous=output
 for _ in range(fps):
  output=step(False,-1000)
  assert 0<=output<=previous+1e-12
  previous=output
 assert output==0
print('PASS: transient rifle target excluded; readiness envelope converges; full raised tracking immediate; graph, smoothing, grip, ADS unchanged. Native playback not run.')
