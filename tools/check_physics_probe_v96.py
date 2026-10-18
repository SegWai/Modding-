from pathlib import Path
import re
import unittest
from analyze_physics_probe import analyze

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'hud-icons-test/MovementLabLocomotion_v93'
TEST=ROOT/'hud-icons-test/MovementLabLocomotion_v96'


def trace(kind,event,alive,bones,present,ragdoll=None,complete=True):
    prefix=f'[MLPHY96] type={kind} event={event} t=1000 '
    text=prefix+f'stage=begin alive={alive}\n'
    if ragdoll is not None:text+=prefix+f'stage=human ragdoll={ragdoll}\n'
    text+=prefix+'stage=before_GetPhysics\n'
    if complete:text+=prefix+f'stage=complete root=present bones={bones} sampled={bones} present={present} dynamic={present} kinematic=0\n'
    return text


class ProbeTests(unittest.TestCase):
    def test_no_false_success_without_logs(self):
        self.assertIn('No v96',analyze('ordinary log')['verdict'])

    def test_require_human_physics_positive_control(self):
        text=trace('Human','human_death_now',0,11,11,ragdoll=False)+trace('Zombie','infected_death_now',0,0,0)
        self.assertIn('Incomplete',analyze(text)['verdict'])

    def test_distinct_controller_evidence(self):
        text=trace('Human','human_death_now',0,11,11,ragdoll=True)+trace('Zombie','infected_death_now',0,0,0)
        result=analyze(text)
        self.assertIn('exposes none',result['verdict'])
        self.assertEqual(result['human_ragdoll_samples'],1)

    def test_multiple_infected_bodies_not_claimed_ragdoll(self):
        text=trace('Human','human_death_now',0,11,11,ragdoll=True)+trace('Zombie','infected_death_now',0,11,11)
        self.assertIn('not proof',analyze(text)['verdict'])

    def test_missing_stage_and_live_samples_not_death(self):
        text=trace('Human','human_death_now',0,11,11,ragdoll=True)+trace('Zombie','infected_death_now',1,0,0,complete=False)
        result=analyze(text)
        self.assertEqual(result['dead_infected_samples'],0)
        self.assertEqual(len(result['unfinished_samples']),1)

    def test_probe_is_read_only_and_uses_declared_api(self):
        source=(TEST/'StartGateSource/Scripts/4_World/MovementLabPhysicsProbe.c').read_text()
        forbidden=['ChangeSimulationState(', 'SetActive(', 'PhysicsSetRagdoll(', 'SetBoneGlobal(', 'CreateObject', 'SetObject(', 'SetFlags(', 'ObjectDelete(']
        self.assertFalse(any(x in source for x in forbidden))
        self.assertIn('GetGame().IsMultiplayer()',source)
        self.assertIn('count > 256',source)
        self.assertIn('limit > 32',source)
        sdk=Path('/tmp/dayz-script-diff/scripts')
        declarations='\n'.join((sdk/p).read_text() for p in ['1_core/proto/enentity.c','1_core/physics/physics.c','3_game/human.c'])
        for name in ['GetPhysics','GetNumBones','GetBone','IsDynamic','IsKinematic','PhysicsIsRagdoll']:
            self.assertRegex(declarations,r'\b'+name+r'\s*\(')

    def test_only_expected_source_files_changed(self):
        changes=[]
        for p in (BASE/'StartGateSource').rglob('*'):
            if p.is_file() and p.read_bytes()!=(TEST/p.relative_to(BASE)).read_bytes():changes.append(p.name)
        self.assertEqual(sorted(changes),['MovementLabRangeInfected.c','MovementLabRangeNPC.c'])
        self.assertEqual((BASE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes(),(TEST/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes())
        self.assertFalse((TEST/'StartGateSource/Scripts/4_World/MovementLabZombieRagdoll.c').exists())
        for name in ['MovementLabRangeInfected.c','MovementLabRangeNPC.c']:
            before=(BASE/'StartGateSource/Scripts/4_World'/name).read_text()
            after=(TEST/'StartGateSource/Scripts/4_World'/name).read_text()
            stripped='\n'.join(line for line in after.splitlines() if 'MovementLabPhysicsProbe.Observe(' not in line)+'\n'
            self.assertEqual(before,stripped)


if __name__=='__main__':unittest.main(verbosity=2)
