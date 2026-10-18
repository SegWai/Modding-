from pathlib import Path
import json,re,unittest
from captured_pose_bridge import fragment,ordered
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'hud-icons-test/MovementLabLocomotion_v105'
TEST=ROOT/'hud-icons-test/MovementLabLocomotion_v106'

class IntegrationTests(unittest.TestCase):
    def test_fragment_matches_spec_and_gate_preserves_normal_graph(self):
        spec=json.loads((TEST/'Captured-Pose-Spec.json').read_text())
        generated=fragment(spec['parents'])
        self.assertEqual(len(spec['ordered_bones']),91)
        self.assertEqual(spec['ordered_bones'],ordered(spec['parents']))
        old=(BASE/'WorkspacePatches/master.agf').read_text()
        wrapper='''    AnimSrcNodeBlend MasterControl {
     BlendWeight "MLCapturedPoseActive"
     Child0 "MovementLabOriginalMasterControl"
     Child1 "%s"
     OptimizeMin 1
     OptimizeMax 1
    }
'''%generated['output_node']
        expected=old.replace('AnimSrcNodeBlend MasterControl {','AnimSrcNodeBlend MovementLabOriginalMasterControl {',1).replace('   Nodes {','   Nodes {\n'+wrapper+generated['nodes']+'\n',1)
        self.assertEqual(expected,(TEST/'WorkspacePatches/master.agf').read_text())
        control='   AnimSrcGCTVarFloat MLCapturedPoseActive { DefaultValue 0 MinValue 0 MaxValue 1 }\n'
        expected=(BASE/'WorkspacePatches/player_main.agr').read_text().replace('  Variables {','  Variables {\n'+control+generated['controls']+'\n',1)
        self.assertEqual(expected,(TEST/'WorkspacePatches/player_main.agr').read_text())

    def test_graph_nodes_resolve_and_identifiers_unique(self):
        graph=(TEST/'WorkspacePatches/master.agf').read_text()
        names=re.findall(r'AnimSrcNode\w+\s+(\w+)\s*\{',graph)
        self.assertEqual(len(names),len(set(names)))
        generated=fragment(json.loads((TEST/'Captured-Pose-Spec.json').read_text())['parents'])
        declared=set(re.findall(r'AnimSrcNodeProcTransform\s+(\w+)',generated['nodes']))|{'APoseSrc'}
        for child in re.findall(r'Child "([^"]+)"',generated['nodes']):self.assertIn(child,declared)
        self.assertEqual(len(re.findall(r'AnimSrcGCTVarFloat ',generated['controls'])),546)
        for path in ['master.agf','player_main.agr']:
            text=(TEST/'WorkspacePatches'/path).read_text()
            text=re.sub(r'"(?:\\.|[^"\\])*"','""',text)
            self.assertEqual(text.count('{'),text.count('}'))

    def test_capture_before_native_death_and_guarded_activation(self):
        world=TEST/'StartGateSource/Scripts/4_World'
        capture=(world/'MovementLabRangeInfected.c').read_text()
        self.assertLess(capture.index('DeathPose.ReadInfected(this)'),capture.index('super.EEKilled(killer)'))
        helper=(world/'MovementLabConfiguredCorpse.c').read_text()
        self.assertNotIn('MovementLabPrimeDeathPose',helper)
        self.assertNotIn('ForceStance(',helper)
        self.assertLess(helper.index('if (!m_PoseBridge.Step())'),helper.index('PhysicsSetRagdoll(true)'))
        bridge=(world/'MovementLabCapturedPoseBridge.c').read_text()
        self.assertIn('positionError <= 0.01 && basisError <= 0.035',bridge)
        self.assertNotIn('SetBoneGlobal(',bridge)
        self.assertNotIn('SetBoneMatrix(',bridge)
        self.assertIn('m_Actor.AnimSetFloat',bridge)

    def test_native_declarations(self):
        sdk=Path('/tmp/dayz-script-diff/scripts')
        math=(sdk/'1_core/proto/enmath3d.c').read_text()
        for name in ['MatrixInvMultiply4','MatrixMultiply4','MatrixInverse4']:self.assertIn(name+'(',math)
        self.assertRegex((sdk/'3_game/dayzplayer.c').read_text(),r'AnimSetFloat\s*\(')
        self.assertIn('BindVariableFloat',(sdk/'3_game/human.c').read_text())

    def test_player_and_other_fixture_source_unchanged(self):
        for path in ['Missions/MovementLabMovementLogic.ChernarusPlus/init.c','StartGateSource/Scripts/4_World/MovementLabRangeNPC.c','StartGateSource/Scripts/4_World/MovementLabPoseCorrections.c']:
            self.assertEqual((BASE/path).read_bytes(),(TEST/path).read_bytes())
        for p in (BASE/'WorkspacePatches').rglob('*'):
            if p.is_file() and p.name not in ('master.agf','player_main.agr'):
                self.assertEqual(p.read_bytes(),(TEST/'WorkspacePatches'/p.relative_to(BASE/'WorkspacePatches')).read_bytes())

if __name__=='__main__':unittest.main(verbosity=2)
