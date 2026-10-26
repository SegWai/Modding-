"""Preserve custom raised first-person endpoints and verify transition-rate changes."""
import sys,unittest,json,re,hashlib,math
sys.dont_write_bytecode=True
from pathlib import Path
import check_ads_lean_mosin_v5 as base
from check_ads_lean_mosin_v40 import ActivationScopeTests
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v41';OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v39';base.KIT=KIT
sys.path.insert(0,str(KIT))
from build_pbos import read_pbo
class TransitionScopeTests(ActivationScopeTests):
 def test_npc_actual_endpoint_conditions_and_native_input(self):
  original=self.code
  try:
   # The source assignment is now a filter target, tracked exactly at NPC's slower rate.
   self.code=original.replace('m_MLADSLeanLeanRequested = m_MLADSLeanDemoAmount','m_MLADSLeanAmount = m_MLADSLeanDemoAmount')
   super().test_npc_actual_endpoint_conditions_and_native_input()
  finally:self.code=original
 def test_crouch_legs_and_walking_steps_remain_native(self):
  original=self.nodes['MLADSLeanFootIKBlend']
  try:
   self.nodes['MLADSLeanFootIKBlend']=original.replace('MLADSLeanMoveBlend','clamp(MovementSpeed, 0.0, 1.0)')
   super().test_crouch_legs_and_walking_steps_remain_native()
  finally:self.nodes['MLADSLeanFootIKBlend']=original
class SmoothRaisedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();cls.n=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text());cls.a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text())
 def test_raised_custom_mode_default_on_without_camera_restriction_or_forced_ads(self):
  self.assertIn('static bool Inspection = true;',self.c)
  self.assertIn('bool inspectionAllowed = MLADSLeanSettings.Inspection;',self.c)
  self.assertNotIn('inspectionAllowed = inspectionAllowed && cameraName',self.c)
  self.assertIn('raised && ready && (aiming || inspectionAllowed)',self.c)
  self.assertIn('bool aiming = IsInIronsights() || IsInOptics();',self.c)
  self.assertNotIn('m_CameraTM',self.c)
  target=re.search(r'bool target = ([^;]+);',self.c)[1]
  for a,b in {'MLADSLeanSettings.Enabled':'enabled','IsAlive()':'alive','IsUnconscious()':'unconscious','state.m_iMovement':'movement','DayZPlayerConstants.COMMANDID_MOVE':'move_id'}.items():target=target.replace(a,b)
  for camera in ['DayZPlayerCamera1stPerson','DayZPlayerCamera3rdPerson']:
   for nativeADS in [False,True]:
    env=dict(actorReady=True,m_MLADSLeanBound=True,enabled=True,alive=True,unconscious=False,mosin=True,supportedStance=True,movement=1,pCurrentCommandID=7,move_id=7,raised=True,ready=True,aiming=nativeADS,inspectionAllowed=True,cameraName=camera)
    self.assertTrue(base.expression(target,env))
  keys=(KIT/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();self.assertIn('Custom raised-weapon pose ON in first and third person.',keys)
 def test_approved_pose_geometry_native_clips_and_full_endpoints_preserved(self):
  self.assertEqual(set(self.n),set(self.a))
  for name,old in self.a.items():
   new=self.n[name]
   if not name.startswith('ML'):
    self.assertEqual(old,new,name);continue
   self.assertEqual(re.findall(r'Amount [-\d.eE]+',old),re.findall(r'Amount [-\d.eE]+',new),name)
   expected=old.replace('clamp(MovementSpeed, 0.0, 1.0)','MLADSLeanMoveBlend')
   if name=='ML33_FinalGripIK':expected=expected.replace('BlendInTime 0.08','BlendInTime 0.22').replace('BlendOutTime 0.08','BlendOutTime 0.22')
   self.assertEqual(expected,new,name)
   exprs=lambda s:re.findall(r'(?:Expression|BlendWeight|WeightAim|WeightPrimaryChain|WeightSecondaryChain) "([^\"]+)"',s)
   for oldexpr,newexpr in zip(exprs(old),exprs(new)):
    for lean in [-1,0,1]:
     for move in [0,.4,1]:
      env=dict(MLADSLeanAmount=lean,MLADSLeanGate=1,MovementSpeed=move,MLADSLeanMoveBlend=move,MLADSLeanWeaponShift=1,MLADSLeanHeightLift=.08,Stance=0,Lean=lean,LeanForward=0,clamp=lambda x,a,b:max(a,min(b,x)),abs=abs)
      # Only compare expressions touched by movement smoothing.
      if 'MLADSLeanMoveBlend' in newexpr:self.assertEqual(base.expression(oldexpr,env),base.expression(newexpr,env),(name,lean,move))
 def test_actual_scalar_smoothing_is_bounded_and_reaches_same_target(self):
  c=self.c
  class M:
   Clamp=staticmethod(lambda x,a,b:max(a,min(b,x)))
   Min=staticmethod(min);Max=staticmethod(max)
  def update(kind,current,target,dt):
   if kind=='lean':field='m_MLADSLeanAmount';requested='m_MLADSLeanLeanRequested';step='leanVisualStep'
   else:field='m_MLADSLeanMoveBlend';requested='moveVisualTarget';step='moveVisualStep'
   env={'pDt':dt,'Math':M,field:current,requested:target}
   expr=re.search(r'float '+step+r' = ([^;]+);',c)[1];env[step]=base.expression(expr,env)
   formulas=re.findall(field+r' = (Math\.(?:Min|Max)\([^;]+);',c)
   self.assertEqual(len(formulas),2)
   return base.expression(formulas[0] if current<target else formulas[1],env)
  for dt in [1/120,1/48,1/30,.2]:
   for kind,target in [('lean',1),('lean',-1),('move',1)]:
    value=0;previous=0
    for i in range(math.ceil(1/dt)):
     value=update(kind,value,target,dt)
     self.assertLessEqual(abs(value-previous),min(dt,.05)/(.18 if kind=='lean' else .2)+1e-9)
     self.assertLessEqual(abs(value),1);previous=value
    self.assertAlmostEqual(value,target)
  # Existing NPC0.20s-per-unit lean remains unchanged by the faster0.18s filter.
  value=0
  for i in range(20):
   target=max(-1,-(i+1)*.02/.2);value=update('lean',value,target,.02);self.assertAlmostEqual(value,target)
  value=1
  for i in range(25):value=update('lean',value,-1,.02)
  self.assertAlmostEqual(value,-1)
 def test_safe_new_registered_input_and_command_handler_only_writes(self):
  agr=(KIT/'WorkspaceSource/player_main.agr').read_text();old=(OLD/'WorkspaceSource/player_main.agr').read_text()
  self.assertEqual(re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr)[:-1],re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',old))
  self.assertRegex(agr,r'AnimSrcGCTVarFloat MLADSLeanMoveBlend \{\s+DefaultValue 0\s+MinValue 0\s+MaxValue 1')
  for other in ['m_MLADSLeanGateVar','m_MLADSLeanCanaryVar','m_MLADSLeanAmountVar','m_MLADSLeanNativeLeanVar','m_MLADSLeanNativeMoveVar','m_MLADSLeanWeaponShiftVar','m_MLADSLeanHeightVar']:self.assertIn('m_MLADSLeanMoveBlendVar != '+other,self.c)
  handler=self.c.split('override void CommandHandler',1)[1].split('protected void MLADSLeanCalibrateStandingHeight',1)[0]
  self.assertLess(handler.index('super.CommandHandler('),handler.index('AnimSetFloat(m_MLADSLeanMoveBlendVar, m_MLADSLeanMoveBlend)'))
  self.assertIn('movementInput.GetMovement(movementRequest, movementDirection);',handler)
 def test_range_and_height_controller_preserved_and_small_diagnostics(self):
  old=(OLD/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  self.assertEqual(old.split('protected bool m_MLADSLeanRangeTarget;',1)[1].replace('MLADSLEAN39','MLADSLEAN41'),self.c.split('protected bool m_MLADSLeanRangeTarget;',1)[1])
  oldheight=old.split('// Height correction is part of this shared actor graph',1)[1].split('// HumanCommandWeapons.SetADS',1)[0]
  newheight=self.c.split('// Height correction is part of this shared actor graph',1)[1].split('// HumanCommandWeapons.SetADS',1)[0]
  self.assertEqual(oldheight,newheight)
  for line in self.c.splitlines():
   if any(s in line for s in ['status +=','transition +=','string transition =']):self.assertLessEqual(line.count('+'),2)
  self.assertIn('visual_transition demo=',self.c)
 def test_correct_packed_resource_and_hashes(self):
  _,entries=read_pbo((KIT/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes());self.assertEqual(entries['MLADSLeanLocomotion_v41.agf'],(KIT/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertIn(b'MLADSLeanLocomotion_v41.agf',entries['player_main.agr'])
  for p,h in json.loads((KIT/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((KIT/p).read_bytes()).hexdigest(),h)
  self.assertIn('Mosin-Lean-v41-Logs',(KIT/'Collect-Logs.ps1').read_text());self.assertNotRegex((KIT/'Launch-Mosin-Lean-Test.cmd').read_text().lower(),r'\bchoice\b')
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(TransitionScopeTests);suite.addTests(loader.loadTestsFromTestCase(SmoothRaisedTests));return suite
if __name__=='__main__':unittest.main()
