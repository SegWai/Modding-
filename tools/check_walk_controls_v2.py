#!/usr/bin/env python3
"""Run actual translated controller and PlayerBase integration with a mock SDK.
This does not compile Enforce or emulate native animations.
"""
from pathlib import Path
import re, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'movement-controls-test/MovementLabWalkControlsTest_v2'
source=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
assert 'override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)' in source
for condition in re.findall(r'if \(([^\n]*)\)',source[source.index('protected bool MovementLabCanUseControls'):]):
    assert condition.count('||')+condition.count('&&')<=2,condition
assert 'StartCommand_Script' not in source
assert 'PreAnim_' not in source
assert 'PrePhys_' not in source
mission=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
assert 'MovementLabUpdateBrake(' not in mission
assert 'MovementLabControlsBraking()' in mission
assert 'MovementLabCancelControls()' in mission
source=source.replace('modded class PlayerBase','class Probe : public PlayerBase')
source=source.replace('protected ', '').replace('override ', '')
source=source.replace('super.CommandHandler(', 'PlayerBase::CommandHandler(')
source=source.replace('ref MovementLabWalkControls m_MovementLabControls;', 'MovementLabWalkControls* m_MovementLabControls = nullptr;')
source=source.replace('m_MovementLabControls.', 'm_MovementLabControls->')
source=source.replace('HumanMovementState state = new HumanMovementState();','HumanMovementState state;')
source=source.replace('static ', 'inline static ')
for name in ['Math','HumanInputControllerOverrideType','DayZPlayerConstants','MovementLabStartGate']:
    source=source.replace(name+'.', name+'::')
source=re.sub(r'(class [^\n]+\n\{)',r'\1\npublic:',source)
source=re.sub(r'^    (float|int|bool) (\w+);',r'    \1 \2 = 0;',source,flags=re.M)
source=re.sub(r'^}', '};',source,flags=re.M)
sdk=r'''
#include <cmath>
#include <algorithm>
#include <cassert>
#include <array>
#include <iostream>
struct Math {static float Clamp(float x,float a,float b){return std::clamp(x,a,b);}static float Max(float a,float b){return std::max(a,b);}static float Min(float a,float b){return std::min(a,b);}static float AbsFloat(float v){return std::abs(v);}static float Atan2(float a,float b){return std::atan2(a,b);}inline static constexpr float RAD2DEG=180/3.141592653589793;};
enum class HumanInputControllerOverrideType {DISABLED,ENABLED,ONE_FRAME};
struct DayZPlayerConstants {static const int COMMANDID_MOVE=1,STANCEIDX_ERECT=0;};
constexpr int UAMoveForward=0,UAMoveBack=1,UAMoveLeft=2,UAMoveRight=3,UAWalkRunTemp=4,UAWalkRunForced=5,UATurbo=6;
struct Action{float value=0;float LocalValue(){return value;}};
struct API{std::array<Action,7>a;Action& GetInputByID(int i){return a[i];}}api;
API& GetUApi(){return api;}
struct UI{bool menu=false;bool GetMenu(){return menu;}};
struct Mission{bool pause=false;operator bool()const{return true;}bool IsPaused(){return pause;}};
struct Game{void* player=nullptr;bool multiplayer=false;UI ui;Mission mission;bool IsMultiplayer(){return multiplayer;}void* GetPlayer(){return player;}UI& GetUIManager(){return ui;}Mission& GetMission(){return mission;}}game;
Game& GetGame(){return game;}
struct HumanMovementState{int m_iStanceIdx=0;};
struct InputState{bool speedOn=false,angleOn=false,walk=false;float speed=0,angle=0;};
struct HumanInputController{InputState* state;operator bool()const{return state!=nullptr;}bool IsWalkToggled(){return state->walk;}void OverrideMovementSpeed(HumanInputControllerOverrideType t,float v){state->speedOn=t!=HumanInputControllerOverrideType::DISABLED;state->speed=v;}void OverrideMovementAngle(HumanInputControllerOverrideType t,float v){state->angleOn=t!=HumanInputControllerOverrideType::DISABLED;state->angle=v;}};
struct HumanCommandMove{float speed=0;operator bool()const{return true;}float GetCurrentMovementSpeed(){return speed;}};
struct PlayerBase{bool alive=true,unconscious=false,raised=false,emote=false,falling=false;int stance=0,baseCalls=0;InputState input;HumanCommandMove move;HumanInputController GetInputController(){return {&input};}HumanCommandMove GetCommand_Move(){return move;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsEmotePlaying(){return emote;}bool PhysicsIsFalling(bool){return falling;}void GetMovementState(HumanMovementState& s){s.m_iStanceIdx=stance;}void CommandHandler(float,int,bool){baseCalls++;move.speed=input.speedOn?input.speed:0;}};
'''
tests=r'''
void tick(Probe& p,float dt){p.CommandHandler(dt,1,false);}
int main(){
 for(int fps:{30,60,144})for(int direction=0;direction<8;direction++){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;game.player=&p;float dt=1.f/fps;
  int primary=direction%4;api.a[primary].value=1;
  if(direction>=4)api.a[primary<2?2:0].value=1;
  // Default directional walking from the very first command tick.
  for(int i=0;i<fps;i++){tick(p,dt);assert(p.input.speedOn);assert(p.input.speed==1);assert(!p.input.angleOn);}
  api.a[6].value=1;
  for(int i=0;i<fps/2;i++)tick(p,dt);
  assert(std::abs(p.input.speed-2)<.0001f);assert(!p.m_MovementLabControls->Sprint);
  // Releasing a single held Shift while moving smoothly returns to walk.
  api.a[6].value=0;for(int i=0;i<fps;i++)tick(p,dt);assert(p.input.speed==1);
  // A slow second press must not sprint.
  api.a[6].value=1;for(int i=0;i<fps/2;i++)tick(p,dt);assert(!p.m_MovementLabControls->Sprint);
  // Quick second press, then release: sprint remains latched while moving.
  api.a[6].value=0;tick(p,dt);api.a[6].value=1;tick(p,dt);
  api.a[6].value=0;tick(p,dt);api.a[6].value=1;tick(p,dt);
  assert(p.m_MovementLabControls->Sprint);
  api.a[6].value=0;for(int i=0;i<fps;i++)tick(p,dt);assert(p.input.speed==3);
  float angle=p.m_MovementLabControls->Angle;api={};tick(p,dt);
  assert(p.m_MovementLabControls->Braking);assert(!p.m_MovementLabControls->Sprint);
  bool sawJog=false,sawWalk=false;int frames=0;
  while(p.m_MovementLabControls->Braking && frames++<fps*2){
   assert(p.input.angleOn);assert(std::abs(p.input.angle-angle)<.001f);
   if(std::abs(p.input.speed-2)<.001f)sawJog=true;
   if(std::abs(p.input.speed-1)<.001f)sawWalk=true;
   tick(p,dt);
  }
  assert(p.input.speed==0);assert(!p.input.angleOn);
  // Native engine can cap lateral/backward sprint; mock accepts gait 3.
  // V11 backward stop deliberately uses a very short backward walk instead.
  if(direction!=1){assert(sawJog);assert(sawWalk);}
  // Sprint latch cleared; restarting without Shift must walk.
  api.a[primary].value=1;tick(p,dt);assert(p.input.speed==1);assert(!p.m_MovementLabControls->Sprint);
  delete p.m_MovementLabControls;
 }
 for(int fps:{30,60,144})for(bool jog:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;game.player=&p;float dt=1.f/fps;
  api.a[0].value=1;api.a[6].value=jog?1:0;
  tick(p,dt);assert(p.input.speed==1); // Shift+W must not leak a jog first.
  for(int i=0;i<fps;i++)tick(p,dt);
  float before=p.input.speed;api={};tick(p,dt);float elapsed=dt;bool sawWalk=!jog;
  while(p.m_MovementLabControls->Braking){if(p.input.speed<=1.1f)sawWalk=true;assert(p.input.speed<=before+.001f);before=p.input.speed;tick(p,dt);elapsed+=dt;}
  assert(sawWalk && p.input.speed==0);assert(elapsed<(jog?.46f:.18f));
  delete p.m_MovementLabControls;
 }

 // Quick sprint request from idle must spend time at walk and jog, not
 // interpolate straight across gait 2. Check real integrated command output.
 for(int fps:{30,60,144}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;game.player=&p;float dt=1.f/fps;
  api.a[0].value=1;int jogFrames=0;bool sprintReached=false;
  for(int i=0;i<fps;i++){
   api.a[6].value=(i==0 || i==2)?1:0;tick(p,dt);
   auto* c=p.m_MovementLabControls;
   if(i==0)assert(c->Speed==1);
   if(c->StartTime<.0999f)assert(c->Speed==1);
   if(c->StartTime<.35f)assert(c->Speed<=2.0001f);
   if(std::abs(c->Speed-2)<.0001f)jogFrames++;
   if(c->Speed>2.99f)sprintReached=true;
  }
  assert(jogFrames>=1 && sprintReached);
  delete p.m_MovementLabControls;
 }
 // Direction is retained even after diagonal input is released. Full sprint
 // stop budgets must match straight forward, both diagonals and pure sides.
 for(int fps:{30,60,144})for(int keys:{1,5,9,4,8}){
  MovementLabWalkControls c;c.Moving=true;c.Speed=3;c.Exposure=.45;c.LastKeys=keys;
  c.Angle=keys==1?0:keys==5?-45:keys==9?45:keys==4?-90:90;
  float angle=c.Angle,dt=1.f/fps;c.Update(dt,0,0,0,false,false,3);
  assert(std::abs(c.BrakeDuration-1.15f)<.0001f);
  int steps=1;while(c.Braking && steps++<fps*2){assert(c.Angle==angle);c.Update(dt,0,0,0,false,false,c.Speed);}
  assert(!c.Braking && c.Speed==0);assert(steps*dt>=1.15f && steps*dt<1.15f+2*dt);
 }
 // Near-jog sprint exposure must not make its stop shorter than jogging.
 MovementLabWalkControls near;near.Moving=true;near.Speed=2.1;near.Exposure=.01;near.LastKeys=1;
 near.Update(.016f,0,0,0,false,false,2.1);assert(near.BrakeDuration>=.42f);
 // Resuming movement in mid-coast retargets from its current gait instead
 // of snapping a moving jogging/sprint pose straight to walking.
 MovementLabWalkControls resume;resume.Moving=true;resume.Speed=3;resume.Exposure=.45;resume.LastKeys=1;
 resume.Update(.016f,0,0,0,false,false,3);float coast=resume.Speed;
 resume.Update(.016f,0,-1,4,false,false,coast);
 assert(!resume.Braking && resume.Speed>2.5f);assert(std::abs(resume.Speed-coast)<.05f);
 for(int i=0;i<80;i++)resume.Update(.016f,0,-1,4,false,false,resume.Speed);
 assert(resume.Speed==1);
 // The short backward settle remains shorter than lateral jogging settles.
 MovementLabWalkControls back;back.Moving=true;back.Speed=2;back.LastKeys=2;back.Angle=180;
 back.Update(.016f,0,0,0,false,false,2);assert(back.BrakeDuration==.18f && back.Speed==1 && back.Angle==180);
 MovementLabWalkControls lateral;lateral.Moving=true;lateral.Speed=2;lateral.LastKeys=4;lateral.Angle=-90;
 lateral.Update(.016f,0,0,0,false,false,2);assert(lateral.BrakeDuration==.42f && lateral.Speed>=1 && lateral.Angle==-90);

 // Opposing forward/back held together with D still has purely lateral
 // intent, so its release gets the lateral walking finish, never forward.
 game={};api={};MovementLabStartGate::Enabled=true;Probe overlap;game.player=&overlap;
 api.a[0].value=1;api.a[1].value=1;api.a[3].value=1;api.a[6].value=1;
 for(int i=0;i<60;i++)tick(overlap,.016f);
 assert(overlap.m_MovementLabControls->LastKeys==8);
 api={};tick(overlap,.016f);assert(overlap.input.angle==90 && overlap.input.speed>=1);
 delete overlap.m_MovementLabControls;
 // Release during a not-yet-achieved sprint cannot receive full sprint tail.
 MovementLabWalkControls c;c.Update(.016f,1,0,1,true,false,0);c.Update(.016f,1,0,1,false,false,1);c.Update(.016f,1,0,1,true,false,1);
 assert(c.Sprint);c.Update(.016f,0,0,0,false,false,1);assert(c.BrakeStart<=1);assert(c.BrakeDuration==.14f);
 // Movement resuming during braking cancels the coast into a walking start.
 c.Update(.016f,0,-1,4,false,false,.8f);assert(c.Speed>0 && c.Speed<=1 && !c.Braking);
 // Even a long supported tick must begin with walking.
 MovementLabWalkControls first;first.Update(.18f,1,0,1,true,false,0);assert(first.Speed==1);
 // Explicit Ctrl walk overrides and clears latched sprint.
 MovementLabWalkControls forced;forced.Sprint=true;forced.Moving=true;forced.Speed=3;
 for(int i=0;i<30;i++)forced.Update(.016f,1,0,1,true,true,3);
 assert(!forced.Sprint && forced.Speed==1);
 for(int reason=0;reason<11;reason++){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;game.player=&p;api.a[0].value=1;tick(p,.016f);assert(p.input.speedOn);
  if(reason==0)MovementLabStartGate::Enabled=false;if(reason==1)p.alive=false;if(reason==2)p.unconscious=true;
  if(reason==3)p.raised=true;if(reason==4)p.emote=true;if(reason==5)p.falling=true;if(reason==6)game.ui.menu=true;
  if(reason==7)game.mission.pause=true;if(reason==8)p.stance=1;if(reason==9)game.multiplayer=true;
  tick(p,reason==10?.3f:.016f);assert(!p.input.speedOn && !p.input.angleOn);
  delete p.m_MovementLabControls;
 }
 std::cout<<"Actual walking-first controls and pre-handler integration passed at 30/60/144 FPS: WASD walking, Shift jogging, double-tap latch/reset, no initial jog frame, direction-preserving staged stops, short-tap stops, cancellation, smooth coast retargeting, explicit walk/jog/sprint stages and v11 directional stop budgets. Native Enforce/animation verification pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='walk-controls-v2-') as temp:
    cpp=Path(temp)/'check.cpp';binary=Path(temp)/'check'
    cpp.write_text(sdk+source+tests)
    subprocess.run(['g++','-std=c++17',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
