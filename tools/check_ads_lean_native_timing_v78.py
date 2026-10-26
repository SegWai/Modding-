"""Verify v78 changes only visual transition timing, retaining camera/graph."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test'
a=base/'MovementLab_ADS_Lean_Mosin_v77';b=base/'MovementLab_ADS_Lean_Mosin_v78'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(77|78)\]',r'[\g<1>VERSION]',s.replace('v77','vVERSION').replace('v78','vVERSION'))
for rel in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr'):
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
for p in (a/'LogicSource').rglob('*'):
 if p.is_file() and p.name!='MLADSLeanPlayer.c':assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
rel='LogicSource/Scripts/4_World/MLADSLeanPlayer.c';old=(a/rel).read_text();new=(b/rel).read_text()
start=old.index('  // Shared low/raised visual lean;');end=old.index('  if (m_MLADSLeanBound && m_ML56LowSmoothVar',start)
newstart=new.index('  // Native movement state already interpolates');newend=new.index('  if (m_MLADSLeanBound && m_ML56LowSmoothVar',newstart)
expected=old[:start]+new[newstart:newend]+old[end:]
expected=expected.replace('float stepGate = Math.Clamp(pDt, 0, 0.05) / 0.36;','float stepGate = Math.Clamp(pDt, 0, 0.05) / 0.08;').replace('float moveVisualStep = Math.Clamp(pDt, 0, 0.05) / 0.20;','float moveVisualStep = Math.Clamp(pDt, 0, 0.05) / 0.08;')
assert norm(expected)==norm(new), 'Unexpected player changes'
assert 'm_MLADSLeanAmount = m_MLADSLeanLeanRequested;' in new
assert 'leanAlpha' not in new
# Check blend endpoints, monotonicity, and bounded behavior on mid-transition reversal.
for fps in (30,60,144):
 dt=1/fps;phase=0
 for target in (1,0,1,0):
  values=[]
  for _ in range(fps):
   step=min(dt,.05)/.08
   phase=min(target,phase+step) if phase<target else max(target,phase-step)
   value=phase*phase*(3-2*phase)
   assert 0<=value<=1
   values.append(value)
  assert phase==target
  assert all(x<=y for x,y in zip(values,values[1:])) if target==1 else all(x>=y for x,y in zip(values,values[1:]))
print('PASS: only native lean tracking and two short visual blends changed; camera, full graph, grip timing and other player logic unchanged. Native gameplay timing not measured.')
