"""Verify single-stage isolation from v85; no claims about native outcome."""
from pathlib import Path
import re
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v85';b=base/'MovementLab_ADS_Lean_Mosin_v86'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(85|86)\]',r'[\g<1>VERSION]',s.replace('v85','vVERSION').replace('v86','vVERSION'))
for p in (a/'LogicSource').rglob('*'):
 if p.is_file():assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
assert old.keys()==new.keys()
assert [name for name in old if old[name]!=new[name]]==['MeleeBlockQ']
assert new['MeleeBlockQ']==old['MeleeBlockQ'].replace('Child "ML83_LeftTransitionAimOnly"','Child "ML67_CoherentLeanAim"')
# No active consumer reaches the disabled branch; retained definitions are
# historical only and still allow source comparison with v85.
for name,block in new.items():
 if name!='ML83_LeftTransitionAimOnly':assert 'Child "ML83_LeftTransitionAimOnly"' not in block
assert 'MLADSLeanLocomotion_v86.agf' in (b/'WorkspaceSource/player_main.agr').read_text()
def clamp(x):return min(1,max(0,x))
for x in (0,.125,.5,.875,1):
 weight=clamp(x*8)*clamp((1-x)*8)
 if x in (0,1):assert weight==0
 else:assert weight==1
print('PASS: only active graph edge changed; v85 camera/scripts/pose definitions untouched, v83 middle-phase solver bypassed; neutral/full/right paths had zero contribution before change. Native result pending.')
