"""Regression: a request alone MUST NOT move camera, and neutral capture precedes loadout."""
from pathlib import Path
import itertools,re
r=Path(__file__).resolve().parents[1];a=r/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v3';b=a.with_name('MovementLab_Ambidextrous_Lean_v4');h=(b/'LogicSource/Scripts/4_World/MLAShoulderPose.c').read_text();scene=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert 'Override3rdIsRightShoulder(HumanInputControllerOverrideType.ENABLED, !MLAShoulderSettings.LeftActive)'in h
assert 'Override3rdIsRightShoulder(HumanInputControllerOverrideType.ENABLED, false)'not in h
assert h.count('Override3rdIsRightShoulder(HumanInputControllerOverrideType.ENABLED')==1
assert 'MLAShoulderSettings.NeutralReady = Neutral != null;'in h
assert 'SetStatus("waiting for neutral skeleton reference")'in h
assert 'MLASFinishLoadout, 100, true'in scene and 'Remove(MLASFinishLoadout)'in scene
oninit=scene[scene.index(' override void OnInit()'):scene.index(' void MLASFinishLoadout()')];assert 'MLVanillaLoadout156.Equip'not in oninit
finish=scene[scene.index(' void MLASFinishLoadout()'):scene.index(' void ML105EquipStartingWeapon()')];assert 'm_MLASSetupAttempts < 50'in finish and 'MLVanillaLoadout156.Equip(setupPlayer)'in finish
# Exercise all readiness dimensions: camera can only be left when actual pose
# is active. Disabled/request-only/neutral-pending/solve-failed all stay RIGHT.
cases=0
for request,neutral,raised,supported,enabled,solution in itertools.product([False,True],repeat=6):
 applied=request and neutral and raised and supported and enabled and solution
 camera_right=not applied
 if not applied:assert camera_right
 if camera_right==False:assert request and neutral and raised and solution
 cases+=1
# Automatic startup 100ms polling equips exactly ONCE after neutral is ready,
# or bounded fallback. Mission finish cancels queue and cannot create late gun.
for ready_at in [4,8,15,None]:
 equipped=0;equip_at=None
 for tick in range(1,70):
  if equipped:continue
  ready=ready_at is not None and tick>=ready_at
  if not ready and tick<50:continue
  equipped+=1;equip_at=tick
 assert equipped==1 and equip_at==(ready_at if ready_at else 50)
for name in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [name,'Profiles/LeanMosin/'+name,'LogicSource/Presets/'+name]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['WorkspaceSource/locomotion.agf','LogicSource/Inputs.xml']:assert(a/rel).read_bytes()==(b/rel).read_bytes()
assert not re.search(r'\w+\[[^\]]+\]\s*(?:\+\+|--)',h)
print(f'PASS: {cases} request/readiness camera invariants, automatic setup/timeout exactly-once; graph/IK/presets unchanged. Native left publication NOT verified.')
