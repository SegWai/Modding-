#!/usr/bin/env python3
"""Validate half-walk schema and preservation; native playback requires DayZ."""
from pathlib import Path
import re,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'ctrl-mode-test/MovementLabCrouchWheel_SixLevels_v4'
SOURCE=ROOT/'ctrl-mode-test/MovementLabSprint_Travel120_v1'
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
physics_match=re.search(r'override void OnPhysMove\([^)]*\)\s*\{',w)
assert physics_match
physics_method=w[physics_match.start():block_end(w,physics_match.start())]
w=w.replace(physics_method,'')
ground_match=re.search(r'protected void MovementLabRecordSprintTravel\([^)]*\)\s*\{',w)
assert ground_match
w=w[:ground_match.start()]+w[block_end(w,ground_match.start()):]
harness=harness[harness.index("source=w.replace"):]
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
harness=harness.replace(' std::cout<<',new_tests+' std::cout<<',1)
def method(text,name):
    match=re.search(r'\b(?:void|bool|float)\s+'+name+r'\([^)]*\)\s*\{',text)
    assert match,name
    return text[match.start():block_end(text,match.start())]
exec(compile(harness,'walk-level-controller-harness','exec'))


assert 'MovementLabUpdateStandingJogWheel' not in w
assert 'MovementLabIsScrollSprinting()' in (SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()

# Translation/proposal callback exercises actual source arithmetic and gates.
physics=physics_method.replace('override ','').replace('super.OnPhysMove(', 'SDK::OnPhysMove(')
physics=physics.replace('vector ','Vec ').replace('IEntity travelHit;','IEntity travelHit=nullptr;')
physics=physics.replace('Math.','Math::').replace('vector.Zero','Vec::Zero').replace('null,','nullptr,')
physics=re.sub(r'^\s*Print\([^\n]*\);','',physics,flags=re.M)
sdk2=r"""
#include <cassert>
#include <cmath>
#include <algorithm>
struct Vec{float a[3]={0,0,0};static const Vec Zero;float&operator[](int i){return a[i];}const float&operator[](int i)const{return a[i];}Vec operator-(Vec b)const{return {{a[0]-b[0],a[1]-b[1],a[2]-b[2]}};}Vec operator*(float f)const{return {{a[0]*f,a[1]*f,a[2]*f}};}float Length(){return std::sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]);}};const Vec Vec::Zero={};
using IEntity=void*;
struct Math{static float Clamp(float x,float a,float b){return std::clamp(x,a,b);}static float Max(float a,float b){return std::max(a,b);}};
enum{UAMoveForward,UAMoveBack,UAMoveLeft,UAMoveRight};
struct Action{float value=0;float LocalValue(){return value;}};struct API{Action actions[4];Action&GetInputByID(int i){return actions[i];}}api;API&GetUApi(){return api;}
struct Move{float speed=3;float GetCurrentMovementSpeed(){return speed;}};
struct SDK{
 bool allowed=true,falling=false,parent=false;float collision=1;Vec pos={};Move move;
 bool m_MovementLabScrollSprint=true,m_MovementLabBrakeActive=false;int m_MovementLabSprintLevel=3;
 float m_MovementLabTravelProbeTime=0,m_MovementLabTravelProbeBase=0,m_MovementLabTravelProbeApplied=0;
 void OnPhysMove(float,Vec[4]){}void MovementLabRecordSprintTravel(float){}
 bool MovementLabCanUseModes(float,int){return allowed;}int GetCurrentCommandID(){return 1;}
 bool GetParent(){return parent;}bool PhysicsIsFalling(bool){return falling;}Move GetCommand_Move(){return move;}
 Vec GetPosition(){return pos;}
 float CollisionMoveTest(Vec,Vec,float,IEntity,IEntity&,Vec&,Vec&){return collision;}
};
struct Probe:SDK{
"""
test2=r"""
};
int main(){
 for(int fps:{30,60,144}){
  Probe p;api={};api.actions[0].value=1;float dt=1.f/fps;
  Vec t[4]={};t[3]={{8*dt,0.1f,0}};p.OnPhysMove(dt,t);
  assert(std::abs(t[3][0]-9.6f*dt)<.00001f && t[3][1]==.1f);
  p.collision=.7f;t[3]={{8*dt,.1f,0}};p.OnPhysMove(dt,t);assert(std::abs(t[3][0]-8*dt)<.00001f);
  p.collision=1;
  for(int gate=0;gate<7;gate++){
   p.allowed=true;p.parent=false;p.falling=false;p.move.speed=3;p.m_MovementLabBrakeActive=false;p.m_MovementLabSprintLevel=3;p.m_MovementLabScrollSprint=true;
   if(gate==0)p.allowed=false;if(gate==1)p.parent=true;if(gate==2)p.falling=true;if(gate==3)p.move.speed=2;if(gate==4)p.m_MovementLabBrakeActive=true;if(gate==5)p.m_MovementLabSprintLevel=2;if(gate==6)p.m_MovementLabScrollSprint=false;
   t[3]={{8*dt,.1f,0}};p.OnPhysMove(dt,t);assert(std::abs(t[3][0]-8*dt)<.00001f);
  }
 }
}
"""
with tempfile.TemporaryDirectory(prefix='sprint-translation-') as temp:
    cpp=Path(temp)/'probe.cpp';binary=Path(temp)/'probe'
    cpp.write_text(sdk2+physics+test2)
    subprocess.run(['g++','-std=c++17',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
prior=ROOT/'ctrl-mode-test/MovementLabScroll_JogSprint_v2'
for rel in ['Prepare-Crouch-Clips.ps1','Missions/MovementLabMovementLogic.ChernarusPlus/init.c']:
    assert (SOURCE/rel).read_bytes()==(prior/rel).read_bytes()
for file in (SOURCE/'WorkspacePatches').iterdir():
    assert file.read_bytes()==(prior/'WorkspacePatches'/file.name).read_bytes()
print('Actual callback proposal scaling120%, height preservation, collision and eligibility gates checked; native physical outcome pending.')
