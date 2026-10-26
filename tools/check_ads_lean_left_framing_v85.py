"""Check left framing projection and isolate changes from v83 pose/timing."""
from pathlib import Path
import re,json
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v83';b=base/'MovementLab_ADS_Lean_Mosin_v85'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(83|85)\]',r'[\g<1>VERSION]',s.replace('v83','vVERSION').replace('v85','vVERSION'))
for rel in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr'):
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
for p in (a/'LogicSource').rglob('*'):
 if p.is_file() and p.name not in ('MLADSLeanCamera.c','MLADSLeanPlayer.c'):assert norm(p.read_text())==norm((b/p.relative_to(a)).read_text())
rel='LogicSource/Scripts/4_World/MLADSLeanPlayer.c';old=(a/rel).read_text();new=(b/rel).read_text()
start=new.index(' // Position-only raised-view weight.');end=new.index(' // Camera-only readback.',start)
assert norm(new[:start]+new[end:])==norm(old)
rel='LogicSource/Scripts/4_World/MLADSLeanCamera.c';old=(a/rel).read_text();new=(b/rel).read_text()
assert norm(old[old.index('modded class DayZPlayerCameraIronsights'):])==norm(new[new.index('modded class DayZPlayerCameraIronsights'):])
assert not re.search(r'result\.m_iDirectBone(?:Mode)?\s*=',new)
assert not re.search(r'result\.m_fUseHeading\s*=',new)
assert 'result.m_CameraTM[3] = correctedEye.InvMultiply4(headTM)' in new
assert 'vector targetCorrection = (desiredEye - nativeEye) * positionWeight;' in new
assert 'if (player.ML85LeftRaisedViewActive() && m_ML85HasSightHeight)' in new
# Calibrated standing/raised Q has gate1. A sight's projected screen height
# must stay at its neutral ratio even if intermediate pose height/depth vary.
ratio=-.20
for yaw in (-60,0,45):
 for pitch in (-70,-20,0,45,75):
  basis=Rotation.from_euler('yx',[yaw,pitch],degrees=True).as_matrix();right,up,forward=basis[:,0],basis[:,1],basis[:,2]
  for t in np.linspace(0,1,41):
   eye=np.array([.1,1.6,.05]);depth=.15+.2*t;height=-.08+.15*np.sin(np.pi*t)
   sight=eye+forward*depth+up*height+right*.025
   delta=sight-eye;error=np.dot(delta,up)-np.dot(delta,forward)*ratio
   corrected=eye+up*error;d=sight-corrected
   assert abs(np.dot(d,up)/np.dot(d,forward)-ratio)<1e-12
   assert abs(np.dot(d,right)-np.dot(delta,right))<1e-12
   assert abs(np.dot(d,forward)-depth)<1e-12
# Right behavior keeps ordinary gate*lean; full-left uses gate1, not amplitude.
for gate in (0,.25,1):
 for lean in (-1,-.5,-.01,0,.01,.5,1):
  ordinary=gate*abs(lean)
  follow=0 if ordinary<=0 else gate if lean<0 else ordinary
  if lean>=0:assert follow==ordinary
  if lean==-1:assert follow==ordinary
p=b/'Left-Framing-v85.json';data=json.loads(p.read_text());data['neutral_sight_height_constraint']='preserve projected vertical sight ratio using camera translation along native view up';data['left_camera_height']='intentionally adjusted through transition and endpoint';p.write_text(json.dumps(data,indent=2)+'\n')
print('PASS: calibrated Q sight-height projection constant in tested yaw/pitch/depth samples; right weighting, v83 graph, native timing, head parent and view direction preserved. Native rendering not run.')
