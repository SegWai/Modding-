"""Rotational reference hold: preserve grip, bone lengths and body; verify packed graph."""
import sys,unittest,json,hashlib,re,math
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
import captured_pose_bridge as pose
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v32';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v31';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class ReferenceHoldTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=json.loads((KIT/'Reference-Hold-v32.json').read_text());cls.n=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
 def test_two_hands_move_together_and_retain_grip_orientation(self):
  d=self.d
  for hand in ['RightHand','LeftHand']:
   for i in range(3):
    self.assertAlmostEqual(d['desired'][hand][i][3]-d['base'][hand][i][3],d['authoring_shift_metres'][i],places=8)
    for j in range(3):self.assertAlmostEqual(d['desired'][hand][i][j],d['base'][hand][i][j],places=8)
  before=pose.multiply(pose.inverse(d['base']['RightHand']),d['base']['LeftHand']);after=pose.multiply(pose.inverse(d['desired']['RightHand']),d['desired']['LeftHand'])
  self.assertLess(max(abs(before[i][j]-after[i][j]) for i in range(4) for j in range(4)),1e-8)
 def test_additional_hand_target_travel_is15cm_without_height_change(self):
  previous=json.loads((OLD/'Reference-Hold-v31.json').read_text())
  for hand in ['RightHand','LeftHand']:
   for i,delta in enumerate([.15,0,0]):
    self.assertAlmostEqual(self.d['desired'][hand][i][3]-previous['desired'][hand][i][3],delta,places=8)
 def test_rotation_only_reconstruction_preserves_lengths_and_non_arm_pose(self):
  d=self.d;parents=d['parents'];c={n:{'rotation_xyz':d['rotation_corrections'].get(n,[0,0,0]),'translation_xyz':[0,0,0]} for n in parents}
  got=pose.reconstruct(d['base'],parents,c)
  for n,p in parents.items():
   for i in range(4):
    for j in range(4):self.assertAlmostEqual(got[n][i][j],d['desired'][n][i][j],delta=1e-8,msg=n)
   if p:
    a=math.dist([d['base'][n][i][3] for i in range(3)],[d['base'][p][i][3] for i in range(3)])
    b=math.dist([got[n][i][3] for i in range(3)],[got[p][i][3] for i in range(3)])
    self.assertAlmostEqual(a,b,delta=1e-8,msg=n)
  for n in ['Pelvis','Spine','Spine1','Spine2','Spine3','Neck','Neck1','Head','RightShoulder','LeftFoot','RightFoot']:
   self.assertEqual(d['base'][n],d['desired'][n],n)
 def test_final_graph_matches_rotation_corrections_and_no_translations(self):
  d=self.d;nodes=self.n;old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());self.assertNotIn('ML29_FinalRightChestHold',nodes)
  actual=[n for n in nodes if n.startswith('ML32_ReferenceHold_')];self.assertEqual(len(actual),21)
  child='NormalWeaponIK'
  for bone in pose.ordered(d['parents']):
   if bone not in d['rotation_corrections']:continue
   for axis,value in zip('XYZ',d['rotation_corrections'][bone]):
    name=f'ML32_ReferenceHold_{bone}_{axis}';b=nodes[name]
    self.assertIn(f'Child "{child}"',b);self.assertIn('Op Rotate',b);self.assertNotIn('Op Translate',b)
    self.assertAlmostEqual(float(re.search(r'Amount ([-\d.eE]+)',b)[1]),-value,places=10)
    self.assertIn('clamp(-MLADSLeanAmount, 0.0, 1.0)*MLADSLeanGate*clamp(MovementSpeed, 0.0, 1.0)*MLADSLeanWeaponShift',b)
    child=name
  self.assertIn(f'Child "{child}"',nodes['ML15_HeadForwardNod'])
  changed={n for n in old if n in nodes and not n.startswith('{') and old[n]!=nodes[n]}
  self.assertEqual(changed,{'ML15_HeadForwardNod'})
 def test_shared_controller_range_and_gun_cant_preserved(self):
  for p in list((OLD/'LogicSource/Scripts/4_World').glob('*.c'))+[OLD/'Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual(p.read_text().replace('MLADSLEAN31','MLADSLEAN32').replace('lean v31','lean v32'),(KIT/p.relative_to(OLD)).read_text())
  self.assertIn('WeaponRoll "8.0*MLADSLeanAmount*MLADSLeanGate"',self.n['NormalWeaponIK'])
 def test_packaged_graph_and_checksum_integrity(self):
  _,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes())
  self.assertEqual(entries['MLADSLeanLocomotion_v32.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertIn(b'MLADSLeanLocomotion_v32.agf',entries['player_main.agr'])
  self.assertNotIn('locomotion.agf',entries)
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('Mosin-Lean-v32-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests);suite.addTests(loader.loadTestsFromTestCase(ReferenceHoldTests));return suite
if __name__=='__main__':unittest.main()
