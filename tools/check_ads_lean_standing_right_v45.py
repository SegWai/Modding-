"""Measured native standing-right transfer and strict graph endpoint isolation."""
import sys,re,json,hashlib,unittest,math
from pathlib import Path
sys.dont_write_bytecode=True
from dayz_graph_formats import newnodes,end
import captured_pose_bridge as pose
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v44';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v45'
sys.path.insert(0,str(B));from build_pbos import read_pbo
class StandingRight(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.g=(B/'WorkspaceSource/locomotion.agf').read_text();cls.old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());cls.n=newnodes(cls.g);cls.spec=json.loads((B/'Standing-Right-Pose-v45.json').read_text())
 def test_only_new_branch_and_single_existing_edge_changed(self):
  for name,node in self.old.items():
   if name.startswith('{'):continue
   if name=='MeleeBlockQ':self.assertEqual(self.n[name],node.replace('Child "SickHotColdQ"','Child "ML45_StandingRightOnly"'))
   else:self.assertEqual(self.n[name],node,name)
  added={n for n in self.n.keys()-self.old.keys() if not n.startswith('{')}
  self.assertEqual(added,set(self.spec['graph_nodes'])|{'ML45_PublishStandingRightWeapon','ML45_StandingRightOnly'})
 def test_gate_and_steady_endpoint_scope(self):
  expr=re.search(r'BlendWeight "([^"]+)"',self.n['ML45_StandingRightOnly'])[1]
  self.assertEqual(expr,self.spec['gate'])
  def weight(lean,gate,stance,move,speed):
   values=dict(MLADSLeanAmount=lean,MLADSLeanGate=gate,Stance=stance,MLADSLeanMoveBlend=move,MovementSpeed=speed)
   return eval(expr,{'__builtins__':{},'clamp':lambda x,a,b:max(a,min(b,x))},values)
  self.assertEqual(weight(1,1,0,0,0),1)
  for lean in (-1,0,1):
   for gate in (0,1):
    for stance in (0,1,2):
     for move in (0,1):
      for speed in (0,1,2,3):
       if lean==1 and gate==1 and stance==0 and move==0 and speed==0:continue
       self.assertEqual(weight(lean,gate,stance,move,speed),0)
  self.assertEqual(weight(1,1,0,0,1),0) # no transient gait leak at raw walk speed
  self.assertIn('OptimizeMin 1',self.n['ML45_StandingRightOnly'])
  self.assertNotIn('MLADSLeanCanary',expr) # shared player/NPC activation
 def test_measured_native_reference_matches_complete_approved_target(self):
  s=self.spec
  self.assertEqual(s['source_reference_id'],'82178_false');self.assertEqual(s['desired_capture_id'],'67091_true')
  self.assertIn('lean=1 move_blend=0 gate=1 raised=true',s['reference_metadata'])
  reconstructed=pose.reconstruct(s['reference'],s['parents'],s['corrections'])
  error=max(abs(reconstructed[n][i][j]-s['desired'][n][i][j]) for n in s['parents'] for i in range(4) for j in range(4))
  self.assertLess(error,1e-10)
  native=json.loads((B/'Requested-Standing-Right-Pose.json').read_text())['desired_capture']['bones']
  for n in s['parents']:
   if n.startswith(('Face_','Eye')):continue
   for i in range(3):self.assertAlmostEqual(reconstructed[n][i][3],native[n]['3'][i],places=10)
  self.assertLess(s['weapon_rigid_follow_prediction_position_error_m'],.001)
  self.assertLess(s['weapon_rigid_follow_prediction_rotation_component_error'],.00001)
 def test_serialized_native_transform_sign_order_values_and_chain(self):
  s=self.spec;child='SickHotColdQ';names=[]
  for bone in pose.ordered(s['parents']):
   if bone.startswith(('Face_','Eye')):continue
   for op,field,sign in [('Rotate','rotation_xyz',-1),('Translate','translation_xyz',1)]:
    for axis,value in zip('XYZ',s['corrections'][bone][field]):
     if abs(value)<1e-10:continue
     name=f'ML45_StaticRight_{bone}_{op}_{axis}';node=self.n[name];names.append(name)
     self.assertIn(f'Child "{child}"',node);self.assertIn('Expression "1.0"',node)
     self.assertIn(f'Bone "{bone}"',node);self.assertIn(f'Axis {axis}',node);self.assertIn('Space Model',node);self.assertIn(f'Op {op}',node)
     actual=float(re.search(r'Amount ([-+\d.eE]+)',node)[1]);self.assertAlmostEqual(actual,sign*value,places=11)
     child=name
  self.assertEqual(names,s['graph_nodes'])
  self.assertIn(f'Child "{child}"',self.n['ML45_PublishStandingRightWeapon'])
 def test_final_weapon_stage_publishes_without_resolving_or_reaiming(self):
  n=self.n['ML45_PublishStandingRightWeapon']
  for prop in ('WeightAim','WeightPrimaryChain','WeightSecondaryChain'):self.assertIn(prop+' "false"',n)
  self.assertIn('outputweaponoffsettobuffer = true',n)
  self.assertIn('Child0 "SickHotColdQ"',self.n['ML45_StandingRightOnly'])
  self.assertIn('Child1 "ML45_PublishStandingRightWeapon"',self.n['ML45_StandingRightOnly'])
  self.assertIn('Child "ML45_StandingRightOnly"',self.n['MeleeBlockQ'])
 def test_control_template_and_runtime_pose_inputs_unchanged(self):
  a=(A/'WorkspaceSource/player_main.agr').read_text();b=(B/'WorkspaceSource/player_main.agr').read_text()
  # Fresh resource name/GUID only, no new controls/bindings.
  a=re.sub(r'\{[A-F0-9]+\}DZ/anims/workspaces/player/player_main/MLADSLeanLocomotion_v41.agf','RESOURCE',a)
  b=re.sub(r'\{[A-F0-9]+\}DZ/anims/workspaces/player/player_main/MLADSLeanLocomotion_v45.agf','RESOURCE',b)
  self.assertEqual(a,b)
  for p in list((A/'LogicSource/Scripts/4_World').glob('*.c'))+[A/'Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   current=(B/p.relative_to(A)).read_text().replace('MLADSLEAN45','MLADSLEAN44').replace('MLPOSE45','MLPOSE44').replace('lean v45','lean v44').replace('Lean v45','Lean v44')
   self.assertEqual(p.read_text(),current)
 def test_resource_integrity_and_no_menu(self):
  agr=(B/'WorkspaceSource/player_main.agr').read_text()
  self.assertIn('MLADSLeanLocomotion_v45.agf',agr)
  _,files=read_pbo((B/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes())
  self.assertEqual(files['MLADSLeanLocomotion_v45.agf'],self.g.encode())
  self.assertEqual(files['player_main.agr'],agr.encode())
  for path,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((B/path).read_bytes()).hexdigest(),h)
  self.assertIn('Mosin-Lean-v45-Logs',(B/'Collect-Logs.ps1').read_text());self.assertIn('F:\\DayZProjects',(B/'Launch-Test.ps1').read_text())
  self.assertNotRegex((B/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
if __name__=='__main__':unittest.main()
