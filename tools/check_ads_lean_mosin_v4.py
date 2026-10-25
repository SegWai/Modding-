"""Offline checks for the asymmetric left-lean elbow/leg revision."""
import unittest,json,math,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
from dayz_graph_formats import newnodes
from captured_pose_bridge import multiply,inverse
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v3';NEW=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v4'
def data(path,name):return json.loads((path/name).read_text())
def point(m):return [m[i][3] for i in range(3)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def length(v):return math.sqrt(sum(x*x for x in v))
def angle(a,b):return math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(a,b))/length(a)/length(b)))))
class LeftLeanRevision(unittest.TestCase):
 def test_other_direction_and_reference_unchanged(self):
  a=data(OLD,'Pose-Snapshot.json');b=data(NEW,'Pose-Snapshot.json')
  for key in ['right','reference','parents']:self.assertEqual(a[key],b[key],key)
  self.assertEqual(data(OLD,'Pose-Spec.json')['corrections']['right'],data(NEW,'Pose-Spec.json')['corrections']['right'])
 def test_right_elbow_is_lower_and_hand_grip_preserved(self):
  a=data(OLD,'Pose-Snapshot.json')['left'];b=data(NEW,'Pose-Snapshot.json')['left']
  sh=point(b['RightArm']);el=point(b['RightForeArm'])
  self.assertAlmostEqual(angle(sub(el,sh),[0,-1,0]),90,places=3)
  self.assertLess(el[1],point(a['RightForeArm'])[1]-.09)
  for name in ['RightHand','LeftHand']:
   delta=sub(point(b[name]),point(a[name]));self.assertLess(length(sub(delta,[0,-.04,0])),1e-5)
   self.assertLess(max(abs(b[name][i][j]-a[name][i][j]) for i in range(3) for j in range(3)),1e-5)
 def test_right_leg_more_extended_with_planted_foot(self):
  a=data(OLD,'Pose-Snapshot.json')['left'];b=data(NEW,'Pose-Snapshot.json')['left']
  knees=[]
  for pose in [a,b]:
   h,k,f=[point(pose[n]) for n in ['RightUpLeg','RightLeg','RightFoot']];knees.append(angle(sub(h,k),sub(f,k)))
  self.assertGreater(knees[1],knees[0]+9)
  self.assertGreater(point(b['RightFoot'])[0],point(a['RightFoot'])[0]+.08)
  self.assertAlmostEqual(point(b['RightFoot'])[1],point(a['RightFoot'])[1],places=5)
  for lr in ['Left','Right']:
   for n1,n2 in [(lr+'UpLeg',lr+'Leg'),(lr+'Leg',lr+'Foot')]:
    self.assertAlmostEqual(length(sub(point(a[n1]),point(a[n2]))),length(sub(point(b[n1]),point(b[n2]))),places=4)
 def test_foot_turns_out_without_changing_support_foot_rotation(self):
  a=data(OLD,'Pose-Snapshot.json')['left'];b=data(NEW,'Pose-Snapshot.json')['left']
  d=multiply(b['RightFoot'],inverse(a['RightFoot']));rotation_angle=math.degrees(math.acos(max(-1,min(1,(sum(d[i][i] for i in range(3))-1)/2))))
  self.assertAlmostEqual(rotation_angle,55,places=2)
  self.assertLess(max(abs(b['LeftFoot'][i][j]-a['LeftFoot'][i][j]) for i in range(3) for j in range(3)),1e-5)
 def test_control_foot_ik_and_right_branch_unchanged(self):
  self.assertEqual((OLD/'WorkspaceSource/player_main.agr').read_bytes(),(NEW/'WorkspaceSource/player_main.agr').read_bytes())
  a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((NEW/'WorkspaceSource/locomotion.agf').read_text())
  self.assertEqual(set(a),set(b))
  for name in a:
   if name.startswith('MLADSLean_right_') or name in ['MLADSLeanFootIKBlend','IdleRasIK','StanceMaster']:self.assertEqual(a[name],b[name],name)
 def test_activation_logic_unchanged_and_joint_readback_has_no_writes(self):
  a=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();b=(NEW/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  prefix=b.split(' // Read-only measurements')[0]+'};\n'
  self.assertEqual(a,prefix.replace('MLADSLEAN4','MLADSLEAN3'))
  readback=b.split(' // Read-only measurements')[1]
  self.assertIn('GetBonePositionMS',readback);self.assertNotIn('AnimSet',readback);self.assertNotIn('SetPosition',readback)
if __name__=='__main__':unittest.main()
