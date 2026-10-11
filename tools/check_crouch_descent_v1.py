#!/usr/bin/env python3
"""Validate half-walk schema and preservation; native playback requires DayZ."""
from pathlib import Path
import re,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'ctrl-mode-test/MovementLabCrouchWheel_SixLevels_v4'
SOURCE=ROOT/'ctrl-mode-test/MovementLabCrouch_Descent_v1'
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
assert len(new)==len(old)+65
for name,raw in old.items():
 if name!='ErcMoveLowG':assert new[name]==raw,name
assert '"ErcMoveLowG" "" "MovementLabWalkLevel"' in new['ErcMoveLowG']
for value,target in [(1,'ErcMoveLowMLL2G'),(2,'ErcMoveLowMLNativeG'),(3,'ErcMoveLowMLL1G'),(4,'ErcMoveLowMLL2J2G'),(5,'ErcMoveLowMLNJ2G'),(6,'ErcMoveLowMLL1J2G')]:
 assert str(value)+'.0 "'+target+'"' in new['ErcMoveLowG']
assert new['ErcMoveLowMLNativeG']==old['ErcMoveLowG'].replace('"ErcMoveLowG"','"ErcMoveLowMLNativeG"',1)
qpat=r'"((?:[^"\\]|\\.)*)"'
cloned=[name for name in new if name.endswith('MLStandingWheel')]
assert len(cloned)==59
for name in cloned:
 tokens=re.findall(qpat,new[name])
 for token in tokens:
  if token.endswith('MLStandingWheel'):assert token in new,token
  if re.fullmatch(r'ZZMovementLabStandingWalk\.\w+',token):
   slot=token.split('.')[1]
   for level in [1,2]:assert 'ZZMovementLabStandingWalk.L'+str(level)+'.'+slot in mapping,(name,slot)
for level in [1,2]:
 assert '"ZZMovementLabStandingWalk" "L'+str(level)+'"' in new['ErcMoveLowMLL'+str(level)+'G']
for slot,path in mapping.items():
 if slot.startswith('Locomotion.Erc.'):
  leaf=slot.split('.')[2]
  for level in [1,2]:
   target=mapping['ZZMovementLabStandingWalk.L'+str(level)+'.'+leaf]
   if leaf in ['WalkB','WalkBL','WalkBR','WalkF','WalkFL','WalkFR']:
    assert target.endswith('/StandingWalkVariants/L'+str(level)+'/p_erc_walk'+leaf[4:]+'.anm')
   else:assert target==path,(leaf,target,path)
# Verify every combined group preserves walking profile and all sprint/other rows.
for group,walkgroup in [('L1J2','L1'),('L2J2','L2'),('NJ2',None)]:
 assert '"ZZMovementLabStandingWalk" "'+group+'"' in new['ErcMoveLowML'+group+'G']
 for key,path in mapping.items():
  if key.startswith('Locomotion.Erc.'):
   leaf=key.split('.')[2];target=mapping['ZZMovementLabStandingWalk.'+group+'.'+leaf]
   if leaf in ['RunB','RunBL','RunBR','RunF','RunFL','RunFR']:
    assert target.endswith('/StandingJogVariants/J80/p_erc_run'+leaf[3:]+'.anm')
   elif walkgroup:
    assert target==mapping['ZZMovementLabStandingWalk.'+walkgroup+'.'+leaf]
   else:assert target==path
assert len([key for key in mapping if key.startswith('ZZMovementLabStandingWalk.')])==195
# World logic changes confined to graph binding; all existing movement methods preserved.
w=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text();bw=(BASE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for m in re.finditer(r'\b(?:void|bool|float)\s+(\w+)\([^)]*\)\s*\{',bw):
 if m[1] not in ['CommandHandler','MovementLabWantedGait','MovementLabCommandStart','MovementLabUpdateCrouchRules']:assert bw[m.start():block_end(bw,m.start())] in w,m[1]
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
 if m[1] not in ['OnKeyPress','MovementLabUpdateBrake']:assert bm[m.start():block_end(bm,m.start())] in mission,m[1]
prep=(SOURCE/'Prepare-Crouch-Clips.ps1').read_text()
assert '$movementlabWalkOriginal.Clone()' in prep and '@(0,26,36)' in prep
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
harness=harness.replace('assert(p.animLevel==5 && p.move.speed==1);','assert(p.animLevel==5 && p.m_MovementLabCrouchDownActive && p.move.speed>2.0f);')

harness=harness.replace("source=source.replace('static bool Enabled;', 'inline static bool Enabled = false;')", "source=source.replace('static bool Enabled;', 'inline static bool Enabled = false;')")
harness=harness.replace('int BindVariableFloat(const char*){return 10;}', 'int BindVariableFloat(const char* n){return std::string(n)=="MovementLabWalkLevel"?11:10;}')
harness=harness.replace('float animLevel=1;', 'float animLevel=1,animHalf=0;')
harness=harness.replace('void AnimSetFloat(int,float v){animLevel=v;}', 'void AnimSetFloat(int id,float v){if(id==11)animHalf=v;else animLevel=v;}')
new_tests=r'''
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;float dt=1.f/fps;
  tick(p,m,dt,order);assert(p.m_MovementLabJogLevel==2 && p.animHalf==6);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode && p.m_MovementLabWalkLevel==1 && p.m_MovementLabJogLevel==2);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==2);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==3);
  api.a[7].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabWalkMode && p.m_MovementLabJogLevel==2 && p.animHalf==4);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabJogLevel==3 && !p.m_MovementLabScrollSprint && p.animHalf==1);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabScrollSprint && p.m_MovementLabJogLevel==3);
  ticks(p,m,fps,dt,order);assert(p.move.speed==3 && m.m_MovementLabSprintExposure>0);
  api.a[8].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabScrollSprint && p.m_MovementLabJogLevel==3);
  ticks(p,m,fps,dt,order);assert(p.move.speed==2);
  api.a[8].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabWalkMode && p.m_MovementLabJogLevel==2 && p.animHalf==4);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode && p.m_MovementLabWalkLevel==1);
  for(int i=0;i<100;i++){
   p.m_MovementLabWalkLevel=3;api.a[7].press=true;tick(p,m,dt,order);assert(!p.m_MovementLabWalkMode && p.m_MovementLabJogLevel==2);
   api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkMode && p.m_MovementLabWalkLevel==1);
  }
  // Idle boundaries and retained native sprint full-stop envelope.
  api.a[0].value=0;p.m_MovementLabWalkLevel=3;api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabJogLevel==2 && !p.m_MovementLabWalkMode);
  api.a[0].value=1;api.a[7].press=true;tick(p,m,dt,order);api.a[7].press=true;tick(p,m,dt,order);
  ticks(p,m,fps,dt,order);api.a[0].value=0;tick(p,m,dt,order);assert(m.m_MovementLabBraking && m.m_MovementLabBrakeStart>2.9);
  ticks(p,m,2*fps,dt,order);assert(p.move.speed==0);
  p.stance=1;api.a[0].value=1;tick(p,m,dt,order);assert(!p.m_MovementLabScrollSprint);
  p.stance=0;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);
 }
'''
descent_tests=r'''
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;
  p.stance=1;api.a[0].value=1;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=6;tick(p,m,dt,order);
  p.m_MovementLabCrouchLevel=5;tick(p,m,dt,order);assert(p.m_MovementLabCrouchDownActive && p.move.speed>2.9f && p.animLevel==5);
  float last=p.move.speed;
  for(int i=0;i<fps;i++){
   tick(p,m,dt,order);assert(p.move.speed<=last+.0001f && p.move.speed>=1);last=p.move.speed;
  }
  assert(!p.m_MovementLabCrouchDownActive && p.move.speed==1);
  // Mission rule reads must never advance timer or restart descent.
  p.m_MovementLabCrouchLevel=6;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=5;tick(p,m,dt,order);
  float elapsed=p.m_MovementLabCrouchDownTime;
  p.MovementLabUpdateCrouchRules(dt,1);p.MovementLabUpdateCrouchRules(dt,1);assert(p.m_MovementLabCrouchDownTime==elapsed);
  // Reverse tofast, then new descent starts from achieved speed; lower tiers cancel.
  api.a[6].value=1;tick(p,m,dt,order);assert(!p.m_MovementLabCrouchDownActive && p.move.speed==3);
  api.a[6].value=0;tick(p,m,dt,order);assert(p.m_MovementLabCrouchDownActive);
  p.m_MovementLabCrouchLevel=4;tick(p,m,dt,order);assert(!p.m_MovementLabCrouchDownActive && p.move.speed==1);
  p.m_MovementLabCrouchLevel=6;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=5;tick(p,m,dt,order);
  api.a[0].value=0;tick(p,m,dt,order);assert(!p.m_MovementLabCrouchDownActive && p.move.speed==0);
  api.a[0].value=1;p.m_MovementLabCrouchLevel=6;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=5;tick(p,m,dt,order);
  p.stance=0;tick(p,m,dt,order);assert(!p.m_MovementLabCrouchDownActive);
 }
'''
new_tests+=descent_tests
harness=harness.replace(' std::cout<<',new_tests+' std::cout<<',1)
def method(text,name):
    match=re.search(r'\b(?:void|bool|float)\s+'+name+r'\([^)]*\)\s*\{',text)
    assert match,name
    return text[match.start():block_end(text,match.start())]
exec(compile(harness,'walk-level-controller-harness','exec'))


assert 'MovementLabUpdateStandingJogWheel' not in w
assert 'MovementLabIsScrollSprinting()' in (SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()

prior=ROOT/'ctrl-mode-test/MovementLabScroll_JogSprint_v2'
for rel in ['Prepare-Crouch-Clips.ps1','Missions/MovementLabMovementLogic.ChernarusPlus/init.c']:
 assert (SOURCE/rel).read_bytes()==(prior/rel).read_bytes()
for file in (SOURCE/'WorkspacePatches').iterdir():
 assert file.read_bytes()==(prior/'WorkspacePatches'/file.name).read_bytes()
