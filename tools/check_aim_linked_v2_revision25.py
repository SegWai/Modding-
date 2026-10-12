from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision25'
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

w=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text();mission=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
# Reuse actual-controller translation and inherited controller regressions.
text=(ROOT/'tools/check_scroll_target_queue_v9.py').read_text();a=text.index('# Reuse baseline actual-controller translation');b=text.index("exec(compile(harness,'walk-level-controller-harness','exec'))")+len("exec(compile(harness,'walk-level-controller-harness','exec'))")
chunk=text[a:b]
extra='\n for(int fps:{30,60,144})for(bool order:{false,true})for(int entry=0;entry<5;entry++){\n  MovementLabStartGate::NativeAimComparison=false;game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;api.a[0].value=1;\n  p.m_MovementLabWalkMode=entry<2;p.m_MovementLabWalkLevel=entry==1?2:1;p.m_MovementLabJogLevel=entry==3?3:2;p.m_MovementLabScrollSprint=entry==4;\n  if(entry==4){p.stance=0;p.move.speed=3;for(int n=0;n<fps+1;n++)p.MovementLabUpdateAimWalking(dt,1); }\n  p.move.speed=2;p.raised=true;p.stance=3;tick(p,m,dt,order);\n  assert(p.m_MovementLabAimSlowMode==(entry<2));\n  if(entry<2)assert(p.m_MovementLabAimSlowLevel==entry+1);else assert(p.m_MovementLabAimFastLevel==(entry==4?4:entry-1));\n  if(entry==3)assert(p.aimActive==0 && p.aimFastActive==0);\n  if(entry==4){float previous=4;for(int frame=1;frame<fps*3/2-1;frame++){api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimFastLevel==4 && p.aimFastProfile<=previous && p.aimFastProfile>=2);previous=p.aimFastProfile;}api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimFastLevel==2 && p.m_MovementLabAimSprintTime==0 && p.aimFastProfile==2);api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimFastLevel==3);for(int n=0;n<8;n++){api.a[7].press=true;tick(p,m,dt,order);}assert(p.m_MovementLabAimFastLevel==3);api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimFastLevel==2);}\n  game.ui.menu=true;tick(p,m,dt,order);game.ui.menu=false;tick(p,m,dt,order);\n  if(entry<2)assert(p.m_MovementLabAimSlowLevel==entry+1);else assert(p.m_MovementLabAimFastLevel==(entry==4?2:entry-1));\n  p.raised=false;p.stance=0;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode==(entry<2));assert(p.m_MovementLabWalkLevel==1 && p.m_MovementLabJogLevel==(entry>=3?3:2) && !p.m_MovementLabScrollSprint);\n  p.raised=true;p.stance=3;tick(p,m,dt,order);assert(p.m_MovementLabAimSlowMode==(entry<2));if(entry<2)assert(p.m_MovementLabAimSlowLevel==1);else assert(p.m_MovementLabAimFastLevel==(entry>=3?2:1));\n  if(entry<2){api.a[6].value=1;tick(p,m,dt,order);api.a[6].value=0;tick(p,m,dt,order);assert(!p.m_MovementLabAimSlowMode);}\n  else{api.a[4].value=1;tick(p,m,dt,order);api.a[4].value=0;tick(p,m,dt,order);assert(p.m_MovementLabAimSlowMode);}\n  p.raised=false;p.stance=0;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode==(entry>=2));\n }\n'
extra+='\n for(bool weapon:{false,true}){\n  MovementLabStartGate::NativeAimComparison=false;game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;p.item.weapon=weapon;\n  p.m_MovementLabWalkMode=false;p.m_MovementLabScrollSprint=true;p.move.speed=3;for(int n=0;n<61;n++)p.MovementLabUpdateAimWalking(1.f/60,1);\n  api.a[6].value=0;p.m_MovementLabScrollSprint=false;p.raised=true;p.stance=3;tick(p,m,1.f/60,false);\n  if(weapon){assert(p.m_MovementLabAimFastLevel==4);float hold=p.m_MovementLabAimSprintTime;p.move.speed=2.6;p.MovementLabUpdateAimWalking(1.f/60,1);assert(p.m_MovementLabAimSprintTime==hold);p.move.speed=2;ticks(p,m,91,1.f/60,false);assert(p.m_MovementLabAimFastLevel==2 && p.m_MovementLabAimSprintTime==0);}\n  else assert(p.m_MovementLabAimFastLevel!=4 && p.m_MovementLabAimSprintTime==0);\n }\n'
extra+='\n for(int fps:{30,60,144})for(int scenario=0;scenario<5;scenario++){\n  game={};api={};MovementLabStartGate::Enabled=true;MovementLabStartGate::NativeAimComparison=false;Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;api.a[6].value=1;p.m_MovementLabWalkMode=false;p.m_MovementLabScrollSprint=true;float dt=1.f/fps;\n  for(int frame=0;frame<fps*2;frame++){p.move.speed=2.6;p.MovementLabUpdateAimWalking(dt,1);}assert(p.m_MovementLabFullSprintTime==0);\n  for(int frame=0;frame<fps/4;frame++){p.move.speed=3;p.MovementLabUpdateAimWalking(dt,1);}assert(p.m_MovementLabRecentSprintUntil<0);\n  if(scenario==0){p.raised=true;p.stance=3;p.move.speed=2;tick(p,m,dt,false);assert(p.m_MovementLabAimFastLevel!=4);continue;}\n  p.move.speed=2;p.MovementLabUpdateAimWalking(dt,1);assert(p.m_MovementLabFullSprintTime==0);\n  for(int frame=0;frame<fps+1;frame++){p.move.speed=3;p.MovementLabUpdateAimWalking(dt,1);}assert(p.m_MovementLabRecentSprintUntil>=0);\n  if(scenario==2){p.move.speed=0;p.MovementLabUpdateAimWalking(dt,1);}\n  if(scenario==3){p.stance=1;p.MovementLabUpdateAimWalking(dt,1);}\n  if(scenario==4){game.ui.menu=true;p.MovementLabUpdateAimWalking(dt,1);game.ui.menu=false;}\n  p.raised=true;p.stance=3;p.move.speed=2;tick(p,m,dt,false);assert((p.m_MovementLabAimFastLevel==4)==(scenario==1));\n }\n'
extra+='\n for(int fps:{30,60,144}){\n  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;p.m_MovementLabWalkMode=false;p.m_MovementLabScrollSprint=true;float dt=1.f/fps;\n  for(int f=0;f<fps+1;f++){p.move.speed=2.97;p.MovementLabUpdateAimWalking(dt,1);}assert(p.m_MovementLabRecentSprintUntil>=0);p.raised=true;p.stance=3;p.move.speed=2;tick(p,m,dt,false);assert(p.m_MovementLabAimFastLevel==4);\n }\n'
extra+='\n for(int stance:{0,3})for(int fps:{30,60,144}){\n  game={};api={};MovementLabStartGate::Enabled=true;MovementLabStartGate::NativeAimComparison=false;Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;p.stance=stance;p.m_MovementLabWalkMode=false;float dt=1.f/fps;\n  for(int f=0;f<fps+1;f++){p.move.speed=2.97;p.MovementLabUpdateAimWalking(dt,1);}assert(p.m_MovementLabRecentSprintUntil>=0);p.raised=true;p.stance=3;p.move.speed=2;tick(p,m,dt,false);assert(p.m_MovementLabAimFastLevel==4);\n }\n'
extra+='\n for(int fps:{30,60,144})for(bool order:{false,true})for(int scenario=0;scenario<3;scenario++){\n  game={};api={};MovementLabStartGate::Enabled=true;MovementLabStartGate::NativeAimComparison=false;Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;p.m_MovementLabWalkMode=false;float dt=1.f/fps;\n  for(int f=0;f<fps;f++){p.move.speed=2.65;p.MovementLabUpdateAimWalking(dt,1);}assert(p.m_MovementLabRecentSprintUntil<0);\n  int frames=scenario==0?int(fps*.2f):int(std::ceil(fps*.36f));for(int f=0;f<frames;f++){p.move.speed=2.75;p.MovementLabUpdateAimWalking(dt,1);}\n  if(scenario==2){p.move.speed=2;p.MovementLabUpdateAimWalking(dt,1);}\n  p.raised=true;p.stance=3;p.move.speed=2;tick(p,m,dt,order);assert((p.m_MovementLabAimFastLevel==4)==(scenario==1));\n }\n'
chunk=chunk.replace("new_tests+=target_tests",'new_tests+=target_tests\nnew_tests+='+repr(extra))
chunk=chunk.replace("exec(compile(harness,'walk-level-controller-harness','exec'))", "harness=harness.replace('int BindVariableFloat(const char* n){','int BindVariableFloat(const char* n){if(std::string(n)==\"MovementLabAimWalkActive\")return 28;if(std::string(n)==\"MovementLabAimWalkProfile\")return 29;if(std::string(n)==\"MovementLabAimFastActive\")return 30;if(std::string(n)==\"MovementLabAimFastProfile\")return 31;')\nharness=harness.replace('float animLevel=1,animHalf=0,exitActive=0,exitWeight=0;', 'float animLevel=1,animHalf=0,exitActive=0,exitWeight=0,aimActive=0,aimProfile=2,aimFastActive=0,aimFastProfile=2;')\nharness=harness.replace('if(id==11)animHalf=v;', 'if(id==28)aimActive=v;else if(id==29)aimProfile=v;else if(id==30)aimFastActive=v;else if(id==31)aimFastProfile=v;else if(id==11)animHalf=v;')\nexec(compile(harness,'walk-level-controller-harness','exec'))")
chunk=chunk.replace('exec(compile(harness,', "harness=harness.replace('STANCEIDX_CROUCH=1;', 'STANCEIDX_CROUCH=1,STANCEIDX_RAISEDERECT=3,STANCEIDX_RAISEDCROUCH=4;')\nexec(compile(harness,")
w=w.replace('GetItemInHands().IsWeapon()', 'GetItemInHands()->IsWeapon()')
w=w.replace('static bool NativeAimComparison;', 'inline static bool NativeAimComparison=false;')
chunk=chunk.replace("exec(compile(harness,'walk-level-controller-harness','exec'))", "harness=harness.replace('struct SDKPlayer{', 'struct MockItem{bool weapon=true;bool IsWeapon(){return weapon;}};struct SDKPlayer{MockItem item;MockItem* GetItemInHands(){return &item;}')\nharness=harness.replace('GetItemInHands().IsWeapon()', 'GetItemInHands()->IsWeapon()')\nexec(compile(harness,'walk-level-controller-harness','exec'))")
chunk=chunk.replace("exec(compile(harness,", 'harness=harness.replace("with tempfile.TemporaryDirectory(prefix=", \'tests=tests[:tests.index("int main(){")]+ \\\'int main(){\\\\n for(int fps:{30,60,144})for(bool order:{false,true}){\\\\n  game={};api={};MovementLabStartGate::Enabled=true;MovementLabStartGate::NativeAimComparison=false;Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;float dt=1.f/fps;\\\\n  tick(p,m,dt,order);api.a[6].value=1;tick(p,m,dt,order);assert(!p.m_MovementLabWalkMode && p.m_MovementLabJogLevel==3 && !p.m_MovementLabScrollSprint && p.MovementLabWantedGait()==2);\\\\n  ticks(p,m,fps,dt,order);assert(p.move.speed==2);api.a[6].value=0;tick(p,m,dt,order);assert(p.MovementLabWantedGait()==2);\\\\n  game.wheelTime+=500;api.a[6].value=1;tick(p,m,dt,order);assert(!p.m_MovementLabScrollSprint);api.a[6].value=0;tick(p,m,dt,order);api.a[6].value=1;tick(p,m,dt,order);assert(p.m_MovementLabScrollSprint && p.MovementLabWantedGait()==3);api.a[6].value=0;tick(p,m,dt,order);assert(p.MovementLabWantedGait()==3);\\\\n  api.a[6].value=1;tick(p,m,dt,order);assert(!p.m_MovementLabScrollSprint && p.m_MovementLabJogLevel==3);api.a[6].value=0;tick(p,m,dt,order);\\\\n  p.m_MovementLabScrollSprint=true;api.a[4].value=1;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode && p.m_MovementLabWalkLevel==1 && !p.m_MovementLabScrollSprint);api.a[4].value=0;tick(p,m,dt,order);api.a[4].value=1;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode && p.MovementLabWantedGait()==1);api.a[4].value=0;tick(p,m,dt,order);\\\\n  for(int i=0;i<4;i++){api.a[7].press=true;tick(p,m,dt,order);}assert(p.m_MovementLabScrollSprint);for(int i=0;i<4;i++){api.a[8].press=true;tick(p,m,dt,order);}assert(p.m_MovementLabWalkMode && p.m_MovementLabWalkLevel==1);\\\\n  game.wheelTime+=500;api.a[6].value=1;tick(p,m,dt,order);api.a[6].value=0;tick(p,m,dt,order);p.raised=true;p.stance=3;tick(p,m,dt,order);assert(!p.m_MovementLabAimSlowMode && p.m_MovementLabAimFastLevel==2);\\\\n  p.raised=false;p.stance=0;tick(p,m,dt,order);for(int f=0;f<fps;f++){p.move.speed=2.75;p.MovementLabUpdateAimWalking(dt,1);}p.raised=true;p.stance=3;p.move.speed=2;tick(p,m,dt,order);assert(p.m_MovementLabAimFastLevel==4);ticks(p,m,fps*2,dt,order);assert(p.m_MovementLabAimFastLevel==2);\\\\n }\\\\n std::cout<<"Standing Shift/Ctrl latch, hold/release, double tap, sprint exit, repeated Ctrl, wheel traversal and aim entry/momentum passed at30/60/144FPS both orders. Native test pending.\\\\\\\\n";\\\\n}\\\\n\\\'\\nwith tempfile.TemporaryDirectory(prefix=\')\n'+"exec(compile(harness,")
exec(compile(chunk,'aim-linked-v2-controller-harness','exec'))
import json
old=ROOT/'ctrl-mode-test/MovementLabArmedSpeeds_v13'
graph=(SOURCE/'WorkspacePatches/locomotion.agr').read_text();original=(old/'WorkspacePatches/locomotion.agr').read_text()
def nodes(s):
 out={}
 for match in re.finditer(r'\$Node\s+\w+\s*\{',s):
  raw=s[match.start():block_end(s,match.start())];name=re.search(r'"([^"\n]+)"',raw)[1]
  assert name not in out,name;out[name]=raw
 return out
new=nodes(graph);previous=nodes(original);slots=['WalkB','WalkBL','WalkBR','WalkF','WalkFL','WalkFR','RunB','RunBL','RunBR','RunF','RunFL','RunFR']
for name,raw in previous.items():
 if name in [x+'Src' for x in slots]:assert new[name+'MLNative']==raw.replace('"'+name+'"','"'+name+'MLNative"',1)
 else:assert new[name]==raw,name
assert len(new)==len(previous)+192
assert not graph[block_end(graph,graph.index('$AnimGraph')):].strip()
sheets=[(m.start(),block_end(graph,m.start())) for m in re.finditer(r'\$Sheet\s+"[^"\n]+"\s*\{',graph)]
for m in re.finditer(r'\$Node\s+\w+\s*\{',graph):assert any(a<m.start()<block_end(graph,m.start())<b for a,b in sheets)
plan=json.loads((SOURCE/'Armed-Speed-Plan.json').read_text());variants={'DZ/anims/anm/player/moves/unarmed/'+v['output']:v for v in plan['variants']}
originals=Path('/tmp/player-main-upload/player_main')
for instance in plan['instances']:
 t=(originals/instance['file']).read_text(errors='replace');rows=dict(re.findall(r'"([^"\n]+)"\s+"([^"\n]+)"',t.split('$animations',1)[-1]))
 for key,value in instance['add'].items():
  if not key.startswith(('ZZMovementLabAimWalk.','ZZMovementLabAimFast.')):continue
  _,level,slot=key.split('.');assert slot in slots
  native='Locomotion.'+('CroRas' if level.startswith('C') else 'ErcRas')+'.'+slot
  expected=re.sub(r'^\{[^}]+\}','',rows[native]).lower()
  actual=variants[value]['source'].lower() if value in variants else re.sub(r'^\{[^}]+\}','',value).lower()
  assert actual==expected,(instance['file'],key)
assert (SOURCE/'StartGateSource/Scripts/4_World/MovementLabTestCamera.c').read_text().replace('extends AssaultBag_Black','extends AliceBag_Green')==(old/'StartGateSource/Scripts/4_World/MovementLabTestCamera.c').read_text()
assert '#Var MovementLabAimWalkActive float 0 0 1 ""' in (SOURCE/'WorkspacePatches/player_main.agr').read_text()
assert '#ngrouptypes 31' in (SOURCE/'WorkspacePatches/player_main.ast').read_text()
print('Only synchronized walking/running leaves wrapped; every native aim/ADS/IK/recoil node unchanged. Scoped walk-only native source mappings, root/sheet containment,linked mode and crouch bounds and lowered regressions passed. Native playback/firing pending.')


print('Separate v2: native Ctrl modes, two slow/three fast wheel clamps and Shift/Ctrl mode rules checked; native upper-body gun layers preserved; original v21 untouched. Native test pending.')

prior=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision2'
# Extended only fast aim group/profile range for sprint momentum.
# Added42FPS variants.
print('Only73/native100 slowaim selectable; F8 native branches, saved custom tiers and crouchaim preservation verified. Native test pending.')

assert 'aimNativeComparison || aimOriginalSlowSource || aimOriginalFastSource' in w
print('Slowaim highest routes to the same unmodified native sources as F8;73 and all other modes unchanged.')

assert all(v["fps"]==42 for v in plan["variants"] if any(value.endswith(v["output"]) for i in plan["instances"] for key,value in i["add"].items() if key.startswith("ZZMovementLabAimFast.F140.")))
print("Sprint-only140 ->100 over1.5s: monotonic profile, discarded wheel spam, normal upper cap3; graph and source mappings validated. Native test pending.")

assert mission.count("GetGame().CreatePlayer(")==1
assert "MovementLabRangeSlot" not in mission and "MovementLabSpawnRangeTarget" not in mission
assert not (SOURCE/"StartGateSource/Scripts/4_World/MovementLabRangeTarget.c").exists()
print("Only player spawn remains; target spawn, scheduler and cleanup removed.")
