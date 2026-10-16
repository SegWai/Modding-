"""Verify one shared shoulder correction covers idle and turn, outside gait paths."""
from pathlib import Path
import re
from dayz_graph_formats import newnodes,end
r=Path(__file__).resolve().parents[1];old=r/'hud-icons-test/MovementLabLocomotion_v75';new=r/'hud-icons-test/MovementLabLocomotion_v76'
a=(old/'WorkspacePatches/locomotion.agf').read_text();b=(new/'WorkspacePatches/locomotion.agf').read_text();before=newnodes(a);after=newnodes(b)
assert end(b,0)==len(b.rstrip())
changed={n for n in before.keys()&after.keys() if before[n]!=after[n]}
assert changed=={'IdleLookLowBlendT','IdleStateMachine','ErcTurnLookBlendT'},changed
assert set(before)-set(after)=={'MovementLabIdleLookUncorrected'}
assert set(after)-set(before)=={'MovementLabIdleTurnUncorrected'}
assert b.count('Expression "MovementLabIdleShoulderYaw"')==1
assert 'Child "MovementLabIdleTurnUncorrected"' in after['IdleStateMachine']
assert after['IdleStateMachine'].startswith('AnimSrcNodeProcTransform')
assert 'Condition "(Look || MovementLabStationaryHeadOnly > 0.001) && !Raised"' in after['ErcTurnLookBlendT']
# The state machine keeps all original clips, sync lines and transition timing.
assert before['IdleStateMachine'].replace('AnimSrcNodeStateMachine IdleStateMachine {','AnimSrcNodeStateMachine "MovementLabIdleTurnUncorrected" {',1)==after['MovementLabIdleTurnUncorrected']
def deps(n,seen=None):
 seen=set() if seen is None else seen
 if n in seen:return seen
 seen.add(n)
 block=after[n]
 children=re.findall(r'\b(?:Child|Child0|Child1)\s+"([^"\n]+)"',block)
 children += [c for m in re.finditer(r'\bChildren\s*\{([^}]+)',block) for c in re.findall(r'"([^"]+)"',m[1])]
 for c in children:
  c=re.sub(r'^\{[^}]+\}','',c)
  if c in after:deps(c,seen)
 return seen
stationary=deps('IdleStateMachine')
assert {'IdleLookLowBlendT','ErcTurnLookBlendT','ErcTurnNBlend','TurnStanceSTM'}<=stationary
for root in ['ErcMoveLowG','CroMoveLowG']:
 gait=deps(root)
 assert 'IdleStateMachine' not in gait
 assert 'MovementLabIdleTurnUncorrected' not in gait
# No source/controller/camera change accompanies the graph routing fix.
for f in (old/'StartGateSource').rglob('*'):
 if f.is_file():assert f.read_bytes()==(new/'StartGateSource'/f.relative_to(old/'StartGateSource')).read_bytes(),f
for f in (old/'Missions').rglob('*'):
 if f.is_file():assert f.read_bytes()==(new/'Missions'/f.relative_to(old/'Missions')).read_bytes(),f
for f in (old/'WorkspacePatches').rglob('*'):
 if f.is_file() and f.name!='locomotion.agf':assert f.read_bytes()==(new/'WorkspacePatches'/f.relative_to(old/'WorkspacePatches')).read_bytes(),f
print('PASS: one shoulder correction after shared idle/turn blend; continuous upright turn head pose; native turn transitions/clips retained; gait branches exclude correction; camera/input/pose source and other workspace files unchanged. Native playback pending.')
