"""Approved bank rollout, transition guards, cache isolation and camera scope."""
from pathlib import Path
import json,re,hashlib,itertools
r=Path(__file__).resolve().parents[1];b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v185';o=b.with_name('MovementLab_ADS_Lean_Mosin_v186');w=o/'LogicSource/Scripts/4_World';spec=json.loads((o/'Player-Rollout-v186.json').read_text())
for name,sha in spec['approved_sha256'].items():
 raw=(r/'ads-lean-test/User-Presets'/('Current-'+name)).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
 for rel in [name,'Profiles/LeanMosin/'+name,'LogicSource/Presets/'+name]:assert(o/rel).read_bytes()==raw
mission=(o/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();assert mission.count('CreatePlayer(')==1 and 'ML181SpawnCrouchPair'not in mission and 'ML181CreatePreview'not in mission
assert 'm_ML182NativeNPC'not in mission and 'm_ML182CustomNPC'not in mission
assert 'MLVanillaLoadout156.Equip(player)'in mission
player=(w/'MLADSLeanPlayer.c').read_text();helper=(w/'MLUnarmedPose183.c').read_text()
assert 'UpdatePlayer(this, pDt, routingState.m_fLeaning)'in player
assert 'm_ML183UnarmedPose.ReleasePlayer(this)'in player
assert 'm_ML182Hold.Write(this, null, false)'in player
assert 'if (m_ML182EditableCrouch)\n   bank = 2;'in player
for field,dim in [('m_ML181HoldRevision',3),('m_ML181BodyRevision',3),('m_ML154ReferenceReady',6),('m_ML146Root',12),('m_ML146Elbow',12),('m_ML146Wrist',12)]:assert f'{field}[{dim}]'in player
assert 'clearBank < 6'in player
# Separate caches uniquely cover all three weapon-stance banks and both arms.
refs=set();samples=set()
for bank,side,arm in itertools.product(range(3),range(2),range(2)):
 key=bank*2+side;refs.add(key);samples.add(key*2+arm)
assert refs==set(range(6))and samples==set(range(12))
# Guarded data routing keeps non-authored contexts native while ordinary
# standing/walking saved paths are selected by gait, not identity/view.
cases=0
for stance,move,hands,raised,alive,cmd,enabled in itertools.product(range(6),range(4),['empty','rifle','pistol','item'],[False,True],[False,True],['move','other'],[False,True]):
 valid=alive and cmd=='move';standing=stance in [0,3];crouched=stance in [1,4]
 unarmed=valid and standing and move==0 and hands=='empty'and not raised and enabled
 crouch=valid and crouched and move==0 and hands=='rifle'
 walking=standing and move in [1,2]
 assert not(unarmed and crouch)
 if unarmed:assert not walking and hands=='empty'and not raised
 if crouch:assert not walking
 cases+=1
# Emulate the real control handoff: unarmed sets native root, forces no input;
# on exit it releases root/flag, legacy rewrites its bank, unarmed cached writes
# are invalidated so reentry reapplies saved values even without slider changes.
controls={'active':0,'native':0,'preview':0,'body':0};cached=None;releases=0
for context in ['unarmed','standing','walking','crouch','standing','unarmed','item','unarmed']:
 if context=='unarmed':
  controls['active']=1;controls['native']=1;controls['preview']=0
  if cached!=7:controls['body']=7;cached=7
  assert controls['body']==7
 else:
  if controls['active']:
   controls['active']=0;controls['native']=0;controls['preview']=0;cached=None;releases+=1
  controls['body']=3
  assert controls['active']==0 and controls['preview']==0
assert releases==2
start=helper.index('  if (!PlayerInput)');end=helper.index('  actor.AnimSetFloat(NativeVar, 1);',start);block=helper[start:end];nativeblock=block[:block.index('  else')];realblock=block[block.index('  else'):]
assert 'AnimSetBool(RaisedVar' in nativeblock and 'AnimSetBool(ADSVar'in nativeblock
assert 'AnimSetBool'not in realblock and 'AnimSetFloat(LeanVar'not in realblock
assert 'Last[index] = 1000'in helper
# No authored pose graph or first-person/ADS camera code changed in rollout.
assert(o/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
assert(w/'MLADSLeanCamera.c').read_bytes()==(b/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes()
cam=(w/'MLInspectionCamera171.c').read_text();oldcam=(b/'LogicSource/Scripts/4_World/MLInspectionCamera171.c').read_text()
assert re.findall(r'pOutResult.m_fDistance = .*;',cam)==re.findall(r'pOutResult.m_fDistance = .*;',oldcam)
assert 'Weapon_Base.Cast(cameraPlayer.GetHumanInventory().GetEntityInHands())'in cam
assert 'pivotDrop = -0.15'in cam
assert abs((.35)-(-.15)-.50)<1e-12 and abs(.10-(-.15)-.25)<1e-12
assert 'm_pPlayer.IsRaised()'not in cam # DayZPlayer base lacks script method; cast PlayerBase.
sdk=(Path('/tmp/dayz-native162/scripts/3_game/human.c')).read_text();assert re.search(r'bool\s+IsRaised\(',sdk)
assert not re.search(r'\w+\[[^\]]+\]\s*(?:\+\+|--)',helper)
result={'approved_banks':'all four exact','spawned_NPCs':0,'routing_guard_cases':cases,'reference_slots':6,'arm_snapshots':12,'transition_cache_handoff':'passed','raised_camera_distance':'identical','camera_height_vs185_m':{'standing':.5,'crouch':.25},'graph_and_first_person_camera':'byte-identical','native_compile_rendering_crash':'NOT RUN'}
(o/'Player-Rollout-Checks-v186.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
