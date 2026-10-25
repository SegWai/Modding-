"""Confirmed screen-left shoulder shift before weapon IK, safe shared comparison control."""
import sys,unittest,re,json,hashlib,math
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v24'
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v23'
base.KIT=KIT
class ShoulderPlacementTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.g=(KIT/'WorkspaceSource/locomotion.agf').read_text();cls.n=newnodes(cls.g)
  cls.old=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text())
  cls.code=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
 def test_shift_is_before_unchanged_weapon_ik(self):
  self.assertIn('Child "ML24_MarkedShoulderOffset"',self.n['NormalWeaponIK'])
  self.assertIn('Child "AimObstructionT"',self.n['ML24_MarkedShoulderOffset'])
  self.assertEqual(self.n['NormalWeaponIK'].replace('Child "ML24_MarkedShoulderOffset"','Child "AimObstructionT"'),self.old['NormalWeaponIK'])
  self.assertEqual({n for n in self.old if not n.startswith('{') and self.n[n]!=self.old[n]},{'NormalWeaponIK'})
  self.assertEqual({n for n in self.n if n not in self.old and not n.startswith('{')},{'ML24_MarkedShoulderOffset'})
 def test_both_arm_roots_move_together_and_head_legs_are_outside_subtrees(self):
  node=self.n['ML24_MarkedShoulderOffset']
  items=re.findall(r'Bone "([^"]+)"\s+Axis X\s+Space Model\s+Op Translate\s+Amount ([-+0-9.eE]+)',node)
  self.assertEqual(dict((b,float(v)) for b,v in items),{'RightShoulder':.08,'LeftShoulder':.08})
  parents=json.loads((KIT/'Pose-Snapshot.json').read_text())['parents']
  def shifted(b):
   while b:
    if b in ['RightShoulder','LeftShoulder']:return True
    b=parents[b]
   return False
  for b in ['RightArm','LeftArm','RightHand','LeftHand']:self.assertTrue(shifted(b),b)
  for b in ['Head','Neck','Pelvis','LeftFoot','RightFoot']:self.assertFalse(shifted(b),b)
 def test_confirmed_screen_left_direction_and_scope(self):
  # Front-facing NPC: his local-right axis is opposite the viewer's local-right.
  heading=math.radians(145);npc_heading=heading+math.pi
  viewer_right=(math.cos(heading),-math.sin(heading))
  npc_right=(math.cos(npc_heading),-math.sin(npc_heading))
  self.assertAlmostEqual(sum(a*b for a,b in zip(viewer_right,npc_right)),-1)
  expr=re.search(r'Expression "([^"]+)"',self.n['ML24_MarkedShoulderOffset'])[1]
  for amount,gate,speed,scale,wanted in [(1,1,1,1,1),(-1,1,1,1,0),(1,1,0,1,0),(1,0,1,1,0),(1,1,1,0,0),(.5,1,.5,1,.25)]:
   self.assertEqual(base.expression(expr,{'MLADSLeanAmount':amount,'MLADSLeanGate':gate,'MovementSpeed':speed,'TestFloat':scale,'clamp':lambda x,a,b:max(a,min(b,x))}),wanted)
  self.assertNotIn('MLADSLeanCanary',expr)
 def test_registered_control_safe_binding_and_command_handler_context(self):
  self.assertEqual((KIT/'WorkspaceSource/player_main.agr').read_bytes(),(OLD/'WorkspaceSource/player_main.agr').read_bytes())
  agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
  self.assertRegex(agr,r'AnimSrcGCTVarFloat TestFloat \{\s+DefaultValue 0\s+MinValue 0\s+MaxValue 1')
  expressions=re.findall(r'm_MLADSLeanWeaponShiftBound = ([^;]+);',self.code)
  self.assertEqual(len(expressions),6)
  names=['m_MLADSLeanGateVar','m_MLADSLeanCanaryVar','m_MLADSLeanAmountVar','m_MLADSLeanNativeLeanVar','m_MLADSLeanNativeMoveVar']
  for ids,new_id,wanted in [([0,1,2,21,3],31,True),([0,1,2,21,3],0,False),([0,1,2,21,3],-1,False),([1,2,3,4,5],0,True)]:
   env=dict(zip(names,ids));env['m_MLADSLeanWeaponShiftVar']=new_id
   for expr in expressions:env['m_MLADSLeanWeaponShiftBound']=base.expression(expr,env)
   self.assertEqual(env['m_MLADSLeanWeaponShiftBound'],wanted)
  c=self.code.split('override void CommandHandler',1)[1]
  self.assertLess(c.index('super.CommandHandler('),c.index('AnimSetFloat(m_MLADSLeanWeaponShiftVar, shoulderShiftScale)'))
  self.assertIn('if (m_MLADSLeanBound && m_MLADSLeanWeaponShiftBound)',c)
 def test_shared_f5_comparison_and_readonly_diagnostics(self):
  keys=(KIT/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
  self.assertIn('static bool WeaponShoulderOffset = true;',self.code)
  self.assertIn('if (key == KeyCode.KC_F5 && !m_MLADSLeanF5Down)',keys)
  self.assertIn('MLADSLeanSettings.WeaponShoulderOffset = !MLADSLeanSettings.WeaponShoulderOffset;',keys)
  self.assertIn('if (key == KeyCode.KC_F5)\n   m_MLADSLeanF5Down = false;',keys)
  self.assertIn('WorldToModel(held.GetPosition())',self.code)
  self.assertIn('weapon_position_ms=',self.code)
  for line in self.code.splitlines():
   if 'status +=' in line or 'string status =' in line:self.assertLessEqual(line.count('+'),2)
 def test_range_behaviour_and_pose_offsets_preserved(self):
  for path in ['LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
   self.assertEqual((KIT/path).read_text().replace('MLADSLEAN24','MLADSLEAN23').replace('lean v24','lean v23'),(OLD/path).read_text())
  old_code=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  self.assertEqual(self.code.split('protected bool m_MLADSLeanRangeTarget;',1)[1].replace('MLADSLEAN24','MLADSLEAN23'),old_code.split('protected bool m_MLADSLeanRangeTarget;',1)[1])
  for path in ['Pose-Snapshot.json','Static-Pose-Snapshot.json','Mode-Coverage.json']:
   self.assertEqual((KIT/path).read_bytes(),(OLD/path).read_bytes())
 def test_package_integrity_and_no_launcher_menu(self):
  d=json.loads((KIT/'validation.json').read_text())
  for p,h in d['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('F:\\DayZProjects',(KIT/'Launch-Test.ps1').read_text())
  self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b|choose [12]|echo [12]\.')
  self.assertIn('Mosin-Lean-v24-Logs',(KIT/'Collect-Logs.ps1').read_text())
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(base.ExpandedLeanTests)
 suite.addTests(loader.loadTestsFromTestCase(ShoulderPlacementTests));return suite
if __name__=='__main__':unittest.main()
