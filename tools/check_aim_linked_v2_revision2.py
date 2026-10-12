from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision2'
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
extra='\n for(int fps:{30,60,144})for(bool order:{false,true}){\n  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;api.a[0].value=1;p.raised=true;p.stance=3;\n  tick(p,m,dt,order);assert(!p.m_MovementLabAimSlowMode && p.m_MovementLabAimFastLevel==2 && p.move.speed==2);\n  api.a[4].value=1;tick(p,m,dt,order);assert(p.m_MovementLabAimSlowMode && p.m_MovementLabAimSlowLevel==3 && p.move.speed==1);\n  api.a[4].value=0;tick(p,m,dt,order);ticks(p,m,fps,dt,order);assert(p.aimProfile>2.96f && p.aimProfile<3.04f);\n  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimSlowLevel==2);\n  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimSlowLevel==1);\n  for(int level=2;level<=5;level++){api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimSlowMode && p.m_MovementLabAimSlowLevel==level);}\n  api.a[7].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabAimSlowMode && p.m_MovementLabAimFastLevel==1);\n  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimFastLevel==2);\n  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimFastLevel==3);\n  for(int i=0;i<20;i++){api.a[7].press=true;tick(p,m,dt,order);}assert(p.m_MovementLabAimFastLevel==3);\n  ticks(p,m,fps,dt,order);assert(p.aimFastProfile>2.96f && p.move.speed==2);\n  for(int level=2;level>=1;level--){api.a[8].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabAimSlowMode && p.m_MovementLabAimFastLevel==level);}\n  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabAimSlowMode && p.m_MovementLabAimSlowLevel==3);\n  for(int i=0;i<20;i++){api.a[8].press=true;tick(p,m,dt,order);}assert(p.m_MovementLabAimSlowLevel==1);\n  api.a[4].value=1;tick(p,m,dt,order);assert(!p.m_MovementLabAimSlowMode && p.m_MovementLabAimFastLevel==2);\n  api.a[4].value=0;tick(p,m,dt,order);api.a[4].value=1;tick(p,m,dt,order);assert(p.m_MovementLabAimSlowMode && p.m_MovementLabAimSlowLevel==3);api.a[4].value=0;\n  p.stance=4;tick(p,m,dt,order);assert(p.m_MovementLabAimCrouchLevel==3 && p.aimProfile==8 && p.move.speed==1 && p.aimFastActive==0);\n  for(int i=0;i<20;i++){api.a[7].press=true;tick(p,m,dt,order);}assert(p.m_MovementLabAimCrouchLevel==5);\n  for(int i=0;i<20;i++){api.a[8].press=true;tick(p,m,dt,order);}assert(p.m_MovementLabAimCrouchLevel==1);\n  p.raised=false;p.stance=1;tick(p,m,dt,order);assert(p.aimActive==0 && p.aimFastActive==0 && !p.m_MovementLabAimOwnsSpeed);\n }\n'
chunk=chunk.replace("new_tests+=target_tests",'new_tests+=target_tests\nnew_tests+='+repr(extra))
chunk=chunk.replace("exec(compile(harness,'walk-level-controller-harness','exec'))", "harness=harness.replace('int BindVariableFloat(const char* n){','int BindVariableFloat(const char* n){if(std::string(n)==\"MovementLabAimWalkActive\")return 28;if(std::string(n)==\"MovementLabAimWalkProfile\")return 29;if(std::string(n)==\"MovementLabAimFastActive\")return 30;if(std::string(n)==\"MovementLabAimFastProfile\")return 31;')\nharness=harness.replace('float animLevel=1,animHalf=0,exitActive=0,exitWeight=0;', 'float animLevel=1,animHalf=0,exitActive=0,exitWeight=0,aimActive=0,aimProfile=2,aimFastActive=0,aimFastProfile=2;')\nharness=harness.replace('if(id==11)animHalf=v;', 'if(id==28)aimActive=v;else if(id==29)aimProfile=v;else if(id==30)aimFastActive=v;else if(id==31)aimFastProfile=v;else if(id==11)animHalf=v;')\nexec(compile(harness,'walk-level-controller-harness','exec'))")
chunk=chunk.replace('exec(compile(harness,', "harness=harness.replace('STANCEIDX_CROUCH=1;', 'STANCEIDX_CROUCH=1,STANCEIDX_RAISEDERECT=3,STANCEIDX_RAISEDCROUCH=4;')\nexec(compile(harness,")
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
assert len(new)==len(previous)+180
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
assert (SOURCE/'StartGateSource/Scripts/4_World/MovementLabTestCamera.c').read_bytes()==(old/'StartGateSource/Scripts/4_World/MovementLabTestCamera.c').read_bytes()
assert '#Var MovementLabAimWalkActive float 0 0 1 ""' in (SOURCE/'WorkspacePatches/player_main.agr').read_text()
assert '#ngrouptypes 31' in (SOURCE/'WorkspacePatches/player_main.ast').read_text()
print('Only synchronized walking/running leaves wrapped; every native aim/ADS/IK/recoil node unchanged. Scoped walk-only native source mappings, root/sheet containment,linked mode and crouch bounds and lowered regressions passed. Native playback/firing pending.')


print('Separate v2: native Ctrl modes, five slow/three fast wheel steps and transient101/99 boundaries checked; native upper-body gun layers preserved; original v21 untouched. Native test pending.')
