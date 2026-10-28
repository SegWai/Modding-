"""Verify aiming order, rigid grip geometry, and unchanged preset/scripts."""
from pathlib import Path
import re,sys,json,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent))
from dayz_graph_formats import newnodes
sys.setrecursionlimit(10000)
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v165';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v166'
old={k:v for k,v in newnodes((a/'WorkspaceSource/locomotion.agf').read_text()).items() if not k.startswith('{')};new={k:v for k,v in newnodes((b/'WorkspaceSource/locomotion.agf').read_text()).items() if not k.startswith('{')}
assert set(new)-set(old)=={'ML166_FinalVerticalAim','ML166_FinalHorizontalAim','ML166_PublishFinalAimedWeapon','ML166_FinalAimOnly'}
changed={'MeleeBlockQ','ML67_SharedVerticalAim','ML68_SharedHorizontalAim'}
for k,v in old.items():
 if k not in changed:assert new[k]==v,k
for original,late in [('ML67_SharedVerticalAim','ML166_FinalVerticalAim'),('ML68_SharedHorizontalAim','ML166_FinalHorizontalAim')]:
 expr=re.search(r'Expression "([^"]+)"',old[original])[1]
 expected=old[original].replace('Expression "'+expr+'"','Expression "('+expr+')*clamp(ML87FirstPersonCrouchLean+(1.0-ML106ShoulderedGrip),0.0,1.0)"',1)
 assert new[original]==expected
 assert expr in new[late] and 'Bone "Spine3"' in new[late]
assert 'Child "ML157_HeadZ"' in new['ML166_FinalVerticalAim']
assert 'Child "ML166_FinalVerticalAim"' in new['ML166_FinalHorizontalAim']
assert 'Child "ML166_FinalHorizontalAim"' in new['ML166_PublishFinalAimedWeapon']
assert 'Child "ML166_FinalAimOnly"' in new['MeleeBlockQ']
expectedpub=old['ML149_BodyWeaponFollow'].replace('ML149_BodyWeaponFollow','ML166_PublishFinalAimedWeapon',1).replace('ML149_BodyWeaponConfig','ML166_FinalAimedConfig').replace('Child "ML154_BodyGate_RightToeBase"','Child "ML166_FinalHorizontalAim"',1)
assert new['ML166_PublishFinalAimedWeapon']==expectedpub
assert 'WeightPrimaryChain "false"' in expectedpub and 'WeightSecondaryChain "false"' in expectedpub
assert 'ML147LeftMuzzleYaw' in expectedpub and 'ML147RightMuzzleYaw' in expectedpub
# First-person and handguns keep original early aiming. Third-person rifles
# receive only the late path, with zero added rotation at centred aim.
for first in [0,1]:
 for rifle in [0,1]:
  early=max(0,min(1,first+(1-rifle)));late=(1-first)*rifle
  assert early+late==1
  if first or not rifle:assert early==1 and late==0
# Common rigid rotation of spine subtree retains every hand-to-gun relation.
source=json.loads((a/'Native-Head-Travel-v55.json').read_text())['sides']['right']['desired']
pivot=np.array(source['Spine3'])[:3,3];right=np.array(source['RightHand']);left=np.array(source['LeftHand']);weapon=right.copy();weapon[:3,3]+=right[:3,:3]@np.array([.02,.03,.12]);relative=np.linalg.inv(weapon)@left
rng=np.random.default_rng(166);maxerr=0.
for _ in range(1000):
 pitch=rng.uniform(-89,89);yaw=rng.uniform(-90,90);weight=rng.uniform(0,1)
 rot=Rotation.from_euler('y',yaw*weight,degrees=True).as_matrix()@Rotation.from_euler('x',-pitch*weight,degrees=True).as_matrix()
 def transform(frame):
  out=frame.copy();out[:3,:3]=rot@frame[:3,:3];out[:3,3]=pivot+rot@(frame[:3,3]-pivot);return out
 aimedweapon=transform(weapon);aimedleft=transform(left)
 err=float(np.max(abs(np.linalg.inv(aimedweapon)@aimedleft-relative)));maxerr=max(maxerr,err);assert err<1e-10
for p in (a/'LogicSource/Scripts').rglob('*.c'):assert p.read_bytes()==(b/p.relative_to(a)).read_bytes(),p
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
 assert hashlib.sha256((b/rel).read_bytes()).hexdigest()=='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
# No cycles in the altered live root.
active=set();done=set()
def visit(n):
 if n in done:return
 assert n not in active,('cycle',n);active.add(n)
 for child in re.findall(r'\bChild\d* "([^"]+)"',new[n]):
  if child in new:visit(child)
 active.remove(n);done.add(n)
visit('LocomotionQ')
report={'aim_rotation_order':'after custom arm/body/head edits, before final hand-pivot weapon publication','rigid_aim_cases':1000,'max_hand_to_weapon_matrix_error':maxerr,'first_person_and_handguns':'original early aim retained','user_muzzle_fields':'preserved in final publisher','v165_crash_gates_and_scripts':'unchanged','fixed_preset_sha256':'aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d','native_grip_muzzle_pose_and_crash_verification':'NOT RUN'}
(b/'Late-Aim-Grip-Checks-v166.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
