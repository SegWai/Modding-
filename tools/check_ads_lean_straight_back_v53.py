"""Straight standing-right spine with preserved height, reach, grip and footing."""
from pathlib import Path
import sys,json,re,math,hashlib,zipfile,unittest
import numpy as np
sys.dont_write_bytecode=True
from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
from package_ads_lean_runtime import runtime_files
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v52';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v53'
sys.path.insert(0,str(B));from build_pbos import read_pbo
class StraightRightBack(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads((B/'Straight-Standing-Right-Back-v53.json').read_text());cls.old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());cls.g=(B/'WorkspaceSource/locomotion.agf').read_text();cls.n=newnodes(cls.g)
 def test_spine_centres_straight_and_all_segment_lengths_retained(self):
  a=self.d['reference'];b=self.d['desired'];chain=self.d['spine_chain']
  self.assertGreater(self.d['max_spine_centreline_deviation_before_m'],.04)
  self.assertLess(self.d['max_spine_centreline_deviation_after_m'],1e-10)
  for first,last in zip(chain,chain[1:]):
   x=np.linalg.norm(np.array(a[last])[:3,3]-np.array(a[first])[:3,3]);y=np.linalg.norm(np.array(b[last])[:3,3]-np.array(b[first])[:3,3]);self.assertAlmostEqual(x,y,places=10)
  self.assertLess(np.linalg.norm(self.d['pelvis_translation_m']),.02)
 def test_head_height_32cm_grip_and_foot_frames_identical(self):
  a=self.d['reference'];b=self.d['desired']
  def belongs(n,root):
   while n:
    if n==root:return True
    n=self.d['parents'][n]
   return False
  for n in a:
   if any(belongs(n,root) for root in ('Neck','LeftHand','RightHand','LeftFoot','RightFoot')):self.assertTrue(np.allclose(a[n],b[n],atol=1e-9,rtol=0),n)
  self.assertAlmostEqual(b['Head'][0][3],.32,places=10);self.assertAlmostEqual(b['Head'][1][3],a['Head'][1][3],places=12)
  for limb in ('Left','Right'):
   for chain in (('Arm','ForeArm','Hand'),('UpLeg','Leg','Foot')):
    names=[limb+x for x in chain]
    for first,last in zip(names,names[1:]):self.assertAlmostEqual(np.linalg.norm(np.array(a[last])[:3,3]-np.array(a[first])[:3,3]),np.linalg.norm(np.array(b[last])[:3,3]-np.array(b[first])[:3,3]),places=9)
 def test_only_one_existing_edge_changed_before_trim_and_publication(self):
  for name,node in self.old.items():
   if name.startswith('{'):continue
   expected=node.replace('Child "ML50_left_BodyBlend"','Child "ML53_StandingRightBackOnly"') if name=='ML50_IdleReachTrim' else node
   self.assertEqual(self.n[name],expected,name)
  added={n for n in self.n.keys()-self.old.keys() if not n.startswith('{')};self.assertEqual(added,set(self.d['graph_nodes'])|{'ML53_StandingRightBackOnly'})
  self.assertIn('Child "ML50_IdleReachTrim"',self.n['ML50_PublishBalancedWeapon'])
  self.assertIn('Amount -1.047197551197',self.n['ML51_StandingRightElbowOut'])
 def test_scope_excludes_left_walk_crouch_and_native(self):
  expr=re.search(r'BlendWeight "([^"]+)"',self.n['ML53_StandingRightBackOnly'])[1];self.assertEqual(expr,self.d['scope_gate'])
  for lean in (-1,0,1):
   for gate in (0,1):
    for stance in (0,1,2):
     for move in (0,1):
      for speed in (0,1,2,3):
       got=eval(expr,{'__builtins__':{},'clamp':lambda x,a,b:max(a,min(b,x))},dict(MLADSLeanAmount=lean,MLADSLeanGate=gate,Stance=stance,MLADSLeanMoveBlend=move,MovementSpeed=speed))
       self.assertEqual(got,1 if (lean,gate,stance,move,speed)==(1,1,0,0,0) else 0)
  self.assertNotIn('MLADSLeanCanary',expr)
 def test_native_transform_serialization_reconstructs_target(self):
  d=self.d;out=bridge.reconstruct(d['reference'],d['parents'],d['corrections']);self.assertLess(max(abs(out[n][i][j]-d['desired'][n][i][j]) for n in out for i in range(4) for j in range(4)),1e-10)
  child='ML50_left_BodyBlend';names=[]
  for bone in bridge.ordered(d['parents']):
   if bone.startswith(('Face_','Eye')):continue
   for op,key,sign in [('Rotate','rotation_xyz',-1),('Translate','translation_xyz',1)]:
    for axis,value in zip('XYZ',d['corrections'][bone][key]):
     if abs(value)<1e-9:continue
     name=f'ML53_RightBack_{bone}_{op}_{axis}';node=self.n[name];names.append(name)
     for s in (f'Child "{child}"',f'Bone "{bone}"',f'Axis {axis}',f'Op {op}','Space Model','Expression "1.0"'):self.assertIn(s,node)
     self.assertAlmostEqual(float(re.search(r'Amount ([-+\d.eE]+)',node)[1]),sign*value,places=11);child=name
  self.assertEqual(names,d['graph_nodes']);self.assertIn(f'Child1 "{child}"',self.n['ML53_StandingRightBackOnly'])
 def test_runtime_and_camera_unmodified(self):
  for p in (A/'LogicSource/Scripts').rglob('*.c'):
   s=(B/p.relative_to(A)).read_text()
   for x,y in [('MLADSLEAN53','MLADSLEAN52'),('MLPOSE53','MLPOSE52'),('MLWALK53','MLWALK52'),('MLCAM53','MLCAM52'),('MLDIST53','MLDIST52'),('lean v53','lean v52'),('Lean v53','Lean v52')]:s=s.replace(x,y)
   self.assertEqual(s,p.read_text())
 def test_pbo_hashes_resource_and_runtime_only_zip(self):
  for p,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((B/p).read_bytes()).hexdigest(),h)
  _,files=read_pbo((B/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes());self.assertEqual(files['MLADSLeanLocomotion_v53.agf'],self.g.encode())
  self.assertIn(b'MLADSLeanLocomotion_v53.agf',files['player_main.agr'])
  with zipfile.ZipFile(R/'artifacts/MovementLab_ADS_Lean_Mosin_v53.zip') as z:
   self.assertIsNone(z.testzip());self.assertEqual(set(z.namelist()),{B.name+'/'+p for p in runtime_files(B)})
   for n in z.namelist():self.assertNotRegex(n.lower(),r'blender|\.blend|\.png|\.py$')
if __name__=='__main__':unittest.main()
