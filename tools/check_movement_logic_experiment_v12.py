#!/usr/bin/env python3
"""Check actual v12 World control logic via mechanical C++ translation/mocks.

Requires g++; this is NOT native Enforce compilation or animation validation.
The controller methods come from source; the harness models instantaneous
native gait response solely to exercise sequencing, ownership and cancellation.
"""
from pathlib import Path
import re, subprocess
root=Path(__file__).resolve().parents[1] / 'movement-logic-experiments/MovementLabMovementLogicTest_v12/StartGateSource/Scripts/4_World'
world=(root/'MovementLabStartGate.c').read_text()
envelope=(root/'MovementLabStopEnvelope.c').read_text()
def translate(s):
 s=s.replace('modded class PlayerBase','class PlayerLogic : public MockPlayer')
 s=s.replace('protected ', '').replace('override void ', 'void ')
 s=re.sub(r'(class [^\n]+\n\{)',r'\1\npublic:',s)
 s=s.replace('HumanMovementState state = new HumanMovementState();','HumanMovementState state;')
 for name in ('MovementLabStartGate','MovementLabStopEnvelope','HumanInputControllerOverrideType','DayZPlayerConstants','Math'):
  s=s.replace(name+'.',name+'::')
 s=s.replace('super.CommandHandler','MockPlayer::CommandHandler')
 s=re.sub(r'^    (bool|float|int) (m_\w+);',r'    \1 \2 = 0;',s,flags=re.M)
 s=re.sub(r'^}', '};', s, flags=re.M)
 return s
sdk=r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <iostream>
struct Math { static float Clamp(float v,float a,float b){return std::clamp(v,a,b);} static float Min(float a,float b){return std::min(a,b);} static float Max(float a,float b){return std::max(a,b);} static float AbsFloat(float v){return std::abs(v);} };
enum class HumanInputControllerOverrideType { DISABLED,ENABLED,ONE_FRAME };
struct DayZPlayerConstants { static constexpr int COMMANDID_MOVE=1, STANCEIDX_ERECT=0; };
constexpr int UAMoveForward=0,UAMoveBack=1,UAMoveLeft=2,UAMoveRight=3,UAWalkRunTemp=4,UAWalkRunForced=5,UATurbo=6;
struct Action { float value=0;bool press=false;float LocalValue(){return value;}bool LocalPress(){return press;} };
struct API { std::array<Action,7> a;Action& GetInputByID(int id){return a[id];} } api;
API& GetUApi(){return api;}
struct InputState { bool speedOn=false,angleOn=false,walkToggle=false;float speed=0,angle=0; };
struct HumanInputController { InputState* p;operator bool()const{return p!=nullptr;}bool IsWalkToggled(){return p->walkToggle;}void OverrideMovementSpeed(HumanInputControllerOverrideType t,float v){p->speedOn=t!=HumanInputControllerOverrideType::DISABLED;p->speed=v;}void OverrideMovementAngle(HumanInputControllerOverrideType t,float v){p->angleOn=t!=HumanInputControllerOverrideType::DISABLED;p->angle=v;} };
struct HumanCommandMove { float gait=0,angle=0;operator bool()const{return true;}float GetCurrentMovementSpeed(){return gait;}float GetCurrentMovementAngle(){return angle;}void SetRunSprintFilterModifier(float){} };
struct HumanMovementState { int m_iStanceIdx=0; };
struct MockPlayer;
struct UI { bool menu=false;void* GetMenu(){return menu?this:nullptr;} };
struct Game { MockPlayer* player=nullptr;UI ui;bool IsMultiplayer(){return false;}MockPlayer* GetPlayer(){return player;}UI& GetUIManager(){return ui;} } game;
Game& GetGame(){return game;}
void Print(const char*){}
struct MockPlayer { InputState input;HumanCommandMove move;bool IsAlive(){return true;}bool IsUnconscious(){return false;}bool IsRaised(){return false;}bool IsEmotePlaying(){return false;}HumanInputController GetInputController(){return {&input};}HumanCommandMove& GetCommand_Move(){return move;}void GetMovementState(HumanMovementState& s){s.m_iStanceIdx=0;}void CommandHandler(float,int,bool){} };
'''
tests=r'''
bool MovementLabStartGate::Enabled=true;
void keys(int f,int b,int l,int r){int values[]={f,b,l,r};for(int i=0;i<4;i++){api.a[i].press=values[i] && !api.a[i].value;api.a[i].value=values[i];}}
void setup(PlayerLogic& p){api={};game.player=&p;game.ui.menu=false;MovementLabStartGate::Enabled=true;}
void tick(PlayerLogic& p,float dt,bool stall=false){p.CommandHandler(dt,1,false);float f=api.a[0].value-api.a[1].value;float s=api.a[3].value-api.a[2].value;bool moving=f!=0||s!=0;bool walk=api.a[4].value||api.a[5].value||p.input.walkToggle;float speed=moving?(walk?1:(api.a[6].value && f>0?3:2)):0;if(p.input.speedOn)speed=p.input.speed;if(!stall)p.move.gait=speed;p.move.angle=p.input.angleOn?p.input.angle:std::atan2(s,f)*180/3.14159265;for(auto& a:api.a)a.press=false;}
void prime(PlayerLogic& p,float dt,int side,bool diagonal=false){p.move.gait=diagonal?3:2;p.move.angle=side*(diagonal?45:90);keys(diagonal,0,side<0,side>0);api.a[6].value=diagonal;tick(p,dt);}
int main(){
 for(int fps:{30,60,144}){float dt=1.0f/fps;
  for(int dir=0;dir<4;dir++){
   PlayerLogic p;setup(p);keys(0,0,0,0);tick(p,dt);assert(p.move.gait==0);
   keys(dir==0,dir==1,dir==2,dir==3);api.a[6].value=dir==0;tick(p,dt);assert(p.move.gait==1);assert(p.MovementLabIsStarting());
   for(int n=0;n<fps;n++)tick(p,dt);assert(!p.MovementLabIsStarting());assert(!p.MovementLabIsReversing());assert(p.move.gait==(dir==0?3:2));
  }
  for(int side:{-1,1})for(bool diagonal:{false,true}){
   PlayerLogic p;setup(p);prime(p,dt,side,diagonal);keys(diagonal,0,side>0,side<0);tick(p,dt);assert(p.MovementLabIsReversing());float zero=0,total=dt;int n=0;
   while(p.MovementLabIsReversing() && n++<fps*3){assert(std::abs(p.move.angle-side*(diagonal?45:90))<.01);if(p.move.gait==0)zero+=dt;tick(p,dt);total+=dt;}
   assert(!p.MovementLabIsReversing());assert(zero>=.12f-.0001f);assert(p.MovementLabIsStarting());assert(p.move.gait==1);assert((side<0 && p.move.angle>0)||(side>0 && p.move.angle<0));assert(total<2);
  }
  {PlayerLogic p;setup(p);prime(p,dt,-1);keys(0,0,0,1);tick(p,dt);keys(0,0,0,0);for(int i=0;i<fps*2;i++)tick(p,dt);assert(!p.MovementLabIsReversing());assert(p.move.gait==0);}
  {PlayerLogic p;setup(p);prime(p,dt,-1);keys(0,0,1,1);tick(p,dt);assert(p.MovementLabIsReversing());for(int i=0;i<fps*2;i++)tick(p,dt);assert(!p.MovementLabIsReversing());assert(p.move.gait==0);}
  {PlayerLogic p;setup(p);prime(p,dt,-1);keys(0,0,0,1);tick(p,dt);float elapsed=dt;int n=0;while(p.MovementLabIsReversing()&&n++<fps*2){keys(0,0,n%2,!(n%2));tick(p,dt);elapsed+=dt;}assert(!p.MovementLabIsReversing());assert(elapsed>=.54f);}
  {PlayerLogic p;setup(p);prime(p,dt,-1);api.a[4].value=1;keys(0,0,0,1);tick(p,dt);assert(!p.MovementLabIsReversing());}
  {PlayerLogic p;setup(p);prime(p,dt,-1);keys(0,0,0,1);tick(p,dt);MovementLabStartGate::Enabled=false;tick(p,dt);assert(!p.MovementLabIsReversing());assert(!p.input.angleOn&&!p.input.speedOn);}
  {PlayerLogic p;setup(p);prime(p,dt,-1);keys(0,0,0,1);tick(p,dt);game.ui.menu=true;tick(p,dt);assert(!p.MovementLabIsReversing());assert(!p.input.angleOn&&!p.input.speedOn);}
  {PlayerLogic p;setup(p);prime(p,dt,-1);keys(0,0,0,1);tick(p,dt);int n=0;while(p.MovementLabIsReversing()&&n++<fps*2)tick(p,dt,true);assert(!p.MovementLabIsReversing());}
 }
 for(float start:{2.5f,2.8f,3.0f}){float prev=start;for(int i=0;i<=1000;i++){float v=MovementLabStopEnvelope::Sprint(start,i/1000.f);assert(v>=-.0001f&&v<=prev+.0001f);prev=v;}assert(std::abs(prev)<.0001f);}
 std::cout<<"Transformed actual World-script logic passed mocked sequences at 30/60/144 FPS: both reversal signs, diagonals, stationary dwell, walk restart, release, opposing held keys, chatter, manual walk, F7/UI cancellation, timeout, and envelope bounds. Not native Enforce/animation validation.\n";
}
'''
import tempfile
with tempfile.TemporaryDirectory(prefix="movementlab-v12-") as temporary:
    cpp = Path(temporary) / "check.cpp"
    executable = Path(temporary) / "check"
    cpp.write_text(sdk + translate(envelope) + translate(world) + tests)
    subprocess.run(["g++", "-std=c++17", "-O0", str(cpp), "-o", str(executable)], check=True)
    subprocess.run([str(executable)], check=True)
