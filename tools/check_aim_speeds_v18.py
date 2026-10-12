from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Speeds_v18'
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
extra=r'''
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;p.raised=true;api.a[0].value=1;p.m_MovementLabWalkMode=true;
  tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==2 && p.m_MovementLabWalkMode);
  api.a[7].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabWalkMode && p.m_MovementLabJogLevel==2);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabJogLevel==3);
  for(int i=0;i<20;i++){api.a[7].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabScrollSprint && p.m_MovementLabJogLevel==3);}
  api.a[6].value=1;ticks(p,m,fps,dt,order);assert(p.move.speed==2);
  api.a[8].press=true;tick(p,m,dt,order);api.a[8].press=true;tick(p,m,dt,order);ticks(p,m,2*fps,dt,order);assert(p.m_MovementLabWalkMode && p.move.speed==1);
  p.stance=1;tick(p,m,dt,order);assert(p.m_MovementLabCrouchLevel==3);
  for(int i=0;i<20;i++){api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabCrouchLevel<=5);}
  ticks(p,m,fps,dt,order);assert(p.move.speed==1 && p.animLevel==5);
  for(int i=0;i<20;i++){api.a[8].press=true;tick(p,m,dt,order);}
  assert(p.m_MovementLabCrouchLevel==1 && p.move.speed==1);
 }
'''
chunk=chunk.replace("new_tests+=target_tests",'new_tests+=target_tests\nnew_tests+='+repr(extra))
exec(compile(chunk,'aim-controller-harness','exec'))
plan=json.loads((SOURCE/'Armed-Speed-Plan.json').read_text());v={'DZ/anims/anm/player/moves/unarmed/'+x['output']:x for x in plan['variants']};original=Path('/tmp/player-main-upload/player_main')
for item in plan['instances']:
 s=(original/item['file']).read_text(errors='replace');rows=dict(re.findall(r'"([^"\n]+)"\s+"([^"\n]+)"',s.split('$animations',1)[-1]))
 for key,value in item['add'].items():
  prefix,level,slot=key.split('.')
  groups={'ZZMovementLabStandingAim':'ErcRas','ZZMovementLabCrouchAim':'CroRas','ZZMovementLabStandingWalk':'Erc','ZZMovementLabCrouchSpeeds':'Cro'}
  native='Locomotion.'+groups[prefix]+'.'+slot
  assert native in rows,(item['file'],key)
  raw=re.sub(r'^\{[^}]+\}','',rows[native]).lower()
  if value in v:assert v[value]['source'].lower()==raw
  else:assert value==rows[native]
ast=(SOURCE/'WorkspacePatches/player_main.ast').read_text();assert '#ngrouptypes 31' in ast
assert 'ZZMovementLabCrouchAim' in ast and 'ZZMovementLabStandingAim' in ast
old=ROOT/'ctrl-mode-test/MovementLabArmedSpeeds_v13'
for name in ['player_main.agr']:
 assert (SOURCE/'WorkspacePatches'/name).read_bytes()==(old/'WorkspacePatches'/name).read_bytes()
assert (SOURCE/'StartGateSource/Scripts/4_World/MovementLabTestCamera.c').read_bytes()==(old/'StartGateSource/Scripts/4_World/MovementLabTestCamera.c').read_bytes()
print('Raised walk/jog bounds, Shift cap and all five crouch tiers passed30/60/144FPS both orders; per-item raised native source mappings verified; no new camera changes. Native aim/fire verification pending.')

graph=(SOURCE/'WorkspacePatches/locomotion.agr').read_text()
root_end=block_end(graph,graph.index('$AnimGraph'))
assert not graph[root_end:].strip(), 'Content outside graph root'
node_spans=[]
sheet_spans=[(m.start(),block_end(graph,m.start())) for m in re.finditer(r'\$Sheet\s+"[^"\n]+"\s*\{',graph)]
for match in re.finditer(r'\$Node\s+\w+\s*\{',graph):
 stop=block_end(graph,match.start())
 assert any(a<match.start()<stop<b for a,b in sheet_spans),'Node outside sheet'
 node_spans.append((match.start(),stop))
assert len(node_spans)>100
assert 'override protected void RegisterPluginDebug' in (SOURCE/'StartGateSource/Scripts/4_World/MovementLabDiagnosticInventory.c').read_text()
print('All graph nodes inside root and sheet; no trailing declarations. Native diagnostic plugin registration fix needs game verification.')

old_graph=(ROOT/'ctrl-mode-test/MovementLabAim_Speeds_v17/WorkspacePatches/locomotion.agr').read_text()
assert old_graph[block_end(old_graph,old_graph.index('$AnimGraph')):].strip(), 'Old graph must fail root-scope regression'
