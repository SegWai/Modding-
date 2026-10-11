#!/usr/bin/env python3
"""Validate half-walk schema and preservation; native playback requires DayZ."""
from pathlib import Path
import re,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'ctrl-mode-test/MovementLabCrouchWheel_SixLevels_v4'
SOURCE=ROOT/'ctrl-mode-test/MovementLabStandingWalk_ThreeLevels_v1'
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
assert columns['ZZMovementLabStandingWalk']==(['L1','L2'],['WalkB','WalkBL','WalkBR','WalkF','WalkFL','WalkFR'])
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
changed={'Walk'+d+'Src' for d in ['B','BL','BR','F','FL','FR']}
assert len(new)==len(old)+30
for name,raw in old.items():
 if name not in changed:assert new[name]==raw,name
for name in changed:
 d=name[4:-3]
 assert '1 + (MovementLabWalkLevel - 1) * (Stance == 0)' in new[name]
 assert '1.0 "'+name+'MLNative"' in new[name]
 assert '2.0 "'+name+'MLL2G"' in new[name]
 assert '3.0 "'+name+'MLL1G"' in new[name]
 assert new[name+'MLNative']==old[name].replace('"'+name+'"','"'+name+'MLNative"',1)
 for level in [1,2]:
  assert '"ZZMovementLabStandingWalk" "L'+str(level)+'"' in new[name+'MLL'+str(level)+'G']
  assert '"ZZMovementLabStandingWalk.Walk'+d+'"' in new[name+'MLL'+str(level)]
  assert mapping['ZZMovementLabStandingWalk.L'+str(level)+'.Walk'+d].endswith('/StandingWalkVariants/L'+str(level)+'/p_erc_walk'+d+'.anm')
# World logic changes confined to graph binding; all existing movement methods preserved.
w=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text();bw=(BASE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for m in re.finditer(r'\b(?:void|bool|float)\s+(\w+)\([^)]*\)\s*\{',bw):
 if m[1]!='CommandHandler':assert bw[m.start():block_end(bw,m.start())] in w,m[1]
assert 'm_MovementLabWalkLevel = 1;' in w and 'BindVariableFloat("MovementLabWalkLevel")' in w
assert 'HalfWalk' not in w
mission=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
assert 'KC_F8' not in mission and 'HalfWalk' not in mission
# Every mission movement/brake method stays identical.
bm=(BASE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
for m in re.finditer(r'\b(?:void|bool|float)\s+(\w+)\([^)]*\)\s*\{',bm):
 if m[1]!='OnKeyPress':assert bm[m.start():block_end(bm,m.start())] in mission,m[1]
prep=(SOURCE/'Prepare-Crouch-Clips.ps1').read_text()
assert '$movementlabWalkOriginal.Clone()' in prep and '@(0,21,26)' in prep
assert 'StandingWalkVariants\\L$movementlabWalkTier\\$movementlabWalkName' in prep
# Actual supplied ANM demonstrates the byte-level retiming invariant.
clip=Path('/workspace/attachments/d8337ae6-7dd3-447d-95fb-a0d800ada321/p_cro_walkf.anm').read_bytes()
assert clip[:4]==b'FORM' and clip[8:16]==b'ANIMSET6' and struct.unpack_from('<I',clip,28)[0]==30
for fps in [21,26]:
    variant=bytearray(clip);struct.pack_into('<I',variant,28,fps)
    assert variant[:28]==clip[:28] and variant[32:]==clip[32:]
    assert struct.unpack_from('<I',variant,28)[0]==fps
assert 21/30==0.7 and abs(26/30-0.85)<0.017
# Fixed approved package integrity.
assert hashlib.sha256((ROOT/'artifacts/MovementLab_Crouch_Wheel_Six_Levels_v4.zip').read_bytes()).hexdigest()=='bfee1d3ff3f45fdb38baee99eb6f33379d7ccaf582147265150b0eae3bb0544d'
print('Three walking tiers, default70%, mapping/schema and preserved baseline verified. Native runtime pending.')
# Reuse baseline actual-controller translation with this variant's World code.
# Distinct graph bindings ensure F8 cannot overwrite the crouch level variable.
import subprocess,tempfile
b=(ROOT/'movement-logic-test/MovementLabMovementLogicTest/Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
m=mission
harness=(ROOT/'tools/check_crouch_wheel_six_levels_v4.py').read_text()
harness=harness[harness.index("source=w.replace"):]
harness=harness.replace("source=source.replace('static bool Enabled;', 'inline static bool Enabled = false;')", "source=source.replace('static bool Enabled;', 'inline static bool Enabled = false;')")
harness=harness.replace('int BindVariableFloat(const char*){return 10;}', 'int BindVariableFloat(const char* n){return std::string(n)=="MovementLabWalkLevel"?11:10;}')
harness=harness.replace('float animLevel=1;', 'float animLevel=1,animHalf=0;')
harness=harness.replace('void AnimSetFloat(int,float v){animLevel=v;}', 'void AnimSetFloat(int id,float v){if(id==11)animHalf=v;else animLevel=v;}')
new_tests=r'''
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;
  Probe p;MissionProbe m;game.player=&p;api.a[0].value=1;p.m_MovementLabWalkMode=true;
  float dt=1.f/fps;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1 && p.animHalf==3);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==2 && p.animHalf==2);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==3 && p.animHalf==1);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==3);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==2);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);
  api.a[8].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);
  // Crouch wheel is independent and standing selection resets on exit.
  p.m_MovementLabWalkLevel=3;p.stance=1;tick(p,m,dt,order);assert(p.animLevel==3);
  api.a[7].press=true;tick(p,m,dt,order);assert(p.animLevel==4 && p.m_MovementLabWalkLevel==3);
  p.stance=0;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1 && p.animHalf==3);
  // Jogging/Shift do not consume wheel input for walking.
  p.m_MovementLabWalkMode=false;api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);api.a[7].press=false;
  p.m_MovementLabWalkMode=true;api.a[6].value=1;api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);api.a[7].press=false;
  api.a[6].value=0;game.ui.menu=true;api.a[7].press=true;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1);api.a[7].press=false;game.ui.menu=false;
  MovementLabStartGate::Enabled=false;tick(p,m,dt,order);assert(p.animHalf==1);
  // Reset every prior standing level after both slow and fast crouch.
  MovementLabStartGate::Enabled=true;
  for(int level:{1,2,3})for(int cro:{3,6}){
   p.stance=1;tick(p,m,dt,order);p.m_MovementLabCrouchLevel=cro;p.m_MovementLabWalkLevel=level;tick(p,m,dt,order);
   p.stance=0;tick(p,m,dt,order);assert(p.m_MovementLabWalkLevel==1 && p.animHalf==3);
  }
 }
'''
harness=harness.replace(' std::cout<<',new_tests+' std::cout<<',1)
def method(text,name):
    match=re.search(r'\b(?:void|bool|float)\s+'+name+r'\([^)]*\)\s*\{',text)
    assert match,name
    return text[match.start():block_end(text,match.start())]
exec(compile(harness,'walk-level-controller-harness','exec'))
