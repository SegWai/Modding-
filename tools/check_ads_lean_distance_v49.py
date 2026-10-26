"""Clean vanilla/custom calibration isolation and neutral-relative distance math."""
from pathlib import Path
import unittest,json,hashlib,re,sys,zipfile,tempfile
sys.dont_write_bytecode=True
from analyze_lean_distances_v49 import analyze,load
from package_ads_lean_runtime import runtime_files
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v48';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v49'
class DistanceCalibration(unittest.TestCase):
 def test_no_pose_graph_or_camera_changes(self):
  for p in ('WorkspaceSource/locomotion.agf','WorkspaceSource/player_main.agr','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo','LogicSource/Scripts/4_World/MLADSLeanCamera.c'):self.assertEqual((A/p).read_bytes(),(B/p).read_bytes())
  old=(A/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();new=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  i=new.index(' // Standing exposure calibration:');j=new.index(' // Camera-only readback.',i);new=new[:i]+new[j:]
  new=new.replace(' static bool DistanceNativeReference = false;\n','')
  for a,b in [('MLADSLEAN49','MLADSLEAN48'),('MLPOSE49','MLPOSE48'),('MLWALK49','MLWALK48'),('MLCAM49','MLCAM48')]:new=new.replace(a,b)
  self.assertEqual(new,old)
 def test_native_reference_loads_original_workspace_only(self):
  launch=(B/'Launch-Test.ps1').read_text();self.assertIn('if ($NativeReference) { $mods = @($logic) }',launch)
  self.assertIn('Profiles\\VanillaLean',launch);self.assertIn('MLADSLeanNativeReference.ChernarusPlus',launch)
  native=(B/'Missions/MLADSLeanNativeReference.ChernarusPlus/init.c').read_text();self.assertLess(native.index('DistanceNativeReference = true'),native.index('super.OnInit()'))
  self.assertIn('MLADSLeanSettings.Enabled = false;',native)
  self.assertNotIn('  MLADSLeanSpawnTarget();',native)
  self.assertNotIn('DemoKilled.Insert',native)
  self.assertIn('-NativeReference',(B/'Launch-Vanilla-Lean-Reference.cmd').read_text())
 def test_sampling_is_readonly_and_native_gate_is_off_custom_on(self):
  player=(B/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();s=player[player.index(' // Standing exposure calibration:'):player.index(' // Camera-only readback.')]
  for term in ('AnimSet','SetPosition','Override','SetADS','Enabled ='):self.assertNotIn(term,s)
  for term in ('m_MLADSLeanBound || m_MLADSLeanGate > 0.02','!m_MLADSLeanBound || m_MLADSLeanGate < 0.98','!IsRaised()','!IsWeaponRaiseCompleted()','distanceState.m_iMovement != 0','bone == -1','"LeftFoot"','"RightFoot"','"EyeLeft"','"EyeRight"'):self.assertIn(term,s)
  self.assertNotIn('bone < 0',s)
  keys=(B/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text()
  for term in ('m_ML49Samples < 20','m_ML49Stable < 0.5','m_ML49Interval < 0.05','m_ML49Done[state + 1]','setup != m_ML49Setup','head_x_min=','head_x_max=','root_ws=','duration_ms='):self.assertIn(term,keys)
  self.assertNotIn('MLADSLeanSettings.Enabled =',keys[keys.index(' protected void ML49ResetWindow()'):keys.index(' override void OnKeyRelease(')])
  self.assertNotRegex(keys,r'(?:m_ML49Sum\[\d\]|points\[\d\])\s*/') # no unsupported vector division
 def fixture(self,asymmetric=False,setup_custom='AK74_raised',include_custom=True):
  lines=[]
  for mode,base,left,right,setup in [('native',.02,.12,.18 if asymmetric else .12,'AK74_raised'),('custom',-.03,.20,.16,setup_custom)]:
   if mode=='custom' and not include_custom:continue
   sid=mode.upper();native='true' if mode=='native' else 'false';lines.append(f'[MLDIST49] SESSION id={sid} setup={setup} native_workspace={native}')
   for sign,extent in ((0,0),(-1,left),(1,right)):
    x=base+sign*extent
    line=f'[MLDIST49] RESULT session={sid} mode={mode} setup={setup} sign={sign} samples=20 duration_ms=950'
    line+=f' root_ws=<4440, 339, 10240> actor_ypr=<145, 0, 0> head_ms=<{x}, 1.6, 0> chest_ms=<{x*.7}, 1.2, 0> pelvis_ms=<0, .95, 0>'
    line+=' left_foot_ms=<-.2, .1, 0> right_foot_ms=<.2, .1, 0>'
    line+=f' eye_centre_ms=<{x}, 1.65, .05> head_x_min={x-.001} head_x_max={x+.001}'
    lines.append(line)
   lines.append(f'[MLDIST49] COMPLETE mode={mode} session={sid}')
  return '\n'.join(lines)
 def test_distances_use_each_runs_neutral_not_absolute_head_x(self):
  r=analyze([self.fixture()]);self.assertAlmostEqual(r['runs']['native']['head_extent_m']['left'],.12)
  self.assertAlmostEqual(r['runs']['native']['head_extent_m']['right'],.12)
  self.assertAlmostEqual(r['custom_minus_native_extent_m']['left'],.08)
  self.assertAlmostEqual(r['custom_minus_native_extent_m']['right'],.04)
  self.assertFalse(r['meaningful_native_asymmetry']);self.assertFalse(r['native_target_chosen'])
 def test_vanilla_asymmetry_is_reported_not_silently_replaced(self):
  r=analyze([self.fixture(asymmetric=True)]);self.assertTrue(r['meaningful_native_asymmetry'])
  self.assertAlmostEqual(r['native_left_right_asymmetry_m'],.06)
  self.assertAlmostEqual(r['shared_vanilla_midpoint_candidate_m'],.15)
  self.assertFalse(r['native_target_chosen'])
 def test_missing_or_mismatched_or_incomplete_runs_rejected(self):
  for text in (self.fixture(include_custom=False),self.fixture(setup_custom='AK74_optics'),self.fixture().replace('samples=20','samples=1'),self.fixture().replace('duration_ms=950','duration_ms=100')):
   with self.assertRaises(ValueError):analyze([text])
 def test_windows_zip_entry_separators_are_supported(self):
  fixture=self.fixture();cut=fixture.index('[MLDIST49] SESSION id=CUSTOM')
  with tempfile.TemporaryDirectory() as folder:
   archive=Path(folder)/'windows-logs.zip'
   with zipfile.ZipFile(archive,'w') as z:
    z.writestr(r'VanillaLean\script_native.log',fixture[:cut])
    z.writestr(r'LeanMosin\script_custom.log',fixture[cut:])
   report=load(archive)
   self.assertAlmostEqual(report['runs']['native']['head_extent_m']['right'],.12)
   self.assertAlmostEqual(report['runs']['custom']['head_extent_m']['left'],.20)
 def test_archive_and_collectors_are_runtime_only(self):
  for p,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():self.assertEqual(hashlib.sha256((B/p).read_bytes()).hexdigest(),h)
  with zipfile.ZipFile(R/'artifacts/MovementLab_ADS_Lean_Mosin_v49.zip') as z:
   self.assertIsNone(z.testzip());self.assertEqual(set(z.namelist()),{B.name+'/'+p for p in runtime_files(B)})
   for n in z.namelist():self.assertNotRegex(n.lower(),r'blender|\.blend|\.png|\.py$')
  collect=(B/'Collect-Logs.ps1').read_text();self.assertIn("@('LeanMosin','VanillaLean')",collect)
  self.assertIn("Select-Object -First 2",collect);self.assertIn('finally',collect)
  for p in ('Launch-Mosin-Lean-Test.cmd','Launch-Vanilla-Lean-Reference.cmd'):self.assertNotRegex((B/p).read_text().lower(),r'\bchoice\b')
if __name__=='__main__':unittest.main()
