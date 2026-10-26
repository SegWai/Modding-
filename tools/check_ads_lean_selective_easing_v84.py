"""State/trajectory tests for selective easing; native playback is separate."""
from pathlib import Path
import re,math
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v83';b=base/'MovementLab_ADS_Lean_Mosin_v84'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(83|84)\]',r'[\g<1>VERSION]',s.replace('v83','vVERSION').replace('v84','vVERSION'))
for rel in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr'):
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
for p in (a/'LogicSource').rglob('*'):
 if p.is_file() and p.name!='MLADSLeanPlayer.c':assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text())
s=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
for marker in ('m_MLADSLeanAmount = ML84EaseLeanEntryExit(pDt, m_MLADSLeanLeanRequested, leanIntent);','GetInputByID(UALeanLeft)','GetInputByID(UALeanRight)','float stepGate = Math.Clamp(pDt, 0, 0.05) / 0.08;','return nativeLean;','magnitude * magnitude * (3.0 - 2.0 * magnitude)'):
 assert marker in s
helper=s[s.index(' protected float ML84EaseLeanEntryExit'):s.index(' // Read-only camera weight,')]
assert not re.search(r'AnimSet|Override|SetPosition|SetTransform',helper)
# Literal policy port to test entry, exit, reversal and interrupted sequences.
class Policy:
 def __init__(self):self.last=0;self.target=0;self.switch=False;self.neutral=0
 def step(self,x,intent,dt=1/60):
  magnitude=abs(x)
  if intent:
   opposite=self.last!=0 and intent!=self.last
   if (opposite or x*intent<-.001) and magnitude>.001:self.switch=True;self.target=intent
   self.last=intent
  self.neutral=self.neutral+min(dt,.05) if magnitude<.001 and intent==0 else 0
  if self.neutral>=.12:self.last=0;self.switch=False
  if self.switch:
   if x*self.target>=.999:self.switch=False
   return x
  eased=magnitude*magnitude*(3-2*magnitude)
  return -eased if x<0 else eased
for sign in (-1,1):
 p=Policy()
 values=[i/20 for i in range(21)]
 entry=[p.step(sign*x,sign) for x in values]
 assert entry[0]==0 and entry[-1]==sign
 assert all(abs(x)<=abs(y) for x,y in zip(entry,entry[1:]))
 # Start a reversal while fully leaned, before native interpolation moves.
 assert p.step(sign,-sign)==sign
 for i in range(41):
  native=sign*(1-i/20)
  assert math.isclose(p.step(native,-sign),native,abs_tol=1e-12)
 # Reverse again immediately: no easing through either zero crossing.
 assert p.step(-sign,sign)==-sign
 for i in range(41):
  native=-sign*(1-i/20)
  assert math.isclose(p.step(native,sign),native,abs_tol=1e-12)
 # Exit to neutral is eased and finishes on the same sample as native.
 exitvals=[p.step(sign*x,0) for x in reversed(values)]
 assert exitvals[0]==sign and exitvals[-1]==0
 for _ in range(10):p.step(0,0)
 assert p.last==0 and not p.switch
 # Re-enter the opposite side after release: this is entry, not reversal.
 assert p.step(-sign*.25,-sign)==-sign*.15625
print('PASS: signed entry/exit endpoints and monotonicity, exact native bidirectional reversals, release/re-entry, no added duration; graph/camera untouched. Native API compilation and mapped input behavior unverified.')
