#!/usr/bin/env python3
"""Validate half-walk schema and preservation; native playback requires DayZ."""
from pathlib import Path
import re,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'ctrl-mode-test/MovementLabCrouchWheel_SixLevels_v4'
SOURCE=ROOT/'ctrl-mode-test/MovementLabScroll_TargetQueue_v9'
def block_end(s,start):
 i=s.index('{',start);depth=0;q=False;esc=False
 for j in range(i,len(s)):
  c=s[j]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':q=False
  elif c=='"':q=True
  elif c=='{':depth+=1
  elif c=='}':
   depth-=1
   if depth==0:return j+1
 raise AssertionError('unclosed block')
def nodes(s):
 out={}
 for m in re.finditer(r'\$Node\s+(\w+)\s*\{',s):
  raw=s[m.start():block_end(s,m.start())];name=re.search(r'"([^"\n]+)"',raw)[1]
  assert name not in out,name;out[name]=raw
 return out
ast=(SOURCE/'WorkspacePatches/player_main.ast').read_text();columns={}
for m in re.finditer(r'\$groupType(?:\s+"([^"]+)")?\s*\{',ast):
 raw=ast[m.start():block_end(ast,m.start())];g=re.search(r'\$groupnames\s*\{([^}]*)\}',raw)
 groups=re.findall(r'"([^"]+)"',g[1]) if g else []
 slots=re.findall(r'"([^"]+)"',re.search(r'\$anims\s*\{([^}]*)\}',raw)[1])
 assert groups==sorted(groups) and slots==sorted(slots)
 assert len(groups)==int(re.search(r'#ngroupnames (\d+)',raw)[1])
 assert len(slots)==int(re.search(r'#nanims (\d+)',raw)[1]);columns[m[1] or '']=(groups,slots)
assert len(columns)==29
assert columns['ZZMovementLabStandingWalk']==(['L1','L1J2','L2','L2J2','NJ2'],columns['Locomotion'][1])
original_ast=(BASE/'WorkspacePatches/player_main.ast').read_text()
for m in re.finditer(r'\$groupType(?:\s+"([^"]+)")?\s*\{',original_ast):
 assert original_ast[m.start():block_end(original_ast,m.start())] in ast
asi=(SOURCE/'WorkspacePatches/player_main.asi').read_text();a=asi.index('$animations');end=block_end(asi,a)
rows=re.findall(r'"([^"\n]+)"\s+"([^"\n]+)"',asi[asi.index('{',a)+1:end-1]);mapping=dict(rows)
assert len(mapping)==len(rows)
for key,path in rows:
 t=key.split('.')
 if len(t)==1:assert t[0] in columns[''][1]
 else:assert len(t)==3 and t[1] in columns[t[0]][0] and t[2] in columns[t[0]][1],key
baseline_asi=(BASE/'WorkspacePatches/player_main.asi').read_text();b=baseline_asi.index('$animations')
assert set(re.findall(r'"([^"\n]+)"\s+"([^"\n]+)"',baseline_asi[b:block_end(baseline_asi,b)])).issubset(set(rows))
graph=(SOURCE/'WorkspacePatches/locomotion.agr').read_text();new=nodes(graph);old=nodes((BASE/'WorkspacePatches/locomotion.agr').read_text())
assert len(new)==len(old)+65+22
qpat=r'"((?:[^"\\]|\\.)*)"'
manifest=__import__('json').loads((SOURCE/'Smoothing-Coverage.json').read_text())
assert len(manifest['changes'])==99
allowed_changes={entry['node'] for entry in manifest['changes']}|{'ErcMoveLowG','CroMoveLowG','CroRunSprintBlendMLWheel'}
for name,raw in old.items():
 if name not in allowed_changes:assert new[name]==raw,name
all_names=set(new)
for name,raw in new.items():
 for token in re.findall(qpat,raw):
  if token.endswith(('MLOriginal','MLSmooth','MLPrevious','MLLateral')):
   assert token in all_names,(name,token)
assert len([name for name in new if name.endswith('MLStandingWheel')])==59
assert 'MovementLabWalkJogPose' in new['WalkRunSprintBlendTMLStandingWheelMLSmooth']
assert 'MovementLabJogSprintPose' in new['RunSprintBlendFMLStandingWheel']
assert 'ErcWheelRow80' in new['ErcWheelMatrix'] and 'ErcWheelRow100' in new['ErcWheelMatrix']
for name in ['WalkFowardCyclicMLWheel','WalkFowardCyclicMLStandingWheel','RunFowardCyclicMLStandingWheel']:
 assert 'MovementLabLateralPose' in new[name+'MLLateral']
 assert 'MovementLabLateralActive' in new[name]
for slot,path in mapping.items():
 if slot.startswith('Locomotion.Erc.'):
  leaf=slot.split('.')[2]
  for level in [1,2]:
   target=mapping['ZZMovementLabStandingWalk.L'+str(level)+'.'+leaf]
   if leaf in ['WalkB','WalkBL','WalkBR','WalkF','WalkFL','WalkFR']:
    assert target.endswith('/StandingWalkVariants/L'+str(level)+'/p_erc_walk'+leaf[4:]+'.anm')
   else:assert target==path
for group,walkgroup in [('L1J2','L1'),('L2J2','L2'),('NJ2',None)]:
 for key,path in mapping.items():
  if key.startswith('Locomotion.Erc.'):
   leaf=key.split('.')[2];target=mapping['ZZMovementLabStandingWalk.'+group+'.'+leaf]
   if leaf in ['RunB','RunBL','RunBR','RunF','RunFL','RunFR']:
    assert target.endswith('/StandingJogVariants/J80/p_erc_run'+leaf[3:]+'.anm')
   elif walkgroup:assert target==mapping['ZZMovementLabStandingWalk.'+walkgroup+'.'+leaf]
   else:assert target==path
# World logic changes confined to graph binding; all existing movement methods preserved.
w=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text();bw=(BASE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for m in re.finditer(r'\b(?:void|bool|float)\s+(\w+)\([^)]*\)\s*\{',bw):
 if m[1] not in ['CommandHandler','MovementLabWantedGait','MovementLabCommandStart','MovementLabUpdateCrouchRules','MovementLabUpdateCrouchWheel']:assert bw[m.start():block_end(bw,m.start())] in w,m[1]
assert 'm_MovementLabWalkLevel = 1;' in w and 'BindVariableFloat("MovementLabWalkLevel")' in w
assert 'HalfWalk' not in w
assert 'MessageStatus("Walking speed level' not in w
assert 'MessageStatus("Jogging' not in w
assert 'm_MovementLabJogLevel = 2;' in w
assert '[MovementLab Walk Wheel v3] Graph variable binding=' in w
mission=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
assert 'KC_F8' not in mission and 'HalfWalk' not in mission
# Every mission movement/brake method stays identical.
bm=(BASE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
for m in re.finditer(r'\b(?:void|bool|float)\s+(\w+)\([^)]*\)\s*\{',bm):
 if m[1] not in ['OnKeyPress','MovementLabUpdateBrake','OnUpdate']:assert bm[m.start():block_end(bm,m.start())] in mission,m[1]
prep=(SOURCE/'Prepare-Crouch-Clips.ps1').read_text()
assert '$movementlabWalkOriginal.Clone()' in prep and '@(0,24,30)' in prep
assert '$movementlabJogOriginal.Clone()' in prep and 'GetBytes([uint32]24)' in prep
assert 'StandingJogVariants\\J80\\$movementlabJogName' in prep
assert 'StandingWalkVariants\\L$movementlabWalkTier\\$movementlabWalkName' in prep
# Actual supplied ANM demonstrates the byte-level retiming invariant.
clip=Path('/workspace/attachments/d8337ae6-7dd3-447d-95fb-a0d800ada321/p_cro_walkf.anm').read_bytes()
assert clip[:4]==b'FORM' and clip[8:16]==b'ANIMSET6' and struct.unpack_from('<I',clip,28)[0]==30
for fps in [26,36,24]:
    variant=bytearray(clip);struct.pack_into('<I',variant,28,fps)
    assert variant[:28]==clip[:28] and variant[32:]==clip[32:]
    assert struct.unpack_from('<I',variant,28)[0]==fps
assert 36/30==1.2 and 24/30==0.8 and abs(26/30-0.85)<0.017
# Fixed approved package integrity.
assert hashlib.sha256((ROOT/'artifacts/MovementLab_Crouch_Wheel_Six_Levels_v4.zip').read_bytes()).hexdigest()=='bfee1d3ff3f45fdb38baee99eb6f33379d7ccaf582147265150b0eae3bb0544d'
print('Jog80/100 and scroll sprint boundaries, full-stop exposure and graph schema verified. Native runtime pending.')
# Reuse baseline actual-controller translation with this variant's World code.
# Distinct graph bindings ensure F8 cannot overwrite the crouch level variable.
import subprocess,tempfile
b=(ROOT/'movement-logic-test/MovementLabMovementLogicTest/Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
m=mission
harness=(ROOT/'tools/check_crouch_wheel_six_levels_v4.py').read_text()
harness=harness[harness.index("source=w.replace"):]
harness=harness.replace("sdk=r"+chr(39)*3, "source=source.replace('MouseState.', 'MouseState::')\nsdk=r"+chr(39)*3)
harness=harness.replace('struct Game{bool multi=false;', 'struct WheelFocus{bool focus=true;bool HasGameFocus(){return focus;}};struct Game{WheelFocus wheelFocus;WheelFocus& GetInput(){return wheelFocus;}int wheelTime=0;int GetTime(){return wheelTime;}bool multi=false;')
harness=harness.replace('static float Min(float a,float b)', 'static int AbsInt(int a){return std::abs(a);}static float Min(float a,float b)')
harness=harness.replace('constexpr int UAPrevAction=7,UANextAction=8;', 'enum class MouseState{WHEEL};int rawWheel=0;int GetMouseState(MouseState){return rawWheel;}constexpr int UAPrevAction=7,UANextAction=8;')
harness=harness.replace('void tick(Probe& p,MissionProbe& m,float dt,bool missionFirst){', 'void tick(Probe& p,MissionProbe& m,float dt,bool missionFirst){++game.wheelTime;p.MovementLabCaptureWheelTarget();')

harness=harness.replace('static float Min(float a,float b)', 'static float AbsFloat(float a){return std::abs(a);}static float Min(float a,float b)')

harness=harness.replace("source=source.replace('static bool Enabled;', 'inline static bool Enabled = false;')", "source=source.replace('static bool Enabled;', 'inline static bool Enabled = false;')")
harness=harness.replace('int BindVariableFloat(const char*){return 10;}', 'int BindVariableFloat(const char* n){if(std::string(n)=="MovementLabWalkLevel")return 11;if(std::string(n)=="MovementLabCrouchExitActive")return 12;if(std::string(n)=="MovementLabCrouchExitWeight")return 13;if(std::string(n)=="MovementLabAllSmoothActive")return 20;if(std::string(n)=="MovementLabWalkJogPose")return 21;if(std::string(n)=="MovementLabJogSprintPose")return 22;if(std::string(n)=="MovementLabWalkingPoseLevel")return 23;if(std::string(n)=="MovementLabJogRatePose")return 24;if(std::string(n)=="MovementLabCrouchPoseLevel")return 25;if(std::string(n)=="MovementLabLateralPose")return 26;if(std::string(n)=="MovementLabLateralActive")return 27;return 10;}')
harness=harness.replace('float animLevel=1;', 'float animLevel=1,animHalf=0,exitActive=0,exitWeight=0;std::array<float,8>poseVars={};')
harness=harness.replace('void AnimSetFloat(int,float v){animLevel=v;}', 'void AnimSetFloat(int id,float v){if(id==11)animHalf=v;else if(id==12)exitActive=v;else if(id==13)exitWeight=v;else if(id>=20&&id<28)poseVars[id-20]=v;else animLevel=v;}')
new_tests=r'''
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;float dt=1.f/fps;
  tick(p,m,dt,order);assert(p.m_MovementLabJogLevel==2 && p.animHalf==6);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode && p.m_MovementLabWalkLevel==1 && p.m_MovementLabJogLevel==2);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==2);
  api.a[7].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabWalkMode && p.m_MovementLabJogLevel==2 && p.animHalf==5);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabJogLevel==3 && !p.m_MovementLabScrollSprint && p.animHalf==2);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabScrollSprint && p.m_MovementLabJogLevel==3);
  ticks(p,m,fps,dt,order);assert(p.move.speed==3 && m.m_MovementLabSprintExposure>0);
  api.a[8].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabScrollSprint && p.m_MovementLabJogLevel==3);
  ticks(p,m,fps,dt,order);assert(p.move.speed==2);
  api.a[8].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabWalkMode && p.m_MovementLabJogLevel==2 && p.animHalf==5);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode && p.m_MovementLabWalkLevel==1);
  for(int i=0;i<100;i++){
   p.m_MovementLabWalkLevel=2;api.a[7].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabWalkMode && p.m_MovementLabJogLevel==2);
   api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode && p.m_MovementLabWalkLevel==1);
  }
  // Idle boundaries and retained native sprint full-stop envelope.
  api.a[0].value=0;p.m_MovementLabWalkLevel=2;api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabJogLevel==2 && !p.m_MovementLabWalkMode);
  api.a[0].value=1;api.a[7].press=true;tick(p,m,dt,order);api.a[7].press=true;tick(p,m,dt,order);
  ticks(p,m,fps,dt,order);api.a[0].value=0;tick(p,m,dt,order);assert(m.m_MovementLabBraking && m.m_MovementLabBrakeStart>2.9);
  ticks(p,m,2*fps,dt,order);assert(p.move.speed==0);
  p.stance=1;api.a[0].value=1;tick(p,m,dt,order);assert(!p.m_MovementLabScrollSprint);
  p.stance=0;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);
 }
'''
pose_tests=r'''
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;
  p.stance=1;api.a[0].value=1;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=6;tick(p,m,dt,order);assert(p.exitActive==0);
  p.m_MovementLabCrouchLevel=5;tick(p,m,dt,order);assert(p.exitActive==1 && p.exitWeight>.99f && p.move.speed==1);
  float last=p.exitWeight;
  for(int i=0;i<fps;i++){tick(p,m,dt,order);assert(p.exitWeight<=last+.00001f && p.exitWeight>=0);last=p.exitWeight;}
  assert(p.exitActive==0 && p.exitWeight==0);
  p.m_MovementLabCrouchLevel=6;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=5;tick(p,m,dt,order);
  float elapsed=p.m_MovementLabCrouchExitTime;p.MovementLabUpdateCrouchRules(dt,1);p.MovementLabUpdateCrouchRules(dt,1);assert(p.m_MovementLabCrouchExitTime==elapsed);
  api.a[6].value=1;tick(p,m,dt,order);assert(p.exitActive==0 && p.move.speed==3);
  api.a[6].value=0;tick(p,m,dt,order);assert(p.exitActive==1);
  p.m_MovementLabCrouchLevel=4;tick(p,m,dt,order);assert(p.exitActive==1);
  p.m_MovementLabCrouchLevel=6;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=5;tick(p,m,dt,order);api.a[0].value=0;tick(p,m,dt,order);assert(p.exitActive==0);
 }
'''
new_tests+=pose_tests
smooth_tests=r'''
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;api.a[0].value=1;
  tick(p,m,dt,order);assert(p.poseVars[0]==1);
  for(int i=0;i<fps*2;i++){tick(p,m,dt,order);for(int k:{1,2,4,6,7})assert(p.poseVars[k]>=0 && p.poseVars[k]<=1);}
  assert(p.poseVars[1]>.99f && p.poseVars[2]<.01f);
  // Native walking and jogging wheel profile selectors remain bounded and independent.
  p.m_MovementLabWalkMode=true;p.m_MovementLabWalkLevel=2;
  float previous=p.poseVars[3];
  for(int i=0;i<fps;i++){tick(p,m,dt,order);assert(p.poseVars[3]>=previous && p.poseVars[3]<=2);previous=p.poseVars[3];}
  assert(p.poseVars[3]>1.98f);
  p.m_MovementLabJogLevel=3;previous=p.poseVars[4];
  for(int i=0;i<fps;i++){tick(p,m,dt,order);assert(p.poseVars[4]>=previous && p.poseVars[4]<=1);previous=p.poseVars[4];}
  assert(p.poseVars[4]>.99f);
  // Lateral weights move continuously side-to-side without asking forward gait.
  p.move.angle=-90;ticks(p,m,fps,dt,order);assert(p.poseVars[6]<.02f && p.poseVars[7]>.99f);
  p.move.angle=90;tick(p,m,dt,order);assert(p.poseVars[6]>0 && p.poseVars[6]<1);
  ticks(p,m,fps,dt,order);assert(p.poseVars[6]>.99f);
  // Confirmed crouch87 exit preserved, and other lower tiers covered too.
  p.stance=1;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=6;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=3;
  tick(p,m,dt,order);assert(p.exitActive==1);
  assert(p.m_MovementLabCrouchPoseLevel>=3 && p.m_MovementLabCrouchPoseLevel<=5);
  ticks(p,m,2*fps,dt,order);assert(p.exitActive==0 && std::abs(p.poseVars[5]-3)<.01f);
  p.m_MovementLabCrouchLevel=1;previous=p.poseVars[5];
  for(int i=0;i<fps;i++){tick(p,m,dt,order);assert(p.poseVars[5]<=previous && p.poseVars[5]>=1);previous=p.poseVars[5];}
  assert(p.poseVars[5]<1.02f);
  MovementLabStartGate::Enabled=false;tick(p,m,dt,order);assert(p.poseVars[0]==0);
  MovementLabStartGate::Enabled=true;game.ui.menu=true;tick(p,m,dt,order);assert(p.poseVars[0]==0);
 }
'''
new_tests+=smooth_tests
target_tests=r'''
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};rawWheel=0;MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;api.a[0].value=1;p.m_MovementLabWalkMode=true;
  tick(p,m,dt,order);
  // Native achieved gait can drop to walking in one sample; pose must not snap.
  p.m_MovementLabPoseInitialised=true;p.m_MovementLabWalkJogPose=1;p.move.speed=1;
  p.MovementLabUpdateAllPoseSmoothing(dt,1);
  assert(p.m_MovementLabWalkJogPose>=1-dt/.45f-.00001f);
  // Persistent raw state alone must not advance any levels.
  rawWheel=1;ticks(p,m,10,dt,order);assert(p.m_MovementLabWalkLevel==1);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==2 && p.m_MovementLabWalkMode);
  ticks(p,m,10,dt,order);assert(p.m_MovementLabWalkLevel==2 && p.m_MovementLabWalkMode);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);
  // Four real edges queue full sprint before one simulation command.
  for(int i=0;i<4;i++){api.a[7].press=true;++game.wheelTime;p.MovementLabCaptureWheelTarget();}
  assert(p.m_MovementLabWheelPending==4);tick(p,m,dt,order);assert(p.m_MovementLabScrollSprint);
  ticks(p,m,2*fps,dt,order);assert(p.move.speed==3);
  api.a[8].press=true;tick(p,m,dt,order);tick(p,m,dt,order);assert(m.m_MovementLabBrakeTarget==2);
  for(int i=0;i<2;i++){api.a[8].press=true;++game.wheelTime;p.MovementLabCaptureWheelTarget();}
  tick(p,m,dt,order);tick(p,m,dt,order);assert(m.m_MovementLabBrakeTarget==1 && m.m_MovementLabBrakeDuration>.70f);
  ticks(p,m,2*fps,dt,order);assert(p.m_MovementLabWalkMode && p.move.speed==1);
  p.stance=1;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=1;
  for(int i=0;i<5;i++){api.a[7].press=true;++game.wheelTime;p.MovementLabCaptureWheelTarget();}
  tick(p,m,dt,order);assert(p.m_MovementLabCrouchLevel==6);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabCrouchLevel==5);
  ticks(p,m,2*fps,dt,order);assert(p.m_MovementLabCrouchLevel==5);
  game.ui.menu=true;api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWheelPending==0);api.a[7].press=false;
 }
'''
new_tests+=target_tests
harness=harness.replace(' std::cout<<',new_tests+' std::cout<<',1)
def method(text,name):
    match=re.search(r'\b(?:void|bool|float)\s+'+name+r'\([^)]*\)\s*\{',text)
    assert match,name
    return text[match.start():block_end(text,match.start())]
exec(compile(harness,'walk-level-controller-harness','exec'))


assert 'MovementLabUpdateStandingJogWheel' not in w
assert 'MovementLabIsScrollSprinting()' in (SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()

assert 'MovementLabCrouchExitWeight*MovementLabCrouchExitActive*(1-Injured)' in graph
prior=ROOT/'ctrl-mode-test/MovementLabScroll_JogSprint_v2'
for rel in ['WorkspacePatches/player_main.ast','WorkspacePatches/player_main.asi']:
 assert (SOURCE/rel).read_bytes()==(prior/rel).read_bytes()
assert method((prior/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text(),'MovementLabUpdateCrouchRules')==method((SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text(),'MovementLabUpdateCrouchRules')

# Current confirmed default package remains byte-identical.
assert hashlib.sha256((ROOT/'artifacts/MovementLab_Crouch_PoseExit_Test_v2.zip').read_bytes()).hexdigest()=='e1a6e4999c45abb0553f2e1dc187e9de091bdb49939effd49eecdc3614e024e3'
print('All movement pose variables, profile/lateral smoothness, confirmed exit and99 graph edits checked. Native visuals pending.')
# Every movement controller method from confirmed default remains identical except
# its command orchestration and broadened, already confirmed crouch exit helper.
confirmed=ROOT/'ctrl-mode-test/MovementLabCrouch_PoseExit_v2'
confirmed_world=(confirmed/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
current_world=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for match in re.finditer(r'\b(?:void|bool|float)\s+(\w+)\([^)]*\)\s*\{',confirmed_world):
    if match[1] not in ['CommandHandler','MovementLabApplyStandingWheelBoundaries','MovementLabUpdateAllPoseSmoothing','MovementLabUpdateCrouchPoseExit','MovementLabUpdateStandingWalkWheel','MovementLabUpdateCrouchWheel']:
        assert method(confirmed_world,match[1])==method(current_world,match[1]),match[1]
# Foot-phase conditions, transition clips/tags and destination offsets preserved.
confirmed_graph=(confirmed/'WorkspacePatches/locomotion.agr').read_text();confirmed_nodes=nodes(confirmed_graph)
for name,raw in confirmed_nodes.items():
    if '$Node AnimNodeStateMachine' not in raw:continue
    old_trans=[];new_trans=[]
    for target,output in [(raw,old_trans),(new[name],new_trans)]:
        for match in re.finditer(r'\$Transition\s*\{',target):
            tokens=re.findall(qpat,target[match.start():block_end(target,match.start())])
            output.append(tokens[:3]+tokens[4:])
    assert old_trans==new_trans,name
for name in ['WalkRunBlendT','WalkRunSprintBlendT','WalkRunSprintBlendTMLStandingWheel']:
    assert new[name+'MLOriginal']==confirmed_nodes[name].replace('"'+name+'"','"'+name+'MLOriginal"',1)
root=(SOURCE/'WorkspacePatches/player_main.agr').read_text()
for var in manifest['variables']:
    assert '#Var '+var+' float' in root
    assert 'BindVariableFloat("'+var+'")' in current_world
print('All default input/brake/stance rules, native transition phase conditions and graph bindings preserved.')

all_base=ROOT/'ctrl-mode-test/MovementLabAllPoseSmoothing_v1'
for rel in ['Smoothing-Coverage.json']:
 assert (SOURCE/rel).read_bytes()==(all_base/rel).read_bytes()
for file in (SOURCE/'WorkspacePatches').iterdir():
 assert file.read_bytes()==(all_base/'WorkspacePatches'/file.name).read_bytes()
base_world=(all_base/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for name in ['MovementLabUpdateCrouchPoseExit','MovementLabCommandStart','MovementLabUpdateCrouchRules']:
 assert method(current_world,name)==method(base_world,name),name
print('Counted bursts cross every boundary immediately; persistent targets settle without more input, frame dedup/menu and queued command tests passed.')


prior_frame_world=(ROOT/'ctrl-mode-test/MovementLabScroll_TargetQueue_v3/StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
assert 'GetMouseState' not in current_world


prior=(ROOT/'ctrl-mode-test/MovementLabScroll_TargetQueue_v6/StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for name in ['MovementLabCommandStart']:
 assert method(current_world,name)==method(prior,name)
assert 'm_MovementLabWalkLevel >= 3' in current_world
assert '@(0,24,30)' in prep
print('Walking80/native100/level3 jogging boundary verified; pose smoothing preserved.')

previous_world=(ROOT/'ctrl-mode-test/MovementLabScroll_TargetQueue_v8/StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for name in ['MovementLabCaptureWheelTarget','MovementLabCommandStart','MovementLabUpdateStandingWalkWheel','MovementLabUpdateCrouchRules']:
 assert method(previous_world,name)==method(current_world,name)
assert (SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes()==(ROOT/'ctrl-mode-test/MovementLabScroll_TargetQueue_v8/Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes()
print('Abrupt achieved-gait handoff bounded; v8 input and speed/brake requests unchanged.')
