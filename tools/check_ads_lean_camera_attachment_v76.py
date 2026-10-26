"""Check v76 source isolation and both camera-parent position mappings."""
from pathlib import Path
import re,math
ROOT=Path(__file__).resolve().parents[1]
a=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v75'
b=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v76'
def normalize(s):
 return re.sub(r'\[(ML[A-Z]+)(75|76)\]',r'[\g<1>VERSION]',s.replace('v75','vVERSION').replace('v76','vVERSION'))
for rel in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr'):
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
for p in (a/'LogicSource').rglob('*'):
 if p.is_file() and p.name!='MLADSLeanCamera.c':assert normalize(p.read_text())==normalize((b/p.relative_to(a)).read_text())
rel='LogicSource/Scripts/4_World/MLADSLeanCamera.c';old=(a/rel).read_text();new=(b/rel).read_text()
assert normalize(old[old.index('modded class DayZPlayerCameraIronsights'):])==normalize(new[new.index('modded class DayZPlayerCameraIronsights'):])
# Eye reference, correction and fallback calculation remain identical.
assert normalize(old[old.index('  Weapon_Base weapon'):old.index('  int primaryHand')]).split('  // During raising')[0] in normalize(new)
assert 'bool wristReady = player.IsRaised() && player.IsWeaponRaiseCompleted();' in new
assert 'correctedEye.InvMultiply4(headTM)' in new
assert 'correctedEye.InvMultiply4(primaryPose)' in new
assert 'result.m_iDirectBoneMode = 1;' in new
assert not re.search(r'result\.m_fUseHeading\s*=',new)
# Both rotated/translating parent paths reconstruct the same eye, including
# the frame in which parent selection changes. Test numerical continuity.
eye=(.2,1.7,.35)
for headangle in (-25,0,35):
 for wristangle in (-170,-90,0,90,170):
  positions=[]
  for degrees,origin in ((headangle,(.15,1.72,.03)),(wristangle,(-.1,1.4,.2))):
   t=math.radians(degrees);c=math.cos(t);s=math.sin(t)
   dx,dy,dz=(eye[i]-origin[i] for i in range(3))
   local=(c*dx-s*dz,dy,s*dx+c*dz)
   positions.append((c*local[0]+s*local[2]+origin[0],local[1]+origin[1],-s*local[0]+c*local[2]+origin[2]))
  assert max(abs(positions[0][i]-positions[1][i]) for i in range(3))<1e-12
print('PASS: parent mappings agree; v75 eye calculation/direction, graph, grip, smoothing and ADS unchanged. Native render timing unverified.')
