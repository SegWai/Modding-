"""First-person camera roll isolation and continuous left-walk export contracts."""
from pathlib import Path
import sys,re,json,math,unittest,importlib.util,hashlib,tempfile,zipfile
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v45';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v46'
spec=importlib.util.spec_from_file_location('leftwalk',B/'BlenderTools/import_left_walk.py');walk=importlib.util.module_from_spec(spec);spec.loader.exec_module(walk)
class FirstPersonAndWalk(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.camera=(B/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();cls.player=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();cls.keys=(B/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
 def test_approved_body_workspace_byte_identical(self):
  for f in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo'):
   self.assertEqual((A/f).read_bytes(),(B/f).read_bytes())
  a=(A/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();b=self.player
  start=b.index(' // Camera-only readback.');end=b.index(' // Read-only calibration',start)
  b=b[:start]+b[end:];b=b.replace(' static float FirstPersonRoll;\n static string FirstPersonRollCamera = "none";\n','')
  b=b.replace('MLADSLEAN46','MLADSLEAN45').replace('MLPOSE46','MLPOSE45')
  self.assertEqual(a,b)
 def test_camera_keeps_super_projection_and_updates_basis_only(self):
  c=self.camera
  self.assertEqual(c.count('super.OnUpdate(pDt, pOutResult);'),2)
  self.assertIn('modded class DayZPlayerCamera1stPerson',c);self.assertIn('modded class DayZPlayerCameraIronsights',c)
  self.assertNotIn('modded class DayZPlayerCamera3rdPerson',c);self.assertNotIn('modded class DayZPlayerCameraOptics',c) # inherited hook once
  self.assertIn('MatrixMultiply3(basis, localRoll, tilted)',c)
  for i in range(3):self.assertIn(f'result.m_CameraTM[{i}] = tilted[{i}];',c)
  for term in ('m_CameraTM[3] =','m_fShootFromCamera =','m_fUseHeading =','m_iDirectBoneMode =','m_fFovAbsolute =','AnimSet','Override','SetADS'):self.assertNotIn(term,c)
  self.assertIn('MLADSLeanFirstPersonRollTarget(false)',c);self.assertIn('MLADSLeanFirstPersonRollTarget(true)',c)
 def test_smoothed_roll_bounded_and_nonzero_from_real_native_heads(self):
  samples=json.loads((R/'ads-lean-test/Blender_Native_Lean_v43/Native-Captures.json').read_text())
  for cid in ('60375_true','67091_true'):
   up=samples[cid]['bones']['Head']['0'];target=math.degrees(math.atan2(up[0],up[1]));self.assertGreater(abs(target),1)
   x=0
   for _ in range(60):
    new=x+(target-x)*((1/60)/(.18+1/60));self.assertGreaterEqual(new,min(x,target));self.assertLessEqual(new,max(x,target));x=new
   self.assertLess(abs(x-target),.2)
  # Local Z rotation keeps forward and translation invariant for any base rotation.
  import captured_pose_bridge as pose
  for angles in ((0,0,0),(.3,-.5,.8)):
   base=pose.rotation(*angles)
   for roll in (-.6,-.2,.2,.6):
    out=pose.multiply(base,pose.rotation(0,0,roll))
    for i in range(3):self.assertAlmostEqual(base[i][2],out[i][2])
    self.assertNotEqual([r[:2] for r in base[:3]],[r[:2] for r in out[:3]])
  self.assertIn('boundedDt / (0.18 + boundedDt)',self.camera)
 def test_camera_getter_readonly_scoped_and_valid_signed_ids(self):
  p=self.player;start=p.index(' float MLADSLeanFirstPersonRollTarget(');end=p.index(' bool MLADSLeanLeftWalkCaptureReady()',start);s=p[start:end]
  for term in ('!MLADSLeanSettings.Enabled','!m_MLADSLeanBound','!IsAlive()','IsUnconscious()','!IsRaised()','m_MLADSLeanGate < 0.001','"AK74"','"Mosin9130"','rollHead == -1','Math.Atan2','rollHeadTM[0]','weaponWorld[1]'):self.assertIn(term,s)
  for term in ('AnimSet','SetPosition','Override','SetADS','GetCurrentCamera'):self.assertNotIn(term,s)
  self.assertNotIn('rollHead < 0',s)
 def test_recorder_only_continuous_left_walking_pass(self):
  s=self.player[self.player.index(' bool MLADSLeanLeftWalkCaptureReady()'):self.player.index(' // Read-only calibration')]
  for term in ('!m_MLADSLeanDemo','!m_MLADSLeanDemoReady','m_MLADSLeanAmount > -0.98','m_MLADSLeanDemoSign >= 0','m_MLADSLeanGate < 0.98','m_MLADSLeanMoveBlend < 0.98','clipState.m_iMovement != 1','STANCEIDX_ERECT','MLADSLeanCapturePose();'):self.assertIn(term,s)
  for term in ('AnimSet','SetPosition','Override','SetADS'):self.assertNotIn(term,s)
  for term in ('m_MLADSClipFrames >= 36','0.041666667','now - m_MLADSClipLastTime > 250','m_MLADSPoseStable < 0.4','m_MLADSClipFrames = 0;','m_MLADSClipSession = "";','nominal_fps=24'):self.assertIn(term,self.keys)
 def test_parser_rejects_sparse_and_incomplete_or_wrong_direction(self):
  fixture=json.loads((R/'ads-lean-test/Blender_Native_Lean_v43/Native-Captures.json').read_text())['60375_true']
  def make(count=36,complete=True,lean=-1,gap=42):
   lines=[]
   for i in range(count):
    cid=f'{1000+i*gap}_true';lines.append(f'[MLWALK46] FRAME session=TEST frame={i} time_ms={1000+i*gap}')
    lines.append(f'[MLPOSE46] BEGIN id={cid} demo=true lean={lean} move_blend=1 gate=1 raised=false')
    for kind,items in [('ACTOR',{'':fixture['actor']}),('BONE',fixture['bones']),('WEAPON',{'':fixture['weapon']})]:
     for name,rows in items.items():
      for row,v in rows.items():lines.append(f'[MLPOSE46] {kind} id={cid} '+(f'name={name} ' if name else '')+f'row={row} value=<{v[0]}, {v[1]}, {v[2]}>')
    lines.append(f'[MLPOSE46] END id={cid} bones=114')
   if complete:lines.append('[MLWALK46] COMPLETE session=TEST frames=36 nominal_fps=24')
   return '\n'.join(lines)
  good=make();self.assertEqual(len(walk.parse_log(good)['frames']),36)
  for bad in (make(count=3),make(complete=False),make(lean=1),make(gap=251),good.replace('name=RightHand row=0','name=MISSING row=0')):
   with self.assertRaises(ValueError):walk.parse_log(bad)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'logs.zip'
   with zipfile.ZipFile(p,'w') as z:z.writestr('script_test.log',good);z.writestr('DayZ.RPT',good) # no duplicate RPT import
   self.assertEqual(len(walk.load_capture(p)['frames']),36)
 def test_package_hashes_direct_helpers_and_template(self):
  for path,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((B/path).read_bytes()).hexdigest(),h)
  self.assertTrue((B/'BlenderTools/Lean_Template.blend').is_file())
  helper=(B/'Build-Left-Walk-Blender.ps1').read_text();self.assertIn('--python-exit-code 1',helper);self.assertIn('yyyyMMdd_HHmmss',helper)
  for p in ('Launch-Mosin-Lean-Test.cmd','Build-Left-Walk-Blender.cmd'):self.assertNotRegex((B/p).read_text().lower(),r'\bchoice\b')
if __name__=='__main__':unittest.main()
