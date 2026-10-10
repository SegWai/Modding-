#!/usr/bin/env python3
"""Exercise actual native reversal/controller methods with a mocked SDK.
No native Enforce/graph compilation or animation claims.
"""
from pathlib import Path
import re, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'movement-logic-test/MovementLabMovementLogicTest'
variant=ROOT/'movement-logic-experiments/MovementLabMovementLogicTest_v17a'
world=variant/'StartGateSource/Scripts/4_World'
def method(text,name):
    m=re.search(r'\b(?:void|bool|float)\s+'+name+r'\([^)]*\)\s*\{',text)
    assert m,name
    start=m.start();i=text.index('{',start)+1;depth=1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]
w=(world/'MovementLabStartGate.c').read_text()
b=(base/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for name in ['MovementLabCancelStart','MovementLabSetBrakingActive','MovementLabIsStarting','MovementLabGetStartSpeed','MovementLabCommandStart']:
    assert method(w,name)==method(b,name)
for prohibited in ['StartCommand_Script','PreAnim_','PrePhys_','CMD_SlidingPose','ModCommandHandlerInside']:
    assert prohibited not in w
mission=(variant/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text().replace('[MovementLab v17a / v11 base]','[MovementLab v11]')
old=(base/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
for name in ['MovementLabCancelStart','MovementLabCancelBrake','MovementLabBeginBrake','MovementLabApplyFilters','OnInit','OnMissionFinish']:
    assert method(mission,name)==method(old,name)
new_update=method(mission,'MovementLabUpdateBrake')
start=new_update.index('        // Avoid v11');end=new_update.index('        // Read physical',start)
assert new_update[:start]+new_update[end:]==method(old,'MovementLabUpdateBrake')
# Regression: each new eligibility condition must remain small.
for condition in re.findall(r'if \(([^\n]*)\)',method(w,'MovementLabCanNativeReversal')):
    assert condition.count('||')+condition.count('&&') <= 2, condition
source=(world/'MovementLabNativeReversal.c').read_text()
source+='\nclass Probe : public PlayerBase\n{\n    ref MovementLabNativeReversal m_MovementLabNativeReversal;\n'
for name in ['MovementLabNativeReversalActive','MovementLabNativeReversalAngle','MovementLabNativeReversalSpeed','MovementLabReleaseNativeReversal','MovementLabCanNativeReversal','MovementLabUpdateNativeReversal']:
    source+=method(w,name)+'\n'
source+='}\n'
source=source.replace('ref MovementLabNativeReversal m_MovementLabNativeReversal;', 'MovementLabNativeReversal* m_MovementLabNativeReversal = nullptr;')
source=source.replace('HumanInputController input','HumanInputController input').replace('HumanMovementState state = new HumanMovementState();','HumanMovementState state;')
source=source.replace('m_MovementLabNativeReversal.', 'm_MovementLabNativeReversal->')
source=source.replace('static ', 'inline static ')
for name in ('MovementLabStartGate','MovementLabReversalSettings','DayZPlayerConstants','HumanInputControllerOverrideType','Math'):
    source=source.replace(name+'.',name+'::')
source=re.sub(r'(class [^\n]+\n\{)',r'\1\npublic:',source)
source=re.sub(r'^    (float|int|bool) (\w+);',r'    \1 \2 = 0;',source,flags=re.M)
source=re.sub(r'^}', '};',source,flags=re.M)

sdk = r'''
#include <array>
#include <cassert>
#include <cmath>
#include <algorithm>
#include <iostream>
struct Vec { float v[3]={0,0,0}; float& operator[](int i){return v[i];} Vec operator-(const Vec& b)const {return {{v[0]-b.v[0],v[1]-b.v[1],v[2]-b.v[2]}};} };
struct Math { static float Max(float a,float b){return std::max(a,b);}static float AbsFloat(float v){return std::abs(v);}static float Sqrt(float v){return std::sqrt(v);}static float Clamp(float v,float a,float b){return std::clamp(v,a,b);}static float Sin(float v){return std::sin(v);}static float Cos(float v){return std::cos(v);}static float Atan2(float a,float b){return std::atan2(a,b);}inline static constexpr float DEG2RAD=3.141592653589793/180, RAD2DEG=180/3.141592653589793; };
struct MovementLabStartGate { inline static bool Enabled=true; };
struct DayZPlayerConstants { static const int STANCEIDX_ERECT=0, MOVEMENT_RUN=2, COMMANDID_MOVE=1, COMMANDID_SCRIPT=2; };
struct HumanAnimInterface { int invalid=-1;int BindCommand(const char*){return invalid>=0?-1:0;}int BindVariableFloat(const char* s){return s[8]=='S'?1:2;} };

enum class HumanInputControllerOverrideType {DISABLED,ENABLED,ONE_FRAME};
struct HumanMovementState {int m_iStanceIdx=0;};
struct InputState {bool angleOn=false,speedOn=false,walk=false;float angle=0,speed=0;};
struct HumanInputController {InputState* state;operator bool()const{return state!=nullptr;}bool IsWalkToggled(){return state->walk;}void OverrideMovementSpeed(HumanInputControllerOverrideType t,float v){state->speedOn=t!=HumanInputControllerOverrideType::DISABLED;state->speed=v;}void OverrideMovementAngle(HumanInputControllerOverrideType t,float v){state->angleOn=t!=HumanInputControllerOverrideType::DISABLED;state->angle=v;}};
struct HumanCommandMove {float speed=2;operator bool()const{return true;}float GetCurrentMovementSpeed(){return speed;}};
struct PlayerBase { bool m_MovementLabWasInput=false; HumanAnimInterface anim;bool alive=true,unconscious=false,raised=false,emote=false,item=false,falling=false,ended=false;Vec position;Vec velocity;InputState input;HumanCommandMove move;int stance=0;void MovementLabCancelStart(){}HumanInputController GetInputController(){return {&input};}HumanCommandMove GetCommand_Move(){return move;}void GetMovementState(HumanMovementState& s){s.m_iStanceIdx=stance;}
 HumanAnimInterface& GetAnimInterface(){return anim;}Vec GetPosition(){return position;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsEmotePlaying(){return emote;}void* GetEntityInHands(){return item?this:nullptr;}bool PhysicsIsFalling(bool){return falling;}void MovementLabReversalEnded(float,float,float,bool){ended=true;}void PhysicsGetVelocity(Vec& v){v=velocity;}
};
using Human=PlayerBase;
constexpr int UAMoveForward=0,UAMoveBack=1,UAMoveLeft=2,UAMoveRight=3,UAWalkRunTemp=4,UAWalkRunForced=5;
struct Action { float value=0;float LocalValue(){return value;} };
struct API { std::array<Action,6> a;Action& GetInputByID(int i){return a[i];} } api;
API& GetUApi(){return api;}
struct UI { bool menu=false;void* GetMenu(){return menu?this:nullptr;} };
struct Mission { bool pause=false;operator bool()const{return true;}bool IsPaused(){return pause;} };
struct Game {void* player=nullptr;bool IsMultiplayer(){return false;}void* GetPlayer(){return player;} UI ui;Mission mission;UI& GetUIManager(){return ui;}Mission& GetMission(){return mission;} } game;
Game& GetGame(){return game;}
struct HumanCommandScript { Vec translation;bool finished=false,rotationLocked=false;int commands=0;std::array<float,3> variables{};
 void SetFlagFinished(bool v){finished=v;}void PreAnim_SetFloat(int id,float value){variables[id]=value;}void PreAnim_CallCommand(int,int,int){commands++;}void PrePhys_GetTranslation(Vec& t){t=translation;}void PrePhys_SetTranslation(Vec t){translation=t;}void PostPhys_LockRotation(){rotationLocked=true;}
};
'''
tests = r'''
int main(){
 for(int fps:{30,60,144})for(int axis=0;axis<2;axis++){
  game={};api={};MovementLabStartGate::Enabled=true;MovementLabReversalSettings::Enabled=true;
  Probe p;game.player=&p;float dt=1.f/fps;int oldKey=axis==0?2:0,newKey=axis==0?3:1;
  float oldAngle=axis==0?-90:0,newAngle=axis==0?90:180;
  api.a[oldKey].value=1;assert(!p.MovementLabUpdateNativeReversal(dt,1,false));
  api={};api.a[newKey].value=1;assert(p.MovementLabUpdateNativeReversal(dt,1,false));
  assert(p.m_MovementLabNativeReversal->Reversals==1);
  float previousSpeed=p.input.speed;int count=0;bool recovering=false;
  while(p.m_MovementLabNativeReversal->Time<.62f && count++<fps){
   api={};if(count%3!=0)api.a[count%2?oldKey:newKey].value=1;
   if(count>=4 && count<=10){api.a[oldKey].value=1;api.a[newKey].value=1;}
   assert(p.MovementLabUpdateNativeReversal(dt,1,false));
   auto* r=p.m_MovementLabNativeReversal;
   assert(r->Reversals==1);assert(p.input.angleOn && p.input.speedOn);
   assert(p.input.speed>=1.599f && p.input.speed<=2.001f);
   assert(std::abs(p.input.angle-(r->Time<.12f?oldAngle:newAngle))<.001f);
   // No gain reset or pop from repeated opposite-key spam.
   assert(std::abs(p.input.speed-previousSpeed)<.25f);
   if(r->Time>.12f){if(recovering)assert(p.input.speed>=previousSpeed-.001f);recovering=true;}
   previousSpeed=p.input.speed;
  }
  api={};api.a[oldKey].value=1;
  assert(p.MovementLabUpdateNativeReversal(dt,1,false));
  assert(p.m_MovementLabNativeReversal->Reversals==2);
  // Another reversal starts while overrides remain owned, no native raw tick.
  assert(p.input.angleOn && p.input.speedOn);
  api={};for(int i=0;i<fps/5;i++)p.MovementLabUpdateNativeReversal(dt,1,false);
  assert(!p.MovementLabNativeReversalActive());assert(!p.input.angleOn && !p.input.speedOn);
  // Reset on release must never interpret starting again as a stale reversal.
  api.a[newKey].value=1;assert(!p.MovementLabUpdateNativeReversal(dt,1,false));
  delete p.m_MovementLabNativeReversal;
 }
 for(int reason=0;reason<13;reason++){
  game={};api={};MovementLabStartGate::Enabled=true;MovementLabReversalSettings::Enabled=true;
  Probe p;game.player=&p;api.a[2].value=1;p.MovementLabUpdateNativeReversal(.016f,1,false);
  api={};api.a[3].value=1;assert(p.MovementLabUpdateNativeReversal(.016f,1,false));
  if(reason==0)MovementLabStartGate::Enabled=false;if(reason==1)MovementLabReversalSettings::Enabled=false;
  if(reason==2)p.alive=false;if(reason==3)p.unconscious=true;if(reason==4)p.raised=true;
  if(reason==5)p.item=true;if(reason==6)p.falling=true;if(reason==7)game.ui.menu=true;
  if(reason==8)game.mission.pause=true;if(reason==9)p.input.walk=true;if(reason==10)p.stance=1;
  assert(!p.MovementLabUpdateNativeReversal(reason==11?.3f:.016f,reason==12?2:1,false));
  assert(!p.input.angleOn && !p.input.speedOn);assert(!p.MovementLabNativeReversalActive());
  delete p.m_MovementLabNativeReversal;
 }
 std::cout<<"V17a actual native-input controller checks passed at 30/60/144 FPS: spam/gap patterns, committed direction, bounded slowdown/recovery, consecutive reversals without an override gap, release and exclusions. V11 ordinary methods/formulas preserved. Native animation/Enforce verification pending.\n";
}
'''

with tempfile.TemporaryDirectory(prefix='movementlab-v17a-') as temp:
    cpp=Path(temp)/'check.cpp';binary=Path(temp)/'check'
    cpp.write_text(sdk+source+tests)
    subprocess.run(['g++','-std=c++17',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
