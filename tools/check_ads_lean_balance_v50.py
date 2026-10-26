"""Balanced 32cm standing reach: preserved footing/grip, scope and idle residual trim."""
from pathlib import Path
import json,re,sys,math,hashlib,unittest,zipfile
import numpy as np
sys.dont_write_bytecode=True
import captured_pose_bridge as pose
from dayz_graph_formats import newnodes,end
from package_ads_lean_runtime import runtime_files
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v49';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v50'
sys.path.insert(0,str(B));from build_pbos import read_pbo
class BalancedStanding(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads((B/'Balanced-Standing-Reach-v50.json').read_text());cls.g=(B/'WorkspaceSource/locomotion.agf').read_text();cls.n=newnodes(cls.g);cls.old=newnodes((A/'WorkspaceSource/locomotion.agf').read_text())
 def test_true_32cm_final_reach_not_neutral_travel(self):
  xs=[]
  for side,sign in [('left',-1),('right',1)]:
   d=self.s['sides'][side];self.assertAlmostEqual(d['desired']['Head'][0][3],sign*.32,places=10)
   out=pose.reconstruct(d['reference'],self.s['parents'],d['corrections'])
   self.assertLess(max(abs(out[n][i][j]-d['desired'][n][i][j]) for n in out for i in range(4) for j in range(4)),1e-10)
   xs.append(out['Head'][0][3])
  self.assertAlmostEqual(xs[0]+xs[1],0,places=10)
 def test_feet_toes_planted_and_limb_lengths_preserved(self):
  for d in self.s['sides'].values():
   a=d['reference'];b=d['desired']
   for n in d['lower_bones_preserved']:self.assertTrue(np.allclose(a[n],b[n],rtol=0,atol=1e-10),n)
   for limb in ('Left','Right'):
    for suffix in [('Arm','ForeArm','Hand'),('UpLeg','Leg','Foot')]:
     names=[limb+k for k in suffix]
     for first,last in zip(names,names[1:]):
      old=np.linalg.norm(np.array(a[first])[:3,3]-np.array(a[last])[:3,3]);new=np.linalg.norm(np.array(b[first])[:3,3]-np.array(b[last])[:3,3]);self.assertAlmostEqual(old,new,places=9)
   self.assertLess(abs(d['hip_lateral_shift_m']),.06)
   self.assertLess(abs(d['spine_total_adjustment_degrees']),20)
 def test_head_gun_grip_orientation_and_relative_positions_preserved(self):
  for d in self.s['sides'].values():
   a=d['reference'];b=d['desired'];delta=np.array(d['head_translation_m'])
   for n in ['Head','LeftHand','RightHand']:
    self.assertTrue(np.allclose(np.array(a[n])[:3,:3],np.array(b[n])[:3,:3],atol=1e-10,rtol=0))
    self.assertTrue(np.allclose(np.array(b[n])[:3,3]-np.array(a[n])[:3,3],delta,atol=1e-10,rtol=0))
   # Every finger keeps its original transform relative to its own wrist.
   for n in a:
    wrist='LeftHand' if n.startswith('LeftHand') else 'RightHand' if n.startswith('RightHand') else None
    if wrist:self.assertTrue(np.allclose(np.linalg.inv(a[wrist])@a[n],np.linalg.inv(b[wrist])@b[n],rtol=0,atol=1e-10))
 def test_old_modes_graph_unchanged_and_new_scope_zero_elsewhere(self):
  for name,node in self.old.items():
   if name.startswith('{'):continue
   expected=node.replace('Child "ML48_StandingLeftOnly"','Child "ML50_StandingBalancedOnly"') if name=='MeleeBlockQ' else node
   self.assertEqual(self.n[name],expected,name)
  expr=re.search(r'BlendWeight "([^"]+)"',self.n['ML50_StandingBalancedOnly'])[1]
  self.assertEqual(expr,self.s['scope_gate'])
  for lean in (-1,0,1):
   for gate in (0,1):
    for stance in (0,1,2):
     for move in (0,1):
      for speed in (0,1,2,3):
       w=eval(expr,{'__builtins__':{},'abs':abs,'clamp':lambda x,a,b:max(a,min(b,x))},dict(MLADSLeanAmount=lean,MLADSLeanGate=gate,Stance=stance,MLADSLeanMoveBlend=move,MovementSpeed=speed))
       self.assertEqual(w,abs(lean)*gate if stance==0 and move==0 and speed==0 else 0)
  self.assertNotIn('MLADSLeanCanary',expr)
  for field in ('WeightAim','WeightPrimaryChain','WeightSecondaryChain'):self.assertIn(field+' "false"',self.n['ML50_PublishBalancedWeapon'])
 def test_transform_chain_uses_solved_native_signs(self):
  base='ML48_StandingLeftOnly'
  for side,sign in [('right',''),('left','-')]:
   d=self.s['sides'][side];child=base;names=[]
   for bone in pose.ordered(self.s['parents']):
    if bone.startswith(('Face_','Eye')):continue
    for op,field,conv in [('Rotate','rotation_xyz',-1),('Translate','translation_xyz',1)]:
     for axis,value in zip('XYZ',d['corrections'][bone][field]):
      if abs(value)<1e-9:continue
      name=f'ML50_{side}_{bone}_{op}_{axis}';node=self.n[name];names.append(name)
      for text in (f'Child "{child}"','Expression "1.0"',f'Bone "{bone}"',f'Axis {axis}',f'Op {op}','Space Model'):self.assertIn(text,node)
      self.assertAlmostEqual(float(re.search(r'Amount ([-+\d.eE]+)',node)[1]),conv*value,places=11);child=name
   self.assertEqual(names,d['graph_nodes']);blend=self.n['ML50_'+side+'_BodyBlend'];self.assertIn(f'Child0 "{base}"',blend);self.assertIn(f'Child1 "{child}"',blend)
   self.assertIn(f'clamp({sign}MLADSLeanAmount, 0.0, 1.0)',blend);base='ML50_'+side+'_BodyBlend'
  self.assertIn(f'Child "{base}"',self.n['ML50_IdleReachTrim']);self.assertIn('Bone "Spine"',self.n['ML50_IdleReachTrim'])
  self.assertIn('Child "ML50_IdleReachTrim"',self.n['ML50_PublishBalancedWeapon'])
 def test_idle_feedback_bounded_convergent_and_fades(self):
  # Exact unit-gain spine-X readback model, including measured-style idle sway.
  for sign in (-1,1):
   trim=0;observed=[]
   for frame in range(360):
    bias=.006*sign+.001*math.sin(frame/60*math.pi*2)
    head=sign*.32+bias+trim;error=sign*.32-head
    trim=max(-.02,min(.02,trim+error*(1/60/.25)))
    self.assertLessEqual(abs(trim),.02)
    if frame>=240:observed.append(head)
   self.assertLess(abs(sum(observed)/len(observed)-sign*.32),.0005)
   for _ in range(180):trim*=1-(1/60/.18)
   self.assertLess(abs(trim),1e-8)
  player=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  helper=player[player.index(' protected void ML50UpdateStandingReach('):player.index(' // Standing exposure calibration:')]
  for text in ('state.m_iMovement == 0','m_MLADSLeanMoveBlend < 0.02','m_MLADSLeanGate > 0.98','Math.AbsFloat(m_MLADSLeanAmount) > 0.98','!MLADSLeanSettings.DistanceNativeReference','head == -1','m_ML50ReachStable < 0.2','step / 0.25','-0.02, 0.02','step / 0.18'):self.assertIn(text,helper)
  self.assertNotIn('AnimSet',helper);self.assertNotIn('SetPosition',helper);self.assertNotIn('m_MLADSLeanDemo',helper)
  marker=player.index('AnimSetFloat(m_ML50ReachVar, m_ML50ReachTrim)');self.assertLess(player.index('super.CommandHandler'),marker);self.assertLess(marker,player.index(' // Shared neutral-standing head-height'))
 def test_existing_player_logic_is_unchanged_outside_scoped_feedback(self):
  current=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  current=re.sub(r'^ protected (?:int|bool|float) m_ML50\w+[^\n]*\n','',current,flags=re.M)
  a=current.index('   m_ML50ReachVar =');b=current.index('   if (localPlayer)',a);current=current[:a]+current[b:]
  current=current.replace('  ML50UpdateStandingReach(pDt, state);\n  if (m_MLADSLeanBound && m_ML50ReachBound)\n   AnimSetFloat(m_ML50ReachVar, m_ML50ReachTrim);\n','')
  a=current.index(' // Shared player/NPC steady-standing idle correction.');b=current.index(' // Standing exposure calibration:',a);current=current[:a]+current[b:]
  current=current.replace('  bool reachActive = m_ML50ReachStable >= 0.2;\n','')
  current=re.sub(r'^  status \+= " reach_[^\n]*\n','',current,flags=re.M)
  for x,y in [('MLADSLEAN50','MLADSLEAN49'),('MLPOSE50','MLPOSE49'),('MLWALK50','MLWALK49'),('MLCAM50','MLCAM49'),('MLDIST50','MLDIST49')]:current=current.replace(x,y)
  self.assertEqual(current,(A/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text())
 def test_registration_bindings_resources_camera_and_package(self):
  agr=(B/'WorkspaceSource/player_main.agr').read_text();old=(A/'WorkspaceSource/player_main.agr').read_text()
  self.assertEqual(agr.count('AnimSrcGCTVarFloat MLADSLeanStandReachTrim {'),1)
  self.assertIn('MinValue -0.02',agr);self.assertIn('MaxValue 0.02',agr)
  def controls(s):
   i=s.index('  Variables {');return s[i:end(s,i)]
  current=controls(agr);current=re.sub(r' AnimSrcGCTVarFloat MLADSLeanStandReachTrim \{[^{}]*\}\n  ','',current)
  self.assertEqual(current,controls(old))
  c=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();self.assertIn('m_ML50ReachBound = m_ML50ReachVar >= 0;',c)
  for other in ('Gate','Canary','Amount','NativeLean','NativeMove','WeaponShift','Height','MoveBlend'):self.assertIn('m_ML50ReachVar != m_MLADSLean'+other+'Var',c)
  self.assertEqual((A/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes(),(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes())
  _,entries=read_pbo((B/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes());self.assertEqual(entries['MLADSLeanLocomotion_v50.agf'],self.g.encode());self.assertEqual(entries['player_main.agr'],agr.encode())
  for p,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((B/p).read_bytes()).hexdigest(),h)
  with zipfile.ZipFile(R/'artifacts/MovementLab_ADS_Lean_Mosin_v50.zip') as z:
   self.assertEqual(set(z.namelist()),{B.name+'/'+p for p in runtime_files(B)});self.assertIsNone(z.testzip())
   for name in z.namelist():self.assertNotRegex(name.lower(),r'blender|\.blend|\.png|\.py$')
if __name__=='__main__':unittest.main()
