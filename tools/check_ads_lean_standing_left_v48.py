"""Transfer uploaded frame15 only to standing anatomical-left custom lean."""
from pathlib import Path
import unittest,json,re,hashlib,sys,zipfile
sys.dont_write_bytecode=True
import captured_pose_bridge as pose
from dayz_graph_formats import newnodes
from package_ads_lean_runtime import FILES
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v47';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v48'
sys.path.insert(0,str(B));from build_pbos import read_pbo
class StandingLeft(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());cls.graph=(B/'WorkspaceSource/locomotion.agf').read_text();cls.n=newnodes(cls.graph);cls.s=json.loads((B/'Standing-Left-Frame15-v48.json').read_text())
 def test_old_right_walk_crouch_native_nodes_unchanged(self):
  for name,node in self.old.items():
   if name.startswith('{'):continue
   expected=node.replace('Child "ML45_StandingRightOnly"','Child "ML48_StandingLeftOnly"') if name=='MeleeBlockQ' else node
   self.assertEqual(self.n[name],expected,name)
  added={n for n in self.n.keys()-self.old.keys() if not n.startswith('{')}
  self.assertEqual(added,set(self.s['graph_nodes'])|{'ML48_PublishStandingLeftWeapon','ML48_StandingLeftOnly'})
 def test_scope_only_left_standing_and_disjoint_right(self):
  expr=re.search(r'BlendWeight "([^"]+)"',self.n['ML48_StandingLeftOnly'])[1];self.assertEqual(expr,self.s['gate'])
  right=re.search(r'BlendWeight "([^"]+)"',self.n['ML45_StandingRightOnly'])[1]
  def weight(expr,lean,gate,stance,move,speed):
   return eval(expr,{'__builtins__':{},'clamp':lambda x,a,b:max(a,min(b,x))},dict(MLADSLeanAmount=lean,MLADSLeanGate=gate,Stance=stance,MLADSLeanMoveBlend=move,MovementSpeed=speed))
  for lean in (-1,-.5,0,.5,1):
   for gate in (0,.5,1):
    for stance in (0,1,2):
     for move in (0,1):
      for speed in (0,1,2,3):
       w=weight(expr,lean,gate,stance,move,speed)
       self.assertEqual(w,max(0,-lean)*gate if stance==0 and move==0 and speed==0 else 0)
       self.assertEqual(w*weight(right,lean,gate,stance,move,speed),0)
  self.assertNotIn('MLADSLeanCanary',expr);self.assertIn('OptimizeMin 1',self.n['ML48_StandingLeftOnly'])
 def test_exact_native_frame15_origins_and_reference(self):
  s=self.s;self.assertEqual(s['desired_blender_frame'],15);self.assertEqual(s['desired_capture_id'],'33626_true');self.assertEqual(s['source_reference_id'],'37205_false')
  self.assertIn('lean=-1 move_blend=0 gate=1 raised=true',s['reference_metadata'])
  target=json.loads((B/'Frame15-Standing-Left-Target.json').read_text())['desired_native_capture'];self.assertEqual(target['index'],14)
  replay=pose.reconstruct(s['reference'],s['parents'],s['corrections'])
  self.assertLess(max(abs(replay[n][i][j]-s['desired'][n][i][j]) for n in replay for i in range(4) for j in range(4)),1e-10)
  for n in replay:
   if n.startswith(('Face_','Eye')):continue
   for i in range(3):self.assertAlmostEqual(replay[n][i][3],target['bones'][n]['3'][i],places=10)
  self.assertLess(s['weapon_rigid_follow_prediction_position_error_m'],.001)
  self.assertLess(s['weapon_rigid_follow_prediction_rotation_component_error'],.00001)
 def test_native_transform_chain_pivot_order_sign_and_amounts(self):
  child='ML45_StandingRightOnly';names=[]
  for bone in pose.ordered(self.s['parents']):
   if bone.startswith(('Face_','Eye')):continue
   for op,field,sign in [('Rotate','rotation_xyz',-1),('Translate','translation_xyz',1)]:
    for axis,value in zip('XYZ',self.s['corrections'][bone][field]):
     if abs(value)<1e-10:continue
     name=f'ML48_StaticLeft_{bone}_{op}_{axis}';n=self.n[name];names.append(name)
     for text in (f'Child "{child}"','Expression "1.0"',f'Bone "{bone}"',f'Axis {axis}','Space Model',f'Op {op}'):self.assertIn(text,n)
     self.assertAlmostEqual(float(re.search(r'Amount ([-+\d.eE]+)',n)[1]),sign*value,places=11);child=name
  self.assertEqual(names,self.s['graph_nodes']);self.assertIn(f'Child "{child}"',self.n['ML48_PublishStandingLeftWeapon'])
  for field in ('WeightAim','WeightPrimaryChain','WeightSecondaryChain'):self.assertIn(field+' "false"',self.n['ML48_PublishStandingLeftWeapon'])
  self.assertIn('outputweaponoffsettobuffer = true',self.n['ML48_PublishStandingLeftWeapon'])
  self.assertIn('Child0 "ML45_StandingRightOnly"',self.n['ML48_StandingLeftOnly'])
 def test_runtime_camera_mission_controls_unchanged(self):
  for p in list((A/'LogicSource/Scripts/4_World').glob('*.c'))+[A/'Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   new=(B/p.relative_to(A)).read_text()
   for a,b in [('MLADSLEAN48','MLADSLEAN47'),('MLPOSE48','MLPOSE47'),('MLWALK48','MLWALK47'),('MLCAM48','MLCAM47'),('lean v48','lean v47'),('Lean v48','Lean v47')]:new=new.replace(a,b)
   self.assertEqual(new,p.read_text())
  a=(A/'WorkspaceSource/player_main.agr').read_text();b=(B/'WorkspaceSource/player_main.agr').read_text()
  for text,version in ((a,45),(b,48)):self.assertIn(f'MLADSLeanLocomotion_v{version}.agf',text)
  def strip(text,version):return re.sub(r'\{[A-F0-9]+\}DZ/anims/workspaces/player/player_main/MLADSLeanLocomotion_v'+str(version)+r'.agf','RESOURCE',text)
  self.assertEqual(strip(a,45),strip(b,48))
  keys=(B/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();self.assertNotIn('OnUpdate',keys);self.assertNotIn('ExportLeftWalkFrame',keys);self.assertNotIn('m_MLADSPoseRecording',keys)
  self.assertIn('MLADSLeanReportJoints();',keys)
 def test_pbo_resources_manifest_and_direct_launcher(self):
  _,files=read_pbo((B/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes());self.assertEqual(files['MLADSLeanLocomotion_v48.agf'],self.graph.encode())
  self.assertEqual(files['player_main.agr'],(B/'WorkspaceSource/player_main.agr').read_bytes())
  for path,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((B/path).read_bytes()).hexdigest(),h)
  self.assertIn('F:\\DayZProjects',(B/'Launch-Test.ps1').read_text());self.assertIn('Mosin-Lean-v48-Logs',(B/'Collect-Logs.ps1').read_text());self.assertNotRegex((B/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
 def test_zip_contains_only_runtime_essentials(self):
  with zipfile.ZipFile(R/'artifacts/MovementLab_ADS_Lean_Mosin_v48.zip') as z:
   self.assertIsNone(z.testzip());self.assertEqual(set(z.namelist()),{B.name+'/'+p for p in FILES})
   for name in z.namelist():
    self.assertNotRegex(name.lower(),r'blender|\.blend|\.png|\.py$|workspacesource|logicsource')
if __name__=='__main__':unittest.main()
