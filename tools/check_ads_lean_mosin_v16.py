"""Reverse only the four shared left-lean Head Z corrections."""
import sys,unittest,re,json,math,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v15 as previous
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v16'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v15'
base.KIT=KIT
previous.KIT=KIT
class LeftHeadDirectionTests(unittest.TestCase):
 def test_only_four_existing_head_nodes_change(self):
  a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text())
  b=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
  self.assertEqual(set(a),set(b))
  expected={f'ML5_{mode}_left_Head_Rotate_Z' for mode in ['StandIdle','StandWalk','CrouchIdle','CrouchWalk']}
  changed={name for name in a if not name.startswith('{') and a[name]!=b[name]}
  self.assertEqual(changed,expected)
  for name in expected:
   before=float(re.search(r'Amount ([-+0-9.eE]+)',a[name])[1]);after=float(re.search(r'Amount ([-+0-9.eE]+)',b[name])[1])
   self.assertGreater(before,0);self.assertLess(after,0);self.assertEqual(after,-before)
   self.assertAlmostEqual(math.degrees(after-before),-26,delta=.001)
   self.assertEqual(re.findall(r'Bone "([^"]+)"',b[name]),['Head'])
   self.assertIn('Axis Z',b[name]);self.assertIn('Space Model',b[name])
   self.assertEqual(a[name].replace('Amount '+str(before),'Amount '+str(after)),b[name])
 def test_left_branch_active_only_for_left_custom_lean(self):
  n=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
  for mode in ['StandIdle','StandWalk','CrouchIdle','CrouchWalk']:
   node=n[f'ML5_{mode}_left_Head_Rotate_Z']
   expr=re.search(r'Expression "([^"]+)"',node)[1]
   for lean,gate,wanted in [(-1,1,1),(-.5,1,.5),(1,1,0),(0,1,0),(-1,0,0)]:
    result=base.expression(expr,{'MLADSLeanAmount':lean,'MLADSLeanGate':gate,'clamp':lambda x,a,b:max(a,min(b,x))})
    self.assertEqual(result,wanted)
   self.assertNotIn('MLADSLeanCanary',expr) # shared actor-independent pose weight
 def test_controller_controls_and_pose_metadata_preserved(self):
  for name in ['WorkspaceSource/player_main.agr','Static-Pose-Snapshot.json','Mode-Coverage.json','Pose-Snapshot.json']:
   self.assertEqual((KIT/name).read_bytes(),(OLD/name).read_bytes())
  for path in ['LogicSource/Scripts/4_World/MLADSLeanPlayer.c','LogicSource/Scripts/5_Mission/MLADSLeanKeys.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   code=(KIT/path).read_text().replace('MLADSLEAN16','MLADSLEAN15').replace('lean v16','lean v15')
   self.assertEqual(code,(OLD/path).read_text())
 def test_revision_matches_actual_graph_amounts(self):
  spec=json.loads((KIT/'Head-Direction-v16.json').read_text())
  n=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
  self.assertEqual(len(spec['changed_nodes']),4)
  for item in spec['changed_nodes']:
   self.assertEqual(float(re.search(r'Amount ([-+0-9.eE]+)',n[item['node']])[1]),item['new_graph_amount'])
 def test_current_package_hashes_and_launcher(self):
  validation=json.loads((KIT/'validation.json').read_text())
  for p,h in validation['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  cmd=(KIT/'Launch-Mosin-Lean-Test.cmd').read_text()
  self.assertNotRegex(cmd.lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v16-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 for name in loader.getTestCaseNames(previous.NativeHeadTiltTests):
  if name not in ['test_head_roll_removed_and_forward_nod_retained','test_current_pbo_hashes_and_direct_launcher']:suite.addTest(previous.NativeHeadTiltTests(name))
 suite.addTests(loader.loadTestsFromTestCase(LeftHeadDirectionTests));return suite
if __name__=='__main__':unittest.main()
