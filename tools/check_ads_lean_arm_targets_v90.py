"""Verify arm-only same-side targets and source isolation; native IK untested."""
from pathlib import Path
import re,json
import numpy as np
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v87';b=base/'MovementLab_ADS_Lean_Mosin_v90'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(87|90)\]',r'[\g<1>VERSION]',s.replace('v87','vVERSION').replace('v90','vVERSION'))
for p in (a/'LogicSource').rglob('*'):
 if p.is_file():assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
for name,node in old.items():
 expected=node.replace('Child "ML67_CoherentLeanAim"','Child "ML90_ArmLoweringOnly"') if name=='MeleeBlockQ' else node
 assert new[name]==expected,name
added={name:block for name,block in new.items() if name not in old and not name.startswith('{')}
assert len(added)==8
assert not any(name.startswith(('ML88_','ML89_')) for name in new)
for side in ('Left','Right'):
 for prefix,amount in (('Target',-.05),('Restore',.05)):
  name='ML90_'+prefix+side+'Hand'+('Down' if prefix=='Target' else 'Source');node=new[name]
  assert 'Bone "'+side+'Hand"' in node
  assert 'Axis Y' in node and 'Op Translate' in node and 'Amount '+str(amount) in node
assert 'Child "ML90_TargetRightHandDown"' in new['ML90_CaptureLoweredHands']
assert 'Child "ML90_RestoreRightHandSource"' in new['ML90_SolveLoweredArms']
assert 'MLADSLeanGate*(1.0-ML87FirstPersonCrouchLean)' in new['ML90_ArmLoweringOnly']
agr=(b/'WorkspaceSource/player_main.agr').read_text()
for node in (new['ML90_CaptureLoweredHands'],new['ML90_SolveLoweredArms']):
 for chain in re.findall(r'IkChain "([^"]+)"',node):assert chain in agr
for field in ('WeightAim','WeightPrimaryChain','WeightSecondaryChain'):assert field+' "false"' in new['ML90_PublishLoweredHold']
# The temporary target translation is undone before the solve; targets are
# same-side and translated identically, preserving target grip/orientation.
data=json.loads((base/'MovementLab_ADS_Lean_Mosin_v55/Native-Head-Travel-v55.json').read_text())
for side in ('left','right'):
 pose=data['sides'][side]['desired'];t=np.eye(4);t[1,3]=-.05
 left=np.array(pose['LeftHand']);right=np.array(pose['RightHand'])
 np.testing.assert_allclose(np.linalg.inv(t@right)@(t@left),np.linalg.inv(right)@left,atol=1e-12)
 for arm in ('Left','Right'):
  root,elbow,hand=[np.array(pose[arm+x])[:3,3] for x in ('Arm','ForeArm','Hand')]
  lengths=(np.linalg.norm(elbow-root),np.linalg.norm(hand-elbow));dist=np.linalg.norm(hand+[0,-.05,0]-root)
  assert abs(lengths[0]-lengths[1])<dist<sum(lengths)
print('PASS: temporary hand offsets restore before same-side arm solve; 5cm targets preserve relative grip and are reachable in captured standing poses; original graph/scripts/body and first-person path retained. Native IK output unverified.')
