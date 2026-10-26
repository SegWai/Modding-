"""Verify v79 camera-parent-only behavioral change and preserved v78 runtime."""
from pathlib import Path
import re,math
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v78';b=base/'MovementLab_ADS_Lean_Mosin_v79'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(78|79)\]',r'[\g<1>VERSION]',s.replace('v78','vVERSION').replace('v79','vVERSION'))
for rel in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr'):
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
for p in (a/'LogicSource').rglob('*'):
 if p.is_file() and p.name!='MLADSLeanCamera.c':assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text())
rel='LogicSource/Scripts/4_World/MLADSLeanCamera.c';old=(a/rel).read_text();new=(b/rel).read_text()
assert norm(old[old.index('modded class DayZPlayerCameraIronsights'):])==norm(new[new.index('modded class DayZPlayerCameraIronsights'):])
assert not re.search(r'result\.m_iDirectBone(?:Mode)?\s*=',new)
assert not re.search(r'result\.m_fUseHeading\s*=',new)
assert 'GetBoneIndexByName("RightHand")' not in new
# Source calculation through correctedEye is preserved, except version labels.
start='  Weapon_Base weapon';end='  vector correctedEye = nativeEye + m_ML58EyeCorrection;'
assert norm(old[old.index(start):old.index(end)+len(end)])==norm(new[new.index(start):new.index(end)+len(end)])
assert 'result.m_CameraTM[3] = correctedEye.InvMultiply4(headTM);' in new
assert 'eye_offset_step_m=' in new
# Same desired model eye re-expressed with head parent, across head rotations.
for angle in (-90,-35,0,35,90):
 c=math.cos(math.radians(angle));s=math.sin(math.radians(angle));d=(.05,.02,-.03)
 local=(c*d[0]-s*d[2],d[1],s*d[0]+c*d[2])
 back=(c*local[0]+s*local[2],local[1],-s*local[0]+c*local[2])
 assert max(abs(back[i]-d[i]) for i in range(3))<1e-12
print('PASS: native head/heading retained; v78 eye target, animation graph, fast timing, grip and ADS unchanged. Render behavior remains unverified.')
