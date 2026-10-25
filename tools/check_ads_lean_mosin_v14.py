"""Head compensation and stationary-only leg restoration; retain v13 controller."""
import sys,unittest,re,json,math,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v14'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v13'
EARLY=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v3'
base.KIT=KIT
class PoseRevisionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.graph=(KIT/'WorkspaceSource/locomotion.agf').read_text();cls.nodes=newnodes(cls.graph)
  cls.oldgraph=(OLD/'WorkspaceSource/locomotion.agf').read_text();cls.oldnodes=newnodes(cls.oldgraph)
 def test_head_correction_is_shared_final_head_only_pass(self):
  n=self.nodes
  self.assertIn('Child "ML14_HeadCounterRoll"',n['SickHotColdQ'])
  self.assertIn('Child "ML14_HeadForwardNod"',n['ML14_HeadCounterRoll'])
  self.assertIn('Child "NormalWeaponIK"',n['ML14_HeadForwardNod'])
  for name in ['ML14_HeadForwardNod','ML14_HeadCounterRoll']:
   self.assertEqual(re.findall(r'Bone "([^"]+)"',n[name]),['Head'])
   expr=re.search(r'Expression "([^"]+)"',n[name])[1]
   self.assertIn('MLADSLeanGate',expr);self.assertIn('MLADSLeanAmount',expr)
   self.assertNotIn('MLADSLeanCanary',expr) # no NPC-only condition
  pitch=float(re.search(r'Amount ([-0-9.eE]+)',n['ML14_HeadForwardNod'])[1])
  roll=float(re.search(r'Amount ([-0-9.eE]+)',n['ML14_HeadCounterRoll'])[1])
  self.assertAlmostEqual(math.degrees(pitch),-5,places=6)
  self.assertAlmostEqual(math.degrees(roll),-12,places=6)
  for gate,lean in [(0,-1),(0,1),(1,0),(1,-1),(1,1)]:
   p=abs(lean)*gate*pitch;r=lean*gate*roll
   if not gate or not lean:self.assertEqual((p,r),(0,0))
   else:self.assertAlmostEqual(p,pitch);self.assertAlmostEqual(abs(r),abs(roll))
 def test_stationary_lower_amounts_restore_early_pose(self):
  spec=json.loads((EARLY/'Pose-Spec.json').read_text())['corrections']
  rev=json.loads((KIT/'Pose-Revision-v14.json').read_text())
  for side in ['left','right']:
   for bone in rev['stationary_lower_bones']:
    for op,field,sign in [('Rotate','rotation_xyz',-1),('Translate','translation_xyz',1)]:
     for axis,wanted in zip('XYZ',spec[side][bone][field]):
      name=f'ML5_StandIdle_{side}_{bone}_{op}_{axis}'
      if name not in self.nodes:
       self.assertLess(abs(wanted),1e-4 if op=='Rotate' else 1e-5);continue
      got=float(re.search(r'Amount ([-+0-9.eE]+)',self.nodes[name])[1])
      self.assertAlmostEqual(got,sign*wanted,places=8,msg=name)
 def test_static_snapshot_feet_match_early_spread_and_height(self):
  static=json.loads((KIT/'Static-Pose-Snapshot.json').read_text())
  early=json.loads((EARLY/'Pose-Snapshot.json').read_text())
  for side in ['left','right']:
   for bone in ['LeftFoot','RightFoot']:
    for axis in range(3):self.assertAlmostEqual(static[side][bone][axis][3],early[side][bone][axis][3],places=5)
   spread=static[side]['RightFoot'][0][3]-static[side]['LeftFoot'][0][3]
   self.assertAlmostEqual(spread,.76,places=4)
 def test_only_static_lower_and_final_head_nodes_changed(self):
  changed=[]
  for name,node in self.oldnodes.items():
   if not name.startswith('{') and self.nodes[name]!=node:changed.append(name)
  rev=json.loads((KIT/'Pose-Revision-v14.json').read_text())
  self.assertEqual(set(changed),set(rev['modified_static_nodes'])|{'SickHotColdQ'})
  self.assertEqual({n for n in set(self.nodes)-set(self.oldnodes) if not n.startswith('{')},{'ML14_HeadForwardNod','ML14_HeadCounterRoll'})
  for mode in ['StandWalk','CrouchIdle','CrouchWalk']:
   for name in self.oldnodes:
    if name.startswith('ML5_'+mode+'_'):self.assertEqual(self.nodes[name],self.oldnodes[name])
  self.assertEqual(self.nodes['MovementRasIK'],self.oldnodes['MovementRasIK'])
  self.assertEqual(self.nodes['NormalWeaponIK'],self.oldnodes['NormalWeaponIK'])
 def test_working_controller_and_control_template_unchanged(self):
  self.assertEqual((KIT/'WorkspaceSource/player_main.agr').read_bytes(),(OLD/'WorkspaceSource/player_main.agr').read_bytes())
  for path in ['LogicSource/Scripts/4_World/MLADSLeanPlayer.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   new=(KIT/path).read_text().replace('MLADSLEAN14','MLADSLEAN13').replace('lean v14','lean v13')
   self.assertEqual(new,(OLD/path).read_text())
  self.assertEqual(re.findall(r'HasVariableChanged\([^\n]+',self.graph),re.findall(r'HasVariableChanged\([^\n]+',self.oldgraph))
 def test_no_new_controls_and_pbo_hashes_valid(self):
  agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
  declared=set(re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr))
  for arg in re.findall(r'HasVariableChanged\(\s*([^,)\n]+)',self.graph):self.assertIn(arg.strip(),declared)
  self.assertNotIn('MLADSLeanDemoActive',self.graph)
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
 def test_direct_launcher_and_current_log_label(self):
  cmd=(KIT/'Launch-Mosin-Lean-Test.cmd').read_text();ps=(KIT/'Launch-Test.ps1').read_text()
  self.assertNotRegex(cmd.lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('F:\\DayZProjects',ps)
  self.assertIn('Mosin-Lean-v14-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(PoseRevisionTests));return suite
if __name__=='__main__':unittest.main()
