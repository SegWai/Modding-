"""Offline native-grip ordering and pose seed isolation regression."""
from pathlib import Path
import sys,re,json
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v190';b=a.with_name('MovementLab_ADS_Lean_Mosin_v191')
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
expected=old['NormalWeaponIK'].replace('AnimSrcNodeWeaponIk NormalWeaponIK','AnimSrcNodeWeaponIk ML187_PublishHeldLean').replace('Child "AimObstructionT"','Child "ML183_Edit_RightToeBase_RZ"').replace('IkconfigName "WeaponIKTest"','IkconfigName "ML191_NativeLoweredGrip"')
assert new['ML187_PublishHeldLean']==expected
for n,v in old.items():
 if n.startswith('{')or n=='ML187_PublishHeldLean':continue
 if n=='ML183_Base6':v=v.replace('Child "NormalWeaponIK"','Child "ML191_HeldBeforeBody"')
 assert new[n]==v,n
assert {n for n in set(new)-set(old)if not n.startswith('{')}=={'ML191_HeldBeforeBody'}
# Each chosen path has one native grip stage; no upstream+downstream double solve.
def path(n,held,seen):
 if n not in new:return
 assert n not in seen,n
 seen.add(n);v=new[n]
 if n in ['ML187_PublishHeldLean','NormalWeaponIK']:seen.add('GRIP:'+n)
 if n in ['ML191_HeldBeforeBody','ML187_HeldGrip']:
  child=re.search(r'Child'+str(int(held))+r' "([^"]+)"',v)[1];path(child,held,seen)
 else:
  child=re.search(r'\bChild "([^"]+)"',v)
  if child:path(child[1],held,seen)
for held in [False,True]:
 seen=set();path('ML187_HeldGrip',held,seen)
 assert len([x for x in seen if x.startswith('GRIP:')])==1,seen
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'LogicSource/Presets/'+n,'Profiles/LeanMosin/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
olddata=json.loads((a/'MLHeldLeanPreset.json').read_text());data=json.loads((b/'MLHeldLeanPreset.json').read_text())
for side in ['LeftLean','RightLean']:
 for k in ['LeftPitch','LeftYaw','LeftRoll','RightPitch','RightYaw','RightRoll']:olddata[side]['WeaponSettings'][k]=0.0
 for part in olddata[side]['BodySettings']['Parts']:
  if part['BoneName']in ['LeftShoulder','RightShoulder','LeftArm','RightArm','LeftForeArm','RightForeArm','LeftHand','RightHand']:
   for k in ['X','Y','Z','Pitch','Yaw','Roll']:part[k]=0.0
assert data==olddata
for rel in ['LogicSource/Presets/MLHeldLeanPreset.json','Profiles/LeanMosin/MLHeldLeanPreset.json']:assert(b/rel).read_bytes()==(b/'MLHeldLeanPreset.json').read_bytes()
for directory in ['LogicSource/Scripts','Missions']:
 for p in (a/directory).rglob('*'):
  if p.is_file():assert p.read_bytes()==(b/p.relative_to(a)).read_bytes()
assert not(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').exists()
print('PASS:native lowered grip template exact;one grip stage per held/empty path;only experimental arm seed changed;all4approved presets/torso/head/legs/scene/scripts/camera preserved. Native load/contact not tested.')
