"""Final pose ordering, direction and rigid arm-subtree translation regression checks."""
import sys,unittest,re,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
import captured_pose_bridge as pose
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v29';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v28';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class FinalHoldTests(unittest.TestCase):
 def test_final_order_has_no_later_weapon_solver(self):
  a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
  self.assertNotIn('ML24_MarkedShoulderOffset',b)
  self.assertIn('Child "AimObstructionT"',b['NormalWeaponIK'])
  self.assertIn('Child "NormalWeaponIK"',b['ML29_FinalRightChestHold'])
  self.assertIn('Child "ML29_FinalRightChestHold"',b['ML15_HeadForwardNod'])
  self.assertNotIn('outputweaponoffsettobuffer',b['NormalWeaponIK'])
  modified={n for n in a if n in b and not n.startswith('{') and a[n]!=b[n]}
  self.assertEqual(modified,{'NormalWeaponIK','ML15_HeadForwardNod'})
  for n in ['ML15_HeadForwardNod','ML20_RightLeanHeadExposure','ML21_RightMovingHeadLift','SickHotColdQ']:
   self.assertNotIn('AnimSrcNodeWeaponIk',b[n])
 def test_anatomical_left_only_and_15cm_right(self):
  node=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())['ML29_FinalRightChestHold']
  items=re.findall(r'Bone "([^"]+)"\s+Axis X\s+Space Model\s+Op Translate\s+Amount ([\d.]+)',node)
  self.assertEqual(dict((b,float(v)) for b,v in items),{'RightArm':.15,'LeftArm':.15})
  expr=re.search(r'Expression "([^"]+)"',node)[1]
  for amount,gate,speed,scale,want in [(-1,1,1,1,1),(1,1,1,1,0),(-1,1,0,1,0),(-1,0,1,1,0),(-1,1,1,0,0),(0,1,1,1,0),(-.5,1,1,1,.5)]:
   self.assertEqual(base.expression(expr,dict(MLADSLeanAmount=amount,MLADSLeanGate=gate,MovementSpeed=speed,MLADSLeanWeaponShift=scale,clamp=lambda x,a,b:max(a,min(b,x)))),want)
 def test_arm_hierarchy_rigid_shift_preserves_other_pose_bones(self):
  s=json.loads((KIT/'Pose-Snapshot.json').read_text());parents=s['parents'];ref=s['left']
  def shifted(b):
   while b:
    if b in ['RightArm','LeftArm']:return True
    b=parents[b]
   return False
  for w in [0,.5,1]:
   corrections={n:{'rotation_xyz':[0,0,0],'translation_xyz':[.15*w if n in ['RightArm','LeftArm'] else 0,0,0]} for n in parents}
   got=pose.reconstruct(ref,parents,corrections)
   for n in ref:
    for i in range(4):
     for j in range(4):
      expected=ref[n][i][j]+(.15*w if shifted(n) and i==0 and j==3 else 0)
      self.assertAlmostEqual(got[n][i][j],expected,delta=1e-5,msg=n)
 def test_range_and_shared_controller_preserved(self):
  for p in ['LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual((OLD/p).read_text().replace('MLADSLEAN28','MLADSLEAN29').replace('lean v28','lean v29'),(KIT/p).read_text())
  p='LogicSource/Scripts/4_World/MLADSLeanPlayer.c'
  a=(OLD/p).read_text().replace('MLADSLEAN28','MLADSLEAN29').replace('// F5 comparison affects the same pre-weapon-IK pose on both actors.','// F5 comparison affects the final solved arm pose on both actors.')
  self.assertEqual(a,(KIT/p).read_text())
 def test_packaged_graph_integrity_and_direct_launcher(self):
  _,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes())
  self.assertEqual(entries['MLADSLeanLocomotion_v29.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertIn(b'MLADSLeanLocomotion_v29.agf',entries['player_main.agr'])
  self.assertNotIn('locomotion.agf',entries)
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
  self.assertIn('Mosin-Lean-v29-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests);suite.addTests(loader.loadTestsFromTestCase(FinalHoldTests));return suite
if __name__=='__main__':unittest.main()
