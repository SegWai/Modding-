"""Source isolation and position reconstruction checks; not a native camera test."""
from pathlib import Path
import re, math
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'ads-lean-test'
old=base/'MovementLab_ADS_Lean_Mosin_v71'
new=base/'MovementLab_ADS_Lean_Mosin_v75'
def normalize(s):
 return re.sub(r'\[(ML[A-Z]+)(71|75)\]',r'[\g<1>VERSION]',s.replace('v71','vVERSION').replace('v75','vVERSION'))
for rel in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr'):
 assert (old/rel).read_bytes()==(new/rel).read_bytes(),rel
for p in (old/'LogicSource').rglob('*'):
 if not p.is_file() or p.name=='MLADSLeanCamera.c':continue
 assert normalize(p.read_text())==normalize((new/p.relative_to(old)).read_text()),p
rel='LogicSource/Scripts/4_World/MLADSLeanCamera.c'
a=(old/rel).read_text();b=(new/rel).read_text()
assert normalize(a[a.index('modded class DayZPlayerCameraIronsights'):])==normalize(b[b.index('modded class DayZPlayerCameraIronsights'):])
assert 'result.m_iDirectBoneMode = 1;' in b
assert 'result.m_iDirectBoneMode = 3;' not in b
assert not re.search(r'result\.m_fUseHeading\s*=',b)
alignment=b[b.index('protected void ML58AlignRaisedView'):b.index(' override void OnUpdate')]
assert not re.search(r'result\.m_CameraTM\[(?:0|1|2|outAxis|modelAxis)\]\s*=',alignment)
assert 'result.m_CameraTM[3] = correctedEye.InvMultiply4(primaryPose);' in b
assert 'result.m_bUpdateEveryFrame = false;' in b
# Eye offset reconstructs for arbitrary wrist poses; view basis is untouched.
# Native mode 1 applies bone parenting to position, not camera direction.
for degrees in (-170,-90,-25,0,45,90,175):
 t=math.radians(degrees);c=math.cos(t);s=math.sin(t)
 eye=(.2,1.7,.35);origin=(-.1,1.4,.2)
 dx,dy,dz=(eye[i]-origin[i] for i in range(3))
 local=(c*dx-s*dz,dy,s*dx+c*dz)
 reconstructed=(c*local[0]+s*local[2]+origin[0],local[1]+origin[1],-s*local[0]+c*local[2]+origin[2])
 assert max(abs(reconstructed[i]-eye[i]) for i in range(3))<1e-12
print('PASS: v71 pose graph, smoothing/grip logic and ADS code unchanged; native raised basis/heading preserved; eye offset reconstructs. Native gameplay not tested.')
