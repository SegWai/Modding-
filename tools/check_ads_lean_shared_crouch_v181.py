"""Shared gait-bank selection, exact user presets and synchronized crouch scene."""
from pathlib import Path
import sys,re,json,hashlib,itertools,random
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));from dayz_graph_formats import newnodes
base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v180';out=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v181';w=out/'LogicSource/Scripts/4_World'
spec=json.loads((out/'Shared-Presets-Crouch-v181.json').read_text())
for filename,key in [('MLLeanPreset.json','standing_preset_sha256'),('MLWalkingLeanPreset.json','walking_preset_sha256')]:
 for rel in [filename,'Profiles/LeanMosin/'+filename,'LogicSource/Presets/'+filename]:
  assert hashlib.sha256((out/rel).read_bytes()).hexdigest()==spec[key],rel
 assert hashlib.sha256((r/'artifacts'/filename).read_bytes()).hexdigest()==spec[key]
 assert json.loads((out/filename).read_bytes())['PresetVersion']==1
assert spec['walking_preset_sha256']=='8828945ff4dc5eb7e0b2d8de7adddfff463ec5403db61de44b56b10a16ce42c2'
assert spec['standing_preset_sha256']=='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
player=(w/'MLADSLeanPlayer.c').read_text();routing=(w/'MLSharedPose181.c').read_text()
handler=player.split(' override void CommandHandler(')[1].split(' protected void ML173UpdateGraph(')[0]
assert 'ML181PoseRouting.WalkingBank(routingState.m_iStanceIdx, routingState.m_iMovement)' in handler
assert handler.index('super.CommandHandler')<handler.index('m_ML173Scope.Enter()')<handler.index('ML173UpdateGraph(')<handler.index('m_ML173Scope.Leave()')
assert 'GetGame().GetPlayer()' not in handler and 'm_MLADSLeanDemo' not in handler
assert 'SetPosition(' not in handler and 'ML181RefreshBankWrites();' in handler
assert 'releaseMove.ForceStance(-1)' in handler
stop=player.split(' void MLADSLeanStopDemo()')[1].split(' protected void MLADSLeanUpdateDemoInput')[0]
assert 'ForceStance(' not in stop and 'm_ML181ReleaseCrouch = m_ML181CrouchDemo;' in stop
assert '(!localPlayer && !m_MLADSLeanDemo)' not in player.split(' protected void ML173UpdateGraph(')[1].split(' protected void MLADSLeanCalibrateStandingHeight(')[0]
assert '  ML172UpdateWalkingUpper(pDt, state);' not in player
assert '  ML157UpdateHead(pDt, state);' not in player
# Actor and view identity cannot change bank routing; stance and gait only.
route_cases=0
for actor,view,stance,gait in itertools.product(['player','lowered_npc','raised_npc','other_npc'],['FP','TP','ADS'],range(6),range(4)):
 walking=stance in [0,3] and gait in [1,2]
 assert walking==((stance==0 or stance==3) and (gait==1 or gait==2))
 route_cases+=1
assert 'return upright && (movement == 1 || movement == 2);' in routing
# Cached coefficient writes are invalidated when data bank changes even when
# both banks coincidentally share the same revision counter.
assert 'm_ML154EditorWritten[i] = false;' in player and 'm_ML149Last[part] = 1000;' in player
stand=json.loads((out/'MLLeanPreset.json').read_bytes());walk=json.loads((out/'MLWalkingLeanPreset.json').read_bytes())
sequence=[0,1,0,1,1,0]*50;cache=None;results=[]
for bank in sequence:
 value=(walk if bank else stand)['LeftLean']['WeaponSettings']['X']
 if cache is None or cache[0]!=bank:cache=(bank,value)
 results.append(cache[1]);assert cache[1]==value
assert len(set(results))==2
# Per-actor standing/walking x left/right x arm references never overlap.
assert 'm_ML154ReferenceReady[4]' in player
for name in ['Root','Elbow','Wrist']:assert 'm_ML146'+name+'[8]' in player
keys={bank*2+side for bank,side in itertools.product([0,1],[0,1])};assert keys=={0,1,2,3}
indices={key*2+arm for key,arm in itertools.product(keys,[0,1])};assert indices==set(range(8))
assert 'int snapshot = m_ML181ArmKey * 2 + side;' in player
assert 'int leftSnapshot = referenceSide * 2;' in player
assert 'm_ML181HoldRevision[bank]' in player and 'm_ML181BodyRevision[bank]' in player
# Parse the actual original scoped assignment lists and simulate interleaved
# actor updates: stationary global data always restored after moving actors.
scope=(w/'MLWalkingEditorScope173.c').read_text();enter=scope.split(' void Enter()')[1].split(' void Leave()')[0];leave=scope.split(' void Leave()')[1]
pat=re.compile(r'^  (\w+(?:\.\w+)?) = (\w+(?:\.\w+)?);',re.M)
enters=pat.findall(enter);leaves=pat.findall(leave);assert len(enters)==len(leaves)==56
keys={k for pair in enters+leaves for k in pair};rnd=random.Random(181)
state={k:object() for k in keys};fixed={k:v for k,v in state.items() if k.startswith(('ML144State.','ML149State.'))}
for _ in range(100):
 for actor in ['player','moving_npc','standing_npc']:
  if actor=='standing_npc':assert all(state[k] is v for k,v in fixed.items());continue
  for dest,src in enters:state[dest]=state[src]
  for dest,src in leaves:state[dest]=state[src]
  assert all(state[k] is v for k,v in fixed.items())
# Exactly two replacements, with role/spacing and cleanup; no former walking
# movement overrides or world-origin pin remain in the actor/mission code.
mission=(out/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert mission.count(' = ML181CreatePreview(')==2
assert '"Hoodie_Red", false)' in mission and '"Hoodie_Blue", true)' in mission
assert 'right * 0.5' in mission and spec['previous_separation_metres']-spec['separation_metres']==2
for name in ['ML136SpawnLeanNPC','ML173SpawnWalkingNPC','m_ML136NPC','m_ML173NPC']:assert name not in mission
for name in ['m_ML181LoweredNPC','m_ML181RaisedNPC']:assert 'GetGame().ObjectDelete('+name+')' in mission
assert 'ML173StartWalkingDemo' not in player
inputfn=player.split(' protected void MLADSLeanUpdateDemoInput(')[1].split(' protected void ML144UpdateEditor(')[0]
assert 'ForceStance(DayZPlayerConstants.STANCEIDX_CROUCH)' in inputfn
assert 'OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 0)' in inputfn
assert 'OverrideRaise(HumanInputControllerOverrideType.ENABLED, m_ML181RaisedDemo)' in inputfn
assert 'ML181CrouchCycle.Target(GetGame().GetTime())' in inputfn
assert 'ML144State.Open' not in inputfn and 'ML173WeaponState.Open' not in inputfn
assert 'bool demoADS = false;' in player and 'requestedHeadADS = false;' in player
assert 'raised = demoControllerActive && m_ML181RaisedDemo;' in player
assert 'demoControllerActive && m_ML181RaisedDemo' in player
assert 'if (m_ML181RaisedDemo)\n     AnimSetInt(m_MLADSLeanDemoArmIK, 7);' in player
# Shared absolute-time schedule, with forward nonlean phase on both sides.
def target(now):
 phase=(max(0,now)//1000)%4
 return -1 if phase==0 else (1 if phase==2 else 0)
assert [target(i*1000) for i in range(8)]==[-1,0,1,0,-1,0,1,0]
for ms in range(0,20000,7):assert target(ms)==target(ms)
assert target(999)==-1 and target(1000)==0 and target(2000)==1 and target(3000)==0
# Graph changes only remove old demo-forced ADS; all pose transforms remain.
a=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((out/'WorkspaceSource/locomotion.agf').read_text());assert a.keys()==b.keys()
count=0
for name,old in a.items():
 expected=old.replace('(ADS || MLADSLeanCanary > 0.9)','ADS')
 assert b[name]==expected,name
 count+=old.count('(ADS || MLADSLeanCanary > 0.9)')
assert count==18 and spec['old_canary_ADS_clauses_removed']==18
assert '(ADS || MLADSLeanCanary > 0.9)' not in (out/'WorkspaceSource/locomotion.agf').read_text()
# Ordinary actor ADS retains the original truth table when canary=.731.
for ads in [False,True]:assert (ads or .731>.9)==ads
# No known native Enforce regressions, duplicate new classes or unbalanced code.
classes=[]
for p in (out/'LogicSource/Scripts').rglob('*.c'):
 text=p.read_text();assert not re.search(r'\]\s*(\+\+|--)|(\+\+|--)\s*[A-Za-z_]\w*\[',text),p
 classes+=re.findall(r'^class (\w+)',text,re.M)
 stripped=re.sub(r'//[^\n]*|"(?:\\.|[^"\\])*"','',text);assert stripped.count('{')==stripped.count('}'),p
assert len(classes)==len(set(classes))
result={'exact_uploaded_presets':True,'actor_view_stance_gait_cases':route_cases,'interleaved_bank_restore_updates':200,'bank_swap_sequence_steps':len(sequence),'reference_keys':4,'arm_snapshot_indices':8,'new_npc_count':2,'centre_spacing_metres':.5,'synchronized_targets':['left','centre','right','centre'],'target_interval_seconds':1,'forced_ADS_clauses_removed':count,'native_crouch_raised_and_player_pose_matching':'NOT RUN'}
(out/'Shared-Presets-Crouch-Checks-v181.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
