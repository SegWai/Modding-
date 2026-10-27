"""Offline head correction algebra and release isolation; no native runtime claim."""
from pathlib import Path
import hashlib,sys,re
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent))
from dayz_graph_formats import newnodes
root=Path(__file__).resolve().parents[1]/'ads-lean-test'
a=root/'MovementLab_ADS_Lean_Mosin_v156';b=root/'MovementLab_ADS_Lean_Mosin_v157'
for p in ['MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','LogicSource/Scripts/4_World/MLADSLeanCamera.c','LogicSource/Scripts/4_World/MLVanillaLoadout156.c']:
 assert (a/p).read_bytes()==(b/p).read_bytes(),p
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
assert {n for n in set(new)-set(old) if not n.startswith('{')}=={'ML157_HeadX','ML157_HeadY','ML157_HeadZ'}
for name,node in old.items():
 expected=node.replace('Child "ML149_BodyWithWeapon"','Child "ML157_HeadZ"') if name=='MeleeBlockQ' else node
 assert new[name]==expected,name
for axis in 'XYZ':
 n=new['ML157_Head'+axis]
 assert 'Bone "Head"' in n and 'Space Model' in n and 'Op Rotate' in n
rng=np.random.default_rng(157)
for _ in range(1000):
 source=Rotation.random(random_state=rng).as_matrix();target=Rotation.random(random_state=rng).as_matrix()
 delta=target@source.T
 ay=np.arcsin(np.clip(-delta[2,0],-1,1))
 ax=np.arctan2(delta[2,1],delta[2,2]);az=np.arctan2(delta[1,0],delta[0,0])
 # AppendNative negates RHS angles; native model Rotate negates these again.
 reconstructed=Rotation.from_euler('xyz',[ax,ay,az]).as_matrix()
 assert np.max(np.abs(reconstructed@source-target))<1e-10
s=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
assert '!m_ML157Ready[keyHead]' in s and 'm_ML157Settled > 0.3' in s
assert 'ML69AimCentered()' in s and 'm_ML87ViewAmount < 0.01' in s
assert hashlib.sha256((b/'MLLeanPreset.json').read_bytes()).hexdigest()=='deeaeac1af612bfe4edaa542e6ebabf6da992b163bd7eac56579a0dd4f0bdb61'
print('PASS: 1000 orientation matches, head-only graph isolation, exact preset/camera/loadout preservation. Native runtime not tested.')
