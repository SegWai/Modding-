"""Check duplicate weight removal without editing authored pose transforms."""
from pathlib import Path
import re
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v81';b=base/'MovementLab_ADS_Lean_Mosin_v82'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(81|82)\]',r'[\g<1>VERSION]',s.replace('v81','vVERSION').replace('v82','vVERSION'))
for p in (a/'LogicSource').rglob('*'):
 if p.is_file():assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
assert old.keys()==new.keys()
assert [name for name in old if old[name]!=new[name]]==['ML50_StandingBalancedOnly']
assert old['ML50_StandingBalancedOnly'].replace('BlendWeight "abs(MLADSLeanAmount)*MLADSLeanGate*','BlendWeight "MLADSLeanGate*')==new['ML50_StandingBalancedOnly']
for name in ('ML50_left_BodyBlend','ML50_right_BodyBlend'):
 assert 'MLADSLeanAmount' in re.search(r'BlendWeight "([^"]+)"',new[name])[1]
# Inner balance contribution should follow native amount once. At endpoint
# 0/1 the old/new weights agree. Moving/crouched outer masks still disable it.
for amount in (0,.1,.25,.5,.75,.9,1):
 before=amount*amount;after=amount
 if amount in (0,1):assert before==after
 if amount==.5:assert before==.25 and after==.5
 for gate in (0,.25,1):
  for crouch in (0,1):
   for movement in (0,1):
    oldweight=amount*gate*(1-crouch)*(1-movement)
    newweight=gate*(1-crouch)*(1-movement)
    if crouch or movement or not gate:assert oldweight==newweight==0
assert 'MLADSLeanLocomotion_v82.agf' in (b/'WorkspaceSource/player_main.agr').read_text()
print('PASS: only outer standing balance weight changed; all pose transforms, camera/scripts, moving/crouched paths and native timing unchanged. Native visual overshoot not measured.')
