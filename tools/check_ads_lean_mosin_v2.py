"""Offline regression checks for the v1 log-confirmed missing control failure.
No DayZ native compilation or playback is claimed by these checks.
"""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v1'
NEW=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v2'

def control_schema(text,name):
 m=re.search(r'\bAnimSrcGCTVarFloat\s+'+re.escape(name)+r'\s*\{([^{}]*)\}',text)
 if not m:raise ValueError('Control missing: '+name)
 lines=[x.strip() for x in m[1].splitlines() if x.strip()]
 if len(lines)!=3:raise ValueError('Expected each control property on a separate native-format line')
 parsed={}
 for line in lines:
  p=re.fullmatch(r'(DefaultValue|MinValue|MaxValue)\s+(-?[0-9]+(?:\.[0-9]+)?)',line)
  if not p or p[1] in parsed:raise ValueError('Invalid/duplicate control property')
  parsed[p[1]]=float(p[2])
 if set(parsed)!={'DefaultValue','MinValue','MaxValue'}:raise ValueError('Incomplete control')
 if not parsed['MinValue']<=parsed['DefaultValue']<=parsed['MaxValue']:raise ValueError('Out-of-range default')
 return parsed

class MissingControlRegression(unittest.TestCase):
 def test_v1_inline_definition_fails_new_native_format_check(self):
  with self.assertRaises(ValueError):control_schema((OLD/'WorkspaceSource/player_main.agr').read_text(),'MLADSLeanGate')
 def test_v2_controls_and_template_identity(self):
  old=(OLD/'WorkspaceSource/player_main.agr').read_text();new=(NEW/'WorkspaceSource/player_main.agr').read_text()
  self.assertEqual(control_schema(new,'MLADSLeanGate')['DefaultValue'],0)
  self.assertEqual(control_schema(new,'MLADSLeanCanary')['DefaultValue'],.731)
  ids=[re.search(r'ControlTemplate AnimSrcGCT "\{([0-9A-F]{16})\}"',s)[1] for s in [old,new]]
  self.assertNotEqual(*ids)
  graph=(NEW/'WorkspaceSource/locomotion.agf').read_text()
  expressions=re.findall(r'Expression "([^"]*)"',graph)
  for expression in expressions:
   for name in re.findall(r'\bMLADSLean[A-Za-z0-9_]*\b',expression):control_schema(new,name)
 def test_pose_graph_unchanged_for_isolated_registration_fix(self):
  self.assertEqual((OLD/'WorkspaceSource/locomotion.agf').read_bytes(),(NEW/'WorkspaceSource/locomotion.agf').read_bytes())
  self.assertEqual(json.loads((OLD/'Pose-Spec.json').read_text())['corrections'],json.loads((NEW/'Pose-Spec.json').read_text())['corrections'])
 def test_actual_binding_guard_accepts_zero_but_rejects_fallback_aliases(self):
  text=(NEW/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  expression=re.search(r'\bm_MLADSLeanBound = ([^;]+);',text)[1].replace('&&',' and ')
  names=['m_MLADSLeanGateVar','m_MLADSLeanCanaryVar','m_MLADSLeanNativeLeanVar','m_MLADSLeanNativeMoveVar']
  for ids,expected in [([0,1,8,2],True),([2,3,0,1],True),([0,0,0,0],False),([-1,1,8,2],False),([0,2,8,2],False)]:
   with self.subTest(ids=ids):self.assertEqual(eval(expression,{'__builtins__':{}},dict(zip(names,ids))),expected)
  self.assertRegex(text,r'if \(m_MLADSLeanBound\)\s+AnimSetFloat')
 def test_debug_dependency_is_offline_diag_only(self):
  text=(NEW/'LogicSource/Scripts/4_World/MLADSLeanDiagPlugins.c').read_text()
  self.assertIn('#ifdef DIAG_DEVELOPER',text)
  self.assertIn('!GetGame().IsMultiplayer() && !GetGame().IsDebug()',text)
  for plugin in ['PluginInventoryDebug','PluginConfigDebugProfile']:
   self.assertIn('RegisterPlugin("'+plugin+'", true, true);',text)
  self.assertNotIn('RegisterPluginDebug(',text)
 def test_existing_project_root_and_new_status_logging(self):
  self.assertIn('F:\\DayZProjects',(NEW/'Launch-Test.ps1').read_text())
  player=(NEW/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
  self.assertIn('[MLADSLEAN2]',player);self.assertIn('m_MLADSLeanNextReport',player)
  self.assertIn('KeyCode.KC_F9',(NEW/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text())

if __name__=='__main__':unittest.main()
