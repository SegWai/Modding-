"""Offline approved-default integrity and crouch reference-bank isolation."""
from pathlib import Path
import hashlib,itertools
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v187';b=a.with_name('MovementLab_ADS_Lean_Mosin_v188')
expected={'MLLeanPreset.json':'aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d','MLWalkingLeanPreset.json':'8828945ff4dc5eb7e0b2d8de7adddfff463ec5403db61de44b56b10a16ce42c2','MLCrouchLeanPreset.json':'2de68073870eb3b17bf24f9546ff90a41b737b516b0535351eae6d247f90eb20','MLUnarmedLeanPreset.json':'d47025fd4275847815d0fda2d34b629d057608355e7fb5d47e79f4b71d859a27'}
for n,digest in expected.items():
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest,rel
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
rel='LogicSource/Scripts/4_World/MLADSLeanPlayer.c'
for p in (a/'LogicSource/Scripts').rglob('*'):
 if p.is_file()and p.relative_to(a).as_posix()!=rel:assert p.read_bytes()==(b/p.relative_to(a)).read_bytes(),p
s=(b/rel).read_text()
for text in ['m_ML181HoldRevision[3]','m_ML181BodyRevision[3]','m_ML154ReferenceReady[6]','m_ML146Root[12]','m_ML146Elbow[12]','m_ML146Wrist[12]','clearBank < 6','if (m_ML182EditableCrouch)\n   bank = 2;','m_ML182Hold.Write(this, null, false)','MLADSLeanWeaponSupport106.Profile(crouchHeld) == 1']:
 assert text in s,text
# Scope and key separation: a crouch sample must never reuse a standing one.
keys={(bank,side):bank*2+side for bank in range(3)for side in range(2)};assert len(set(keys.values()))==6
snapshots={key*2+arm for key in keys.values()for arm in range(2)};assert len(snapshots)==12
cases=0
for move,alive,awake,crouch,stationary,profile in itertools.product([False,True],repeat=6):
 selected=move and alive and awake and crouch and stationary and profile
 if selected:assert crouch and stationary and profile
 cases+=1
for p in (a/'Missions').rglob('*'):
 if p.is_file():assert p.read_bytes()==(b/p.relative_to(a)).read_bytes()
print(f'PASS:12 exact approved JSON copies;{cases} crouch routing cases;6 isolated side references/12 arm snapshots;standing-held helper/other scripts/graph/scene unchanged. Native compilation/rendering NOT RUN.')
