"""Regression checks: release only the custom standing lean from native foot pinning."""
from pathlib import Path
import unittest,re,json,sys
sys.dont_write_bytecode=True
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v2'
NEW=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v3'
class FootPinningRegression(unittest.TestCase):
 def test_working_control_template_unchanged(self):
  self.assertEqual((OLD/'WorkspaceSource/player_main.agr').read_bytes(),(NEW/'WorkspaceSource/player_main.agr').read_bytes())
 def test_only_idle_entry_and_new_blend_change(self):
  a=newnodes((OLD/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((NEW/'WorkspaceSource/locomotion.agf').read_text())
  self.assertEqual(set(b)-set(a),{'MLADSLeanFootIKBlend'})
  for name,body in a.items():
   if name not in ['StanceMaster','IdleRas']:self.assertEqual(body,b[name],name)
  self.assertIn('Child "MLADSLeanFootIKBlend"',b['StanceMaster'])
  self.assertIn('Child0 "IdleRasIK"',b['MLADSLeanFootIKBlend'])
  self.assertIn('Child1 "IdleRasSTM"',b['MLADSLeanFootIKBlend'])
 def test_gate_lean_and_stance_endpoints(self):
  n=newnodes((NEW/'WorkspaceSource/locomotion.agf').read_text())['MLADSLeanFootIKBlend'];expr=re.search(r'BlendWeight "([^"]+)"',n)[1]
  def weight(lean,gate,stance):return eval(expr,{'__builtins__':{}},{'clamp':lambda v,a,b:max(a,min(b,v)),'abs':abs,'Lean':lean,'MLADSLeanGate':gate,'Stance':stance})
  for lean in [-1,-.5,0,.5,1]:
   for stance in [0,1,2]:self.assertEqual(weight(lean,0,stance),0)
  for gate in [0,.5,1]:self.assertEqual(weight(0,gate,0),0)
  for stance in [1,2]:
   for lean in [-1,-.5,.5,1]:self.assertEqual(weight(lean,1,stance),0)
  self.assertEqual(weight(-1,1,0),1);self.assertEqual(weight(1,1,0),1);self.assertEqual(weight(.5,1,0),.5)
 def test_bypassed_solver_only_has_foot_chains(self):
  nodes=newnodes((NEW/'WorkspaceSource/locomotion.agf').read_text());native=nodes['IdleRasIK']
  self.assertIn('Child "IdleRasSTM"',native)
  self.assertEqual(re.findall(r'IkTarget "([^"]+)"',native),['LFootIKTarget','RFootIKTarget'])
  self.assertNotIn('Hand',native)
 def test_pose_corrections_unchanged(self):
  a=json.loads((OLD/'Pose-Spec.json').read_text());b=json.loads((NEW/'Pose-Spec.json').read_text())
  self.assertEqual(a['corrections'],b['corrections']);self.assertEqual(a['math_reconstruction_error'],b['math_reconstruction_error'])
 def test_activation_logic_only_version_labels_change(self):
  for path in (OLD/'LogicSource').rglob('*.c'):
   text=(NEW/path.relative_to(OLD)).read_text().replace('MLADSLEAN3','MLADSLEAN2').replace('lean v3','lean v2')
   self.assertEqual(path.read_text(),text,path.name)
if __name__=='__main__':unittest.main()
