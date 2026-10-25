"""Offline coverage/symmetry/NPC-control regression checks; not a native playtest."""
from pathlib import Path
import unittest,json,re,sys,math
sys.dont_write_bytecode=True
from dayz_graph_formats import newnodes
import captured_pose_bridge as pose
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v5';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v4'
def load(name):return json.loads((KIT/name).read_text())
def expression(s,env):
 s=s.replace('&&',' and ').replace('||',' or ')
 s=re.sub(r'!(?!=)','not ',s)
 return eval(s,{'__builtins__':{}},env)
class ExpandedLeanTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.graph=(KIT/'WorkspaceSource/locomotion.agf').read_text();cls.nodes=newnodes(cls.graph);cls.code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();cls.coverage=load('Mode-Coverage.json')
 def test_full_lean_head_chest_and_hip_symmetry(self):
  s=load('Pose-Snapshot.json')
  for n in ['Pelvis','Spine','Spine1','Spine2','Spine3','Neck','Neck1','Head']:
   self.assertLess(abs(s['left'][n][0][3]+s['right'][n][0][3]-2*s['reference'][n][0][3]),1e-5,n)
   for i in [1,2]:self.assertLess(abs((s['left'][n][i][3]-s['reference'][n][i][3])-(s['right'][n][i][3]-s['reference'][n][i][3])),1e-5,n)
 def test_pose_math_and_partial_lean_symmetry(self):
  s=load('Pose-Snapshot.json');ds={k:pose.solve(s['reference'],s[k],s['parents']) for k in ['left','right']}
  for w in [0,.25,.5,.75,1]:
   p={k:pose.reconstruct(s['reference'],s['parents'],{n:{f:[x*w for x in values] for f,values in d.items()} for n,d in ds[k].items()}) for k in ds}
   for n in ['Pelvis','Spine3','Head']:self.assertLess(abs(p['left'][n][0][3]+p['right'][n][0][3]-2*s['reference'][n][0][3]),.001)
 def test_every_supported_native_branch_is_replaced(self):
  self.assertEqual(set(self.coverage),{'StandIdle','StandWalk','CrouchIdle','CrouchWalk'})
  for mode,c in self.coverage.items():
   self.assertEqual(self.graph.count('Child "'+c['output_node']+'"'),1,mode)
   for suffix in ['Left','Right']:
    body=self.nodes[c['native_chain']+suffix];expr=re.search(r'Expression "([^"]+)"',body)[1]
    for lean in [-1,-.5,0,.5,1]:
     self.assertEqual(expression(expr,{'clamp':lambda x,a,b:max(a,min(b,x)),'Lean':lean,'MLADSLeanGate':1}),0)
   for name,body in self.nodes.items():
    if name.startswith('ML5_'+mode+'_') and '_Collision' not in name and 'Expression' in body:self.assertIn('MLADSLeanAmount',body)
 def test_crouch_legs_and_walking_steps_remain_native(self):
  for mode,c in self.coverage.items():
   if mode!='StandIdle':self.assertFalse(any(any(word in n for word in ['Leg','Foot','Toe','HipExtra']) for n in c['bones']))
   if mode.startswith('Crouch'):self.assertNotIn('Pelvis',c['bones'])
  old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());self.assertEqual(old['MovementRasIK'],self.nodes['MovementRasIK'])
  expr=re.search(r'BlendWeight "([^"]+)"',self.nodes['MLADSLeanFootIKBlend'])[1]
  env={'clamp':lambda x,a,b:max(a,min(b,x)),'abs':abs,'MLADSLeanAmount':1,'MLADSLeanGate':1,'Stance':0,'MovementSpeed':0}
  self.assertEqual(expression(expr,env),1)
  for stance,speed in [(1,0),(1,1),(0,1),(2,0)]:self.assertEqual(expression(expr,dict(env,Stance=stance,MovementSpeed=speed)),0)
 def test_one_common_weapon_roll_target(self):
  rolls=re.findall(r'WeaponRoll "([^"]+)"',self.graph);self.assertEqual(rolls,['8.0*MLADSLeanAmount*MLADSLeanGate'])
  for stance in [0,1]:
   for speed in [0,1,2]:
    for amount in [-1,1]:self.assertEqual(expression(rolls[0],{'MLADSLeanAmount':amount,'MLADSLeanGate':1}),8*amount)
  self.assertEqual(expression(rolls[0],{'MLADSLeanAmount':1,'MLADSLeanGate':0}),0)
 def test_actual_activation_guard_covers_walk_crouch_and_demo(self):
  expr=re.search(r'bool target = ([^;]+);',self.code)[1]
  replacements={'MLADSLeanSettings.Enabled':'enabled','MLADSLeanSettings.Inspection':'inspection','IsAlive()':'alive','IsUnconscious()':'unconscious','state.m_iMovement':'movement','DayZPlayerConstants.COMMANDID_MOVE':'move_id'}
  for a,b in replacements.items():expr=expr.replace(a,b)
  base={'actorReady':True,'m_MLADSLeanBound':True,'enabled':True,'alive':True,'unconscious':False,'mosin':True,'supportedStance':True,'movement':0,'pCurrentCommandID':7,'move_id':7,'raised':True,'ready':True,'aiming':True,'inspection':False}
  for movement in [0,1,2]:self.assertTrue(expression(expr,dict(base,movement=movement)))
  for key in ['actorReady','m_MLADSLeanBound','enabled','mosin','supportedStance','aiming']:self.assertFalse(expression(expr,dict(base,**{key:False})),key)
  self.assertFalse(expression(expr,dict(base,movement=3)))
  self.assertIn('DayZPlayerConstants.STANCEIDX_RAISEDCROUCH',self.code)
  self.assertIn('(!localPlayer && !m_MLADSLeanDemo)',self.code)
 def test_distinct_five_bindings_and_valid_zero(self):
  expr=re.search(r'm_MLADSLeanBound = ([^;]+);',self.code)[1]
  names=['m_MLADSLeanGateVar','m_MLADSLeanCanaryVar','m_MLADSLeanAmountVar','m_MLADSLeanNativeLeanVar','m_MLADSLeanNativeMoveVar']
  for ids,ok in [([0,1,2,8,3],True),([0,0,0,0,0],False),([0,1,-1,8,3],False),([0,1,0,8,3],False)]:self.assertEqual(expression(expr,dict(zip(names,ids))),ok)
 def test_npc_actual_endpoint_conditions_and_native_input(self):
  left=re.search(r'if \((m_MLADSLeanDemoSign < 0 && lateral <= -2)\)\s+m_MLADSLeanDemoSign = (1);',self.code);right=re.search(r'else if \((m_MLADSLeanDemoSign > 0 && lateral >= 2)\)\s+m_MLADSLeanDemoSign = (-1);',self.code)
  self.assertIsNotNone(left);self.assertIsNotNone(right)
  def direction(sign,position):
   env={'m_MLADSLeanDemoSign':sign,'lateral':position}
   return int(left[2]) if expression(left[1],env) else int(right[2]) if expression(right[1],env) else sign
  for sign,x,wanted in [(-1,-2.01,1),(-1,-1.99,-1),(1,2.01,-1),(1,1.99,1)]:self.assertEqual(direction(sign,x),wanted)
  x=0;sign=-1;turns=0
  for i in range(400):
   nxt=direction(sign,x);turns+=int(nxt!=sign);sign=nxt;x+=sign*.05;self.assertLessEqual(abs(x),2.051)
  self.assertGreater(turns,3)
  self.assertNotIn('SetPosition(',self.code)
  self.assertIn('OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, speed)',self.code)
  self.assertIn('90 * m_MLADSLeanDemoSign',self.code)
  self.assertIn('m_MLADSLeanAmount = m_MLADSLeanDemoAmount',self.code)
  self.assertRegex(self.code,r'AnimSetFloat\(m_MLADSLeanDemoAimIK, (90 \* m_MLADSLeanDemoAmount|0)\)')
 def test_npc_ownership_and_cleanup(self):
  self.assertIn('if (GetGame().IsMultiplayer() || GetGame().GetPlayer() == this)',self.code)
  for method in ['OverrideMovementSpeed','OverrideMovementAngle','OverrideRaise']:self.assertIn(method+'(HumanInputControllerOverrideType.DISABLED',self.code)
  mission=(KIT/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
  self.assertIn('spawn + facing * 8',mission)
  self.assertIn('m_MLADSLeanNPC.MLADSLeanStartDemo()',mission)
  self.assertIn('m_MLADSLeanNPC.MLADSLeanStopDemo()',mission)
  self.assertIn('GetGame().ObjectDelete(m_MLADSLeanNPC)',mission)
  self.assertIn('MLADSLeanSettings.DemoActor = null',mission)
if __name__=='__main__':unittest.main()
