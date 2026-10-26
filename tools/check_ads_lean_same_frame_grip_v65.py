"""Graph and rigid-transform tests; native cross-hand IK target still unverified."""
from pathlib import Path
import unittest,re
import numpy as np
from scipy.spatial.transform import Rotation
from dayz_graph_formats import newnodes
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v64';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v65'
class SameFrame65(unittest.TestCase):
 def test_current_frame_target_and_primary_restoration(self):
  rng=np.random.default_rng(65)
  for trial in range(100):
   primary=np.eye(4);primary[:3,:3]=Rotation.random(random_state=rng).as_matrix();primary[:3,3]=rng.normal(size=3)
   yaw,pitch,roll=rng.uniform(-1.4,1.4,3);offset=rng.uniform(-.3,.3,3)
   relative=np.eye(4);relative[:3,:3]=Rotation.from_euler('YXZ',[yaw,pitch,roll]).as_matrix();relative[:3,3]=offset
   target=primary.copy()
   target[:3,3]+=target[:3,:3]@offset
   for axis,angle in zip('yxz',[yaw,pitch,roll]):target[:3,:3]=target[:3,:3]@Rotation.from_euler(axis,angle).as_matrix()
   np.testing.assert_allclose(target,primary@relative,atol=1e-12)
   restored=target.copy()
   for axis,angle in zip('zxy',[-roll,-pitch,-yaw]):restored[:3,:3]=restored[:3,:3]@Rotation.from_euler(axis,angle).as_matrix()
   restored[:3,3]-=restored[:3,:3]@offset
   np.testing.assert_allclose(restored,primary,atol=1e-12)
   np.testing.assert_allclose(np.linalg.inv(primary)@target,relative,atol=1e-12)
 def test_proxy_sequence_and_registered_native_chains(self):
  n=newnodes((B/'WorkspaceSource/locomotion.agf').read_text());agr=(B/'WorkspaceSource/player_main.agr').read_text();child='ML51_StandingLeftElbowOnly'
  for label,ops,sign in [('Proxy',[('Translate','XYZ'),('Rotate','YXZ')],1),('Restore',[('Rotate','ZXY'),('Translate','ZYX')],-1)]:
   if label=='Restore':
    self.assertIn(f'Child "{child}"',n['ML65_CaptureSupportProxy']);child='ML65_CaptureSupportProxy'
   for op,axes in ops:
    for axis in axes:
     name=f'ML65_{label}_{op}_{axis}';node=n[name];self.assertIn(f'Child "{child}"',node);self.assertIn('Bone "RightHand"',node);self.assertIn('Space Local',node);self.assertIn(f'Amount {sign}',node);child=name
  self.assertIn(f'Child "{child}"',n['ML65_SolveSupportArm'])
  self.assertIn('IkTarget "LHandIKTarget"',n['ML65_CaptureSupportProxy'])
  for name in ['ML65_CaptureSupportProxy','ML65_SolveSupportArm']:
   chain=re.search(r'IkChain "([^"]+)"',n[name])[1];self.assertIn('}'+chain+'"',agr)
  self.assertIn('Child "ML65_SupportGripOnly"',n['MeleeBlockQ'])
 def test_no_per_frame_feedback_and_camera_preserved(self):
  s=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();body=s[s.index(' protected void ML60UpdateGrip'):s.index(' // Read-only camera weight,')]
  self.assertNotRegex(body,r'wantedShift|wantedRotation|QuatLerp|m_ML60GripShift|errorM\s*\*|\]\s*\[')
  self.assertIn('fixed_primary_local_grip=',body);self.assertIn('!m_ML60GripReference',body)
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text().replace('MLCAM65','MLCAM64');self.assertEqual(old,new)
  a=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((B/'WorkspaceSource/locomotion.agf').read_text())
  for name in a:
   if name.startswith('{') or name=='MeleeBlockQ':continue
   self.assertEqual(a[name],b[name],name)
if __name__=='__main__':unittest.main()
