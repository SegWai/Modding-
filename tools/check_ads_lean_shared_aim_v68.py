"""Combined aim and camera-frame invariants. Native playback remains unverified."""
from pathlib import Path
import unittest,json,re
import numpy as np
from scipy.spatial.transform import Rotation
from dayz_graph_formats import newnodes
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v67';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v68'
class SharedAim68(unittest.TestCase):
 def test_both_aim_axes_keep_hands_and_weapon_rigidly_related(self):
  data=json.loads((R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v55/Native-Head-Travel-v55.json').read_text())
  for side in ('left','right'):
   p={n:np.array(v) for n,v in data['sides'][side]['desired'].items()};pivot=p['Spine3'][:3,3]
   attachment=np.eye(4);attachment[:3,3]=[.02,-.03,.04];weapon=p['RightHand']@attachment;grip=np.linalg.inv(weapon)@p['LeftHand']
   for yaw in (-85,-30,0,30,85):
    for pitch in (-85,-30,0,30,85):
     d=np.eye(4);d[:3,:3]=Rotation.from_euler('y',yaw,degrees=True).as_matrix()@Rotation.from_euler('x',-pitch,degrees=True).as_matrix();d[:3,3]=pivot-d[:3,:3]@pivot
     np.testing.assert_allclose(np.linalg.inv(d@weapon)@(d@p['LeftHand']),grip,atol=1e-12)
     np.testing.assert_allclose(np.linalg.inv(d@p['RightHand'])@(d@p['LeftHand']),np.linalg.inv(p['RightHand'])@p['LeftHand'],atol=1e-12)
 def test_using_native_sight_basis_preserves_approved_camera_framing(self):
  rng=np.random.default_rng(68)
  def rigid():
   m=np.eye(4);m[:3,:3]=Rotation.random(random_state=rng).as_matrix();m[:3,3]=rng.normal(size=3);return m
  for i in range(100):
   w0,w1,sight,neutral_view=[rigid() for _ in range(4)]
   old=w1@np.linalg.inv(w0)@neutral_view
   new=(w1@sight)@np.linalg.inv(w0@sight)@neutral_view
   np.testing.assert_allclose(old,new,atol=1e-12)
 def test_sources_mask_yaw_and_keep_existing_authored_transform_amounts(self):
  old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((B/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((B/'Coherent-Aim-v68.json').read_text());changed=set(spec['horizontal_nodes_masked']);mask='(1.0-clamp(abs(MLADSLeanAmount)*MLADSLeanGate, 0.0, 1.0))'
  for name,node in old.items():
   if name.startswith('{'):continue
   expected=node
   if name in changed:expected=re.sub(r'((?:ValueX|WeaponDirLr) ")([^"]*\b(?:AimX|AimIKX)\b[^"]*)(")',lambda m:m[1]+'('+m[2]+')*'+mask+m[3],expected)
   if name=='ML67_PublishAimedWeapon':expected=re.sub(r'WeaponDirLr "[^"]+"','WeaponDirLr "0.0"',expected.replace('Child "ML67_SharedVerticalAim"','Child "ML68_SharedHorizontalAim"'))
   self.assertEqual(new[name],expected,name)
  yaw=new['ML68_SharedHorizontalAim'];self.assertIn('Bone "Spine3"',yaw);self.assertIn('Axis Y',yaw);self.assertIn('Amount -1',yaw)
  for field in ('Expression','ValueX','ValueY','WeaponDirLr','WeaponDirUd','BlendWeight'):
   for expression in re.findall(field+r' "([^"]*)"',(B/'WorkspaceSource/locomotion.agf').read_text()):self.assertEqual(expression.count('('),expression.count(')'))
 def test_raised_camera_reads_native_pose_and_ads_is_unchanged(self):
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();raised=new[new.index(' protected void ML58AlignRaisedView'):new.index('// Optics inherits')]
  self.assertIn('poseAccessor.WeaponGetCameraPointMSTransform',raised);self.assertNotIn('weapon.GetTransform(',raised);self.assertNotIn('player.GetTransform(',raised)
  marker='modded class DayZPlayerCameraIronsights';self.assertEqual(old[old.index(marker):],new[new.index(marker):])
  s=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();self.assertNotIn('ML60UpdateGrip',s);self.assertNotRegex(s,r'\]\s*\[')
if __name__=='__main__':unittest.main()
