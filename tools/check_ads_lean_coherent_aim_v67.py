"""Common aim transform invariants on captured poses; not a native engine test."""
from pathlib import Path
import unittest,json,re,math
import numpy as np
from scipy.spatial.transform import Rotation
from dayz_graph_formats import newnodes
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v66';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v67'
class CoherentAim67(unittest.TestCase):
 def test_common_pitch_preserves_grip_limb_lengths_and_head_x_on_captured_poses(self):
  data=json.loads((R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v55/Native-Head-Travel-v55.json').read_text());parents=data['parents']
  def descendant(n):
   while n:
    if n=='Spine3':return True
    n=parents[n]
   return False
  affected={n for n in parents if descendant(n)}
  for n in ('LeftArm','LeftForeArm','LeftHand','RightHand','Head'):self.assertIn(n,affected)
  for side in ('left','right'):
   pose={n:np.array(m) for n,m in data['sides'][side]['desired'].items()};pivot=pose['Spine3'][:3,3]
   # A rifle's fixed attachment offset to the trigger wrist does not affect the
   # rigid-invariance proof. Use a nontrivial offset/rotation to exercise it.
   attachment=np.eye(4);attachment[:3,3]=[.03,.02,.05];attachment[:3,:3]=Rotation.from_euler('xyz',[.1,-.2,.05]).as_matrix();weapon=pose['RightHand']@attachment
   grip_before=np.linalg.inv(weapon)@pose['LeftHand']
   for degrees in (-85,-60,-30,0,30,60,85):
    delta=np.eye(4);delta[:3,:3]=Rotation.from_euler('x',-degrees,degrees=True).as_matrix();delta[:3,3]=pivot-delta[:3,:3]@pivot
    result={n:delta@m if n in affected else m.copy() for n,m in pose.items()};new_weapon=delta@weapon
    np.testing.assert_allclose(np.linalg.inv(new_weapon)@result['LeftHand'],grip_before,atol=1e-12)
    for n,p in parents.items():
     if p:self.assertAlmostEqual(np.linalg.norm(result[n][:3,3]-result[p][:3,3]),np.linalg.norm(pose[n][:3,3]-pose[p][:3,3]),places=10)
    for n in ('Pelvis','Spine','Spine1','Spine2','LeftFoot','RightFoot'):np.testing.assert_array_equal(result[n],pose[n])
    self.assertAlmostEqual(result['Head'][0,3],pose['Head'][0,3],places=12)
    if degrees==0:
     for n in pose:np.testing.assert_allclose(result[n],pose[n],atol=1e-12)
 def test_native_pitch_is_partitioned_once_and_same_for_both_sides(self):
  spec=json.loads((B/'Coherent-Aim-v67.json').read_text());new=newnodes((B/'WorkspaceSource/locomotion.agf').read_text());old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());changed=set(spec['native_nodes_masked'])
  for name,node in old.items():
   if name.startswith('{'):continue
   if name in changed:
    expected=re.sub(r'((?:ValueY|WeaponDirUd) ")([^"]*\bAimY\b[^"]*)(")',lambda m:m[1]+'('+m[2]+')*'+spec['native_pitch_mask']+m[3],node)
   elif name=='MeleeBlockQ':expected=node.replace('Child "ML51_StandingLeftElbowOnly"','Child "ML67_CoherentLeanAim"')
   else:expected=node
   self.assertEqual(new[name],expected,name)
  for lean in (-1,-.5,0,.5,1):
   for gate in (0,.3,1):
    l=min(1,max(0,abs(lean)*gate))
    for pitch in (-85,0,85):self.assertAlmostEqual(pitch*(1-l)+pitch*l,pitch)
  publisher=new['ML67_PublishAimedWeapon']
  for field in ('WeightAim','WeightPrimaryChain','WeightSecondaryChain'):self.assertIn(field+' "false"',publisher)
  self.assertIn('WeaponDirUd "0.0"',publisher)
  self.assertIn('Bone "Spine3"',new['ML67_SharedVerticalAim']);self.assertIn('Space Model',new['ML67_SharedVerticalAim'])
 def test_camera_approved_tilt_unchanged_and_no_grip_writers(self):
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text().replace('MLCAM67','MLCAM66');self.assertEqual(old,new)
  s=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();self.assertNotIn('ML60UpdateGrip',s);self.assertNotIn('ML60BindGrip',s)
  diag=s[s.index(' protected void ML67ReadAimCoherence'):s.index(' // Read-only camera weight,')];self.assertNotRegex(diag,r'AnimSet|SetPosition|SetTransform|SetOrientation|OverrideAim')
if __name__=='__main__':unittest.main()
