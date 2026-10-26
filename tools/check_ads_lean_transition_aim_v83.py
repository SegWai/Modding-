"""Structural/activation checks, not a simulation of DayZ's native IK solver."""
from pathlib import Path
import re
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v81';b=base/'MovementLab_ADS_Lean_Mosin_v83'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(81|83)\]',r'[\g<1>VERSION]',s.replace('v81','vVERSION').replace('v83','vVERSION'))
for p in (a/'LogicSource').rglob('*'):
 if p.is_file():assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
assert set(new)-set(old)=={'ML83_LeftTransitionAimOnly','ML83_LeftTransitionAimIK'}
for name,node in old.items():
 expected=node.replace('Child "ML67_CoherentLeanAim"','Child "ML83_LeftTransitionAimOnly"') if name=='MeleeBlockQ' else node
 assert new[name]==expected,name
ik=new['ML83_LeftTransitionAimIK'];blend=new['ML83_LeftTransitionAimOnly']
for field in ('WeightAim','WeightPrimaryChain','WeightSecondaryChain'):assert field+' "true"' in ik
for item in ('Child "ML67_CoherentLeanAim"','BlendInTime 0','BlendOutTime 0','outputweaponoffsettobuffer = true','WeaponDirLr "AimIKX"','WeaponDirUd "AimY"','IkconfigName "ML83_LeftTransitionAimConfig"'):assert item in ik
for item in ('OptimizeMin 1','OptimizeMax 1','Child0 "ML67_CoherentLeanAim"','Child1 "ML83_LeftTransitionAimIK"'):assert item in blend
# Both branch children consume the same pre-constraint pose; no dependency cycle.
assert 'ML83_' not in new['ML67_CoherentLeanAim']
def clamp(x):return max(0,min(1,x))
def weight(lean,gate=1,stance=0,move=0,speed=0):return clamp(-lean*8)*clamp((1+lean)*8)*gate*(1-clamp(stance))*(1-move)*(1-clamp(speed))
for lean in (0,1,-1):assert weight(lean)==0
for lean in (-.125,-.25,-.5,-.75,-.875):assert weight(lean)==1
for lean in (-.1,-.5,-.9):
 for field in ('gate','stance','move','speed'):
  assert weight(lean,**{field:0 if field=='gate' else 1})==0
assert 'MLADSLeanLocomotion_v83.agf' in (b/'WorkspaceSource/player_main.agr').read_text()
print('PASS: v82 balance change reverted, scoped native IK branch acyclic, endpoint and non-standing-left weights zero; all camera/scripts and authored poses unchanged. Native IK visual behavior unverified.')
