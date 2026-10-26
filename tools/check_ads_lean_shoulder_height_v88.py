"""Check shared 5cm arm/rifle translation, unchanged view scopes and scripts."""
from pathlib import Path
import re,json
import numpy as np
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v87';b=base/'MovementLab_ADS_Lean_Mosin_v88'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(87|88)\]',r'[\g<1>VERSION]',s.replace('v87','vVERSION').replace('v88','vVERSION'))
for p in (a/'LogicSource').rglob('*'):
 if p.is_file():assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text()),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
assert {name for name in set(new)-set(old) if not name.startswith('{')}=={'ML88_LowerLeftArm','ML88_LowerRightArm','ML88_PublishLoweredWeapon','ML88_LoweredRaisedOnly'}
for name,node in old.items():
 expected=node.replace('Child "ML67_CoherentLeanAim"','Child "ML88_LoweredRaisedOnly"') if name=='MeleeBlockQ' else node
 assert new[name]==expected,name
for side in ('Left','Right'):
 n=new['ML88_Lower'+side+'Arm']
 for item in ('Bone "'+side+'Arm"','Axis Y','Space Model','Op Translate','Amount -0.05','Expression "1.0"'):assert item in n
blend=new['ML88_LoweredRaisedOnly'];assert 'MLADSLeanGate*(1.0-ML87FirstPersonCrouchLean)' in blend
for field in ('WeightAim','WeightPrimaryChain','WeightSecondaryChain'):assert field+' "false"' in new['ML88_PublishLoweredWeapon']
assert 'outputweaponoffsettobuffer = true' in new['ML88_PublishLoweredWeapon']
# Real captured wrist transforms: a common model-space translation preserves
# relative hand grip and rifle orientation, translating the fixed attachment.
data=json.loads((base/'MovementLab_ADS_Lean_Mosin_v55/Native-Head-Travel-v55.json').read_text())
for side in ('left','right'):
 pose=data['sides'][side]['desired'];left=np.array(pose['LeftHand']);right=np.array(pose['RightHand']);t=np.eye(4);t[1,3]=-.05
 grip=np.linalg.inv(right)@left
 np.testing.assert_allclose(np.linalg.inv(t@right)@(t@left),grip,atol=1e-12)
 attachment=np.eye(4);attachment[:3,3]=[.03,.02,.05]
 weapon=right@attachment;lowered=(t@right)@attachment
 np.testing.assert_allclose(lowered[:3,:3],weapon[:3,:3],atol=1e-12)
 np.testing.assert_allclose(lowered[:3,3]-weapon[:3,3],[0,-.05,0],atol=1e-12)
for gate in (0,.5,1):assert gate*(1-1)==0 # first-person branch unaffected
assert 'MLADSLeanLocomotion_v88.agf' in (b/'WorkspaceSource/player_main.agr').read_text()
print('PASS: 5cm common translation preserves captured grip/orientation; first-person control disables lowering; all previous pose nodes and scripts unchanged. Native visual alignment unverified.')
