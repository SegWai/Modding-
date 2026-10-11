#!/usr/bin/env python3
"""Run actual translated v11-derived mode/brake methods against an SDK mock.
Native Enforce compilation and animation playback are not modeled.
"""
from pathlib import Path
import re, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v10_Strafe_v1'
w=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
m=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
b=(ROOT/'movement-logic-test/MovementLabMovementLogicTest/Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
assert 'override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)' in w
for cond in re.findall(r'if \(([^\n]*)\)',w[w.index('protected bool MovementLabCanUseModes'):w.index('protected void MovementLabCommandStart')]):
    assert cond.count('||')+cond.count('&&')<=2
assert 'StartCommand_Script' not in w and 'PreAnim_' not in w

def method(text,name):
    match=re.search(r'\b(?:void|bool|float)\s+'+name+r'\([^)]*\)\s*\{',text);assert match,name
    start=match.start();i=text.index('{',start)+1;depth=1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]



source=w.replace('modded class PlayerBase','class Probe : public SDKPlayer')
source=source.replace('protected bool m_MovementLabStartOwnsSpeed;', 'static Probe* Cast(void* p){return static_cast<Probe*>(p);}\n    protected bool m_MovementLabStartOwnsSpeed;')
prior=(ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v9/Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
for name,mission in [('MissionProbe',m),('MissionBaseline',b),('MissionPrevious',prior)]:
    fields=mission[mission.index('    protected bool m_MovementLabHeavy'):mission.index('    protected void MovementLabCancelStart')]
    source+='\nclass '+name+'\n{\n'+fields
    source+=' UI& GetUIManager(){return game.ui;}bool IsPaused(){return game.mission.pause;}\n'
    for helper in ['MovementLabCancelStart','MovementLabCancelBrake','MovementLabBeginBrake','MovementLabUpdateBrake']:
        source+=method(mission,helper)+'\n'
    source+='}\n'
source=re.sub(r'^\s*Print\([^\n]*\);','',source,flags=re.M)
source=source.replace('protected ','').replace('override ','')
source=source.replace('super.CommandHandler(', 'SDKPlayer::CommandHandler(')
source=source.replace('PlayerBase', 'Probe')
source=source.replace('Probe player','Probe* player').replace('Probe m_MovementLabBrakePlayer;', 'Probe* m_MovementLabBrakePlayer = nullptr;')
source=source.replace('m_MovementLabBrakePlayer.', 'm_MovementLabBrakePlayer->').replace('player.', 'player->')
source=re.sub(r'HumanMovementState (\w+) = new HumanMovementState\(\);', r'HumanMovementState \1;',source)
source=source.replace('null','nullptr').replace('nullptrptr','nullptr')
source=source.replace('static bool Enabled;', 'inline static bool Enabled = false;')
for name in ['Math','MovementLabStartGate','HumanInputControllerOverrideType','DayZPlayerConstants']:
    source=source.replace(name+'.',name+'::')
source=source.replace('Probe.Cast(', 'Probe::Cast(')
source=re.sub(r'(class [^\n]+\n\{)',r'\1\npublic:',source)
source=re.sub(r'^    (float|int|bool) (\w+);',r'    \1 \2 = 0;',source,flags=re.M)
source=re.sub(r'^}', '};',source,flags=re.M)
sdk=r'''
#include <cassert>
#include <cmath>
#include <algorithm>
#include <array>
#include <iostream>
struct Math{static float AbsFloat(float v){return std::abs(v);}static float Clamp(float x,float a,float b){return std::clamp(x,a,b);}static float Min(float a,float b){return std::min(a,b);}static float Max(float a,float b){return std::max(a,b);}};
constexpr int UAMoveForward=0,UAMoveBack=1,UAMoveLeft=2,UAMoveRight=3,UAWalkRunTemp=4,UAWalkRunForced=5,UATurbo=6;
struct Action{float value=0;float LocalValue(){return value;}};struct API{std::array<Action,7>a;Action& GetInputByID(int id){return a[id];}}api;API& GetUApi(){return api;}
struct UI{bool menu=false;bool GetMenu(){return menu;}};struct Pause{bool pause=false;operator bool()const{return true;}bool IsPaused(){return pause;}};
struct Game{bool multi=false;void* player=nullptr;UI ui;Pause mission;bool IsMultiplayer(){return multi;}void* GetPlayer(){return player;}UI& GetUIManager(){return ui;}Pause& GetMission(){return mission;}}game;Game& GetGame(){return game;}
struct DayZPlayerConstants{static const int COMMANDID_MOVE=1,STANCEIDX_ERECT=0,STANCEIDX_CROUCH=1;};
enum class HumanInputControllerOverrideType{DISABLED,ENABLED,ONE_FRAME};
struct InputState{bool speedOn=false,angleOn=false;float speed=0,angle=0;};
struct HumanInputController{InputState* state;operator bool()const{return state!=nullptr;}void OverrideMovementSpeed(HumanInputControllerOverrideType t,float v){state->speedOn=t!=HumanInputControllerOverrideType::DISABLED;state->speed=v;}void OverrideMovementAngle(HumanInputControllerOverrideType t,float v){state->angleOn=t!=HumanInputControllerOverrideType::DISABLED;state->angle=v;}};
struct HumanMovementState{int m_iStanceIdx=0;};struct HumanCommandMove{float speed=0,angle=0;operator bool()const{return true;}float GetCurrentMovementSpeed(){return speed;}float GetCurrentMovementAngle(){return angle;}};
struct SDKPlayer{bool alive=true,unconscious=false,raised=false,emote=false;int stance=0;InputState input;HumanCommandMove move;HumanInputController GetInputController(){return {&input};}HumanCommandMove GetCommand_Move(){return move;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsEmotePlaying(){return emote;}void GetMovementState(HumanMovementState& s){s.m_iStanceIdx=stance;}void CommandHandler(float,int,bool){bool moving=false;for(int k=0;k<4;k++)moving=moving||api.a[k].value>.05f;float native=moving?(api.a[6].value>.05f?3.f:api.a[4].value>.05f?1.f:2.f):0.f;move.speed=input.speedOn?input.speed:native;}};
'''
tests=r'''
void tick(Probe& p,MissionProbe& m,float dt,bool missionFirst){
 if(missionFirst)m.MovementLabUpdateBrake(&p,dt);
 p.CommandHandler(dt,1,false);
 if(!missionFirst)m.MovementLabUpdateBrake(&p,dt);
 bool moving=false;for(int k=0;k<4;k++)moving=moving||api.a[k].value>.05f;float native=moving?(api.a[6].value>.05f?3.f:api.a[4].value>.05f?1.f:2.f):0.f;p.move.speed=p.input.speedOn?p.input.speed:native;
 if(p.input.angleOn)p.move.angle=p.input.angle;
 else if(api.a[2].value>.05f && api.a[3].value<=.05f)p.move.angle=-90;
 else if(api.a[3].value>.05f && api.a[2].value<=.05f)p.move.angle=90;
}
void ticks(Probe& p,MissionProbe& m,int n,float dt,bool order){for(int i=0;i<n;i++)tick(p,m,dt,order);}
int main(){
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;
  api.a[0].value=1;tick(p,m,dt,order);assert(p.move.speed==1);ticks(p,m,fps,dt,order);assert(p.move.speed==2);
  // Ctrl edge toggles once, held Ctrl does not repeatedly change mode.
  api.a[4].value=1;tick(p,m,dt,order);assert(p.MovementLabBaseGait()==1);assert(p.move.speed>1.7f);
  ticks(p,m,fps,dt,order);assert(p.move.speed==1 && p.MovementLabBaseGait()==1);
  api.a[4].value=0;tick(p,m,dt,order);assert(p.move.speed==1);
  // Walk -> sprint must show jogging, then restore WALK after Shift release.
  api.a[6].value=1;bool jog=false;
  for(int i=0;i<fps;i++){tick(p,m,dt,order);if(std::abs(p.move.speed-2)<.001f)jog=true;}
  assert(jog && p.move.speed==3 && p.MovementLabBaseGait()==1);
  // Ctrl while sprinting cannot overwrite the saved pre-sprint mode.
  api.a[4].value=1;tick(p,m,dt,order);assert(p.MovementLabBaseGait()==1);api.a[4].value=0;
  ticks(p,m,fps,dt,order);api.a[6].value=0;tick(p,m,dt,order);
  assert(p.move.speed>2);assert(m.m_MovementLabBrakeTarget==1);
  jog=false;for(int i=0;i<fps*2;i++){tick(p,m,dt,order);if(std::abs(p.move.speed-2)<.001f)jog=true;}
  assert(jog && p.move.speed==1 && !m.m_MovementLabBraking);
  // Toggle back to jogging, use Shift, restore JOG rather than walking.
  api.a[4].value=1;tick(p,m,dt,order);assert(p.MovementLabBaseGait()==2);api.a[4].value=0;ticks(p,m,fps,dt,order);
  assert(p.move.speed==2);api.a[6].value=1;ticks(p,m,fps,dt,order);assert(p.move.speed==3);
  api.a[6].value=0;tick(p,m,dt,order);assert(m.m_MovementLabBrakeTarget==2);
  ticks(p,m,fps,dt,order);assert(p.move.speed==2);
  // Hold Shift but release movement: complete v11 stop, not ongoing sprint.
  api.a[6].value=1;ticks(p,m,fps,dt,order);api.a[0].value=0;tick(p,m,dt,order);
  assert(m.m_MovementLabBrakeTarget==0 && m.m_MovementLabBraking);
  assert(std::abs(m.m_MovementLabBrakeDuration-1.15f)<.0001f);
  ticks(p,m,fps*2,dt,order);assert(p.move.speed==0 && !m.m_MovementLabBraking);
  // Starting again in walk mode from idle respects mode and no jog leak.
  api.a[6].value=0;api.a[4].value=1;tick(p,m,dt,order);api.a[4].value=0;api.a[0].value=1;
  tick(p,m,dt,order);assert(p.move.speed==1);ticks(p,m,fps,dt,order);assert(p.move.speed==1);
  api.a[0].value=0;tick(p,m,dt,order);assert(!m.m_MovementLabBraking);
  ticks(p,m,fps,dt,order);assert(p.move.speed==0);
 }
 // Differential regression: execute ORIGINAL v11 and new actual braking
 // methods with equal sustained-sprint inputs, compare every tick and deadline.
 for(int fps:{30,60,144})for(float gait:{2.f,2.1f,2.3f,2.49f,2.5f,2.9f,3.f})for(float exposure:{.05f,.225f,.45f})for(int keys:{1,5,9,4,8,2}){
  game={};api={};api.a[6].value=1;MovementLabStartGate::Enabled=true;Probe p;game.player=&p;p.move.speed=gait;
  MissionProbe next;MissionBaseline old;float dt=1.f/fps;
  next.m_MovementLabWasMoving=old.m_MovementLabWasMoving=true;
  next.m_MovementLabLastSpeed=old.m_MovementLabLastSpeed=gait;
  next.m_MovementLabSprintExposure=old.m_MovementLabSprintExposure=gait>2?exposure:0;
  next.m_MovementLabLastKeys=old.m_MovementLabLastKeys=keys;
  next.m_MovementLabLastAngle=old.m_MovementLabLastAngle=keys==1?0:keys==2?180:keys==5?-45:keys==9?45:keys==4?-90:90;
  for(int i=0;i<fps*2;i++){
   old.MovementLabUpdateBrake(&p,dt);next.MovementLabUpdateBrake(&p,dt);
   assert(old.m_MovementLabBraking==next.m_MovementLabBraking);
   assert(std::abs(old.m_MovementLabBrakeSpeed-next.m_MovementLabBrakeSpeed)<.0001f);
   assert(std::abs(old.m_MovementLabBrakeDuration-next.m_MovementLabBrakeDuration)<.0001f);
   assert(old.m_MovementLabBrakeAngle==next.m_MovementLabBrakeAngle);
  }
 }


 // Shift release into walk matches original v11 full stop on every frame
 // above walk, then stays at walk. Exercise both sides of the 2.5 threshold,
 // brief/full sprint exposure, all stopping directions, and FPS budgets.
 for(int fps:{30,60,144})for(float gait:{2.1f,2.3f,2.49f,2.5f,2.9f,3.f})
 for(float exposure:{.05f,.225f,.45f})for(int keys:{1,5,9,4,8,2}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;game.player=&p;
  p.m_MovementLabWalkMode=true;p.move.speed=gait;
  MissionProbe walking;MissionBaseline stopping;float dt=1.f/fps;
  walking.m_MovementLabWasMoving=stopping.m_MovementLabWasMoving=true;
  walking.m_MovementLabWasTurbo=stopping.m_MovementLabWasTurbo=true;
  walking.m_MovementLabLastSpeed=stopping.m_MovementLabLastSpeed=gait;
  walking.m_MovementLabSprintExposure=stopping.m_MovementLabSprintExposure=exposure;
  walking.m_MovementLabLastKeys=stopping.m_MovementLabLastKeys=keys;
  p.move.angle=walking.m_MovementLabLastAngle=stopping.m_MovementLabLastAngle=keys==1?0:keys==2?180:keys==5?-45:keys==9?45:keys==4?-90:90;
  for(int i=0;i<fps*2;i++){
   api={};stopping.MovementLabUpdateBrake(&p,dt);
   api.a[0].value=(keys&1)?1:0;api.a[1].value=(keys&2)?1:0;
   api.a[2].value=(keys&4)?1:0;api.a[3].value=(keys&8)?1:0;
   walking.MovementLabUpdateBrake(&p,dt);
   assert(walking.m_MovementLabBraking==stopping.m_MovementLabBraking);
   assert(std::abs(walking.m_MovementLabBrakeDuration-stopping.m_MovementLabBrakeDuration)<.0001f);
   if(!walking.m_MovementLabBraking)break;
   assert(walking.m_MovementLabBrakeTarget==1);
   assert(std::abs(walking.m_MovementLabBrakeSpeed-std::max(1.f,stopping.m_MovementLabBrakeSpeed))<.0001f);
   assert(walking.m_MovementLabBrakeAngle==stopping.m_MovementLabBrakeAngle);
   assert(walking.m_MovementLabBrakeSpeed>=1 && walking.m_MovementLabBrakeSpeed<=gait);
  }
 }


 // Turning lowers achieved native gait, especially in rear diagonals.
 // A continuous held input must NOT repeatedly re-arm the startup blend.
 for(int fps:{30,60,144})for(bool order:{false,true})for(bool walk:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;
  float dt=1.f/fps;api.a[0].value=1;ticks(p,m,fps,dt,order);
  if(walk){api.a[4].value=1;tick(p,m,dt,order);api.a[4].value=0;ticks(p,m,fps,dt,order);}
  for(int keys:{1,9,8,10,2,6,4,5,1})for(int i=0;i<fps;i++){
   for(int k=0;k<4;k++)api.a[k].value=(keys&(1<<k))?1:0;
   p.move.speed=walk?1.2f:1.4f; // native turn gait dip, not a new mode request
   p.move.angle=(keys&2)?135.f:-45.f;
   tick(p,m,dt,order);
   assert(!p.MovementLabIsStarting() && !m.m_MovementLabBraking);
   assert(p.input.speedOn && p.input.speed==(walk?1.f:2.f));
   assert(!p.input.angleOn);
  }
 }
 // A jog->walk return started in a rear diagonal must never pin old forward
 // heading while mouse/native direction changes; no repeat brake after finish.
 for(int keys:{6,10})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;
  api.a[0].value=1;ticks(p,m,90,.016f,order);
  api.a[0].value=0;api.a[1].value=1;api.a[keys==6?2:3].value=1;
  p.move.angle=keys==6?-135.f:135.f;api.a[4].value=1;
  tick(p,m,.016f,order);api.a[4].value=0;
  tick(p,m,.016f,order);assert(m.m_MovementLabBraking && m.m_MovementLabBrakeTarget==1);
  assert(m.m_MovementLabBrakeKeys==keys);
  assert(!p.input.angleOn);
  for(int i=0;i<90;i++){p.move.angle=keys==6?-120.f:120.f;tick(p,m,.016f,order);assert(!p.input.angleOn);}
  assert(!m.m_MovementLabBraking && p.move.speed==1);
 }


 // Four crouch rules, prior walk/jog modes, all directions and both callback
 // orders. Native fast crouch must never be capped by a script gait override.
 for(int fps:{30,60,144})for(bool order:{false,true})for(bool priorWalk:{false,true})for(int keys:{1,2,4,8,5,9,6,10}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;
  float dt=1.f/fps;p.m_MovementLabWalkMode=priorWalk;
  for(int k=0;k<4;k++)api.a[k].value=(keys&(1<<k))?1:0;
  ticks(p,m,fps,dt,order);p.stance=1;
  for(int i=0;i<fps;i++){tick(p,m,dt,order);assert(p.move.speed==1 && !p.input.angleOn);}
  assert(p.MovementLabBaseGait()==(priorWalk?1.f:2.f));
  // Slow crouch exit preserves selected standing mode (rule 4).
  p.stance=0;ticks(p,m,fps,dt,order);
  assert(p.move.speed==(priorWalk?1.f:2.f));
  p.stance=1;tick(p,m,dt,order);api.a[6].value=1;
  for(int i=0;i<fps;i++){tick(p,m,dt,order);assert(!p.input.speedOn && !p.input.angleOn && p.move.speed==3);}
  assert(p.MovementLabBaseGait()==(priorWalk?1.f:2.f));
  // Stand from fast crouch while Shift remains held: JOG, not sprint.
  p.stance=0;ticks(p,m,fps,dt,order);
  assert(p.MovementLabBaseGait()==2 && p.move.speed==2 && p.m_MovementLabCrouchShiftConsumed);
  api.a[6].value=0;ticks(p,m,fps,dt,order);assert(p.move.speed==2);
  // New standing Shift press restores exactly the original v4 sprint rule.
  api.a[6].value=1;ticks(p,m,fps,dt,order);assert(p.move.speed==3);
  api.a[6].value=0;ticks(p,m,fps,dt,order);assert(p.move.speed==2);
  api.a[4].value=1;tick(p,m,dt,order);api.a[4].value=0;ticks(p,m,fps,dt,order);assert(p.move.speed==1 && p.MovementLabBaseGait()==1);
  // Fast crouch, then release Shift WHILE STILL CROUCHED: not an ever-fast latch.
  p.stance=1;api.a[6].value=1;tick(p,m,dt,order);api.a[6].value=0;
  tick(p,m,dt,order);assert(p.move.speed==1);p.stance=0;ticks(p,m,fps,dt,order);
  assert(p.MovementLabBaseGait()==1 && p.move.speed==1);
 }
 for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;
  p.m_MovementLabWalkMode=true;p.stance=1;api.a[6].value=1;
  tick(p,m,.016f,order);assert(p.move.speed==0 && !p.input.speedOn && !p.m_MovementLabFastCrouch);
  p.stance=0;tick(p,m,.016f,order);assert(p.MovementLabBaseGait()==1); // idle Shift is not fast crouch
  p.stance=1;api.a[0].value=1;tick(p,m,.016f,order);
  // Same-frame release + stand from previously active fast crouch also selects jog.
  p.stance=0;api.a[6].value=0;ticks(p,m,90,.016f,order);assert(p.MovementLabBaseGait()==2 && p.move.speed==2);
  // Crouching during an existing standing stop drops its owned angle/speed.
  api.a[6].value=1;ticks(p,m,90,.016f,order);api.a[0].value=0;tick(p,m,.016f,order);assert(m.m_MovementLabBraking);
  p.stance=1;api.a[0].value=1;tick(p,m,.016f,order);assert(!m.m_MovementLabBraking && !p.input.speedOn && !p.input.angleOn);
  p.stance=0;tick(p,m,.016f,order);assert(p.move.speed==2);
  // Explicit Ctrl may select walk after fast exit, even if the consumed Shift remains held.
  api.a[4].value=1;tick(p,m,.016f,order);api.a[4].value=0;ticks(p,m,90,.016f,order);assert(p.move.speed==1);
  // Disabled profile and prone must not receive a slow-crouch gait override.
  p.stance=1;MovementLabStartGate::Enabled=false;tick(p,m,.016f,order);assert(!p.input.speedOn);
  MovementLabStartGate::Enabled=true;p.stance=2;tick(p,m,.016f,order);assert(!p.input.speedOn);
 }


 // Ctrl jog->walk now keeps moving jogging initially: momentum is higher early, but the request
 // remains monotonic and completes on the SAME tick/deadline as v8.
 for(int fps:{30,60,144})for(float gait:{1.8f,2.f,2.05f})for(int keys:{1,2,4,8,5,9,6,10}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;game.player=&p;
  p.m_MovementLabWalkMode=true;p.move.speed=gait;p.move.angle=keys==6?-135.f:keys==10?135.f:0.f;
  for(int k=0;k<4;k++)api.a[k].value=(keys&(1<<k))?1:0;
  MissionProbe next;MissionPrevious old;float dt=1.f/fps,previous=gait;bool changed=false;
  next.m_MovementLabWasMoving=old.m_MovementLabWasMoving=true;
  next.m_MovementLabLastSpeed=old.m_MovementLabLastSpeed=gait;
  next.m_MovementLabLastKeys=old.m_MovementLabLastKeys=keys;
  for(int i=0;i<fps;i++){
   old.MovementLabUpdateBrake(&p,dt);next.MovementLabUpdateBrake(&p,dt);
   assert(next.m_MovementLabBraking==old.m_MovementLabBraking);
   assert(next.m_MovementLabBrakeDuration==old.m_MovementLabBrakeDuration);
   if(!next.m_MovementLabBraking){assert(changed);break;}
   float t=next.m_MovementLabBrakeTime/next.m_MovementLabBrakeDuration;
   float u=std::clamp((t-.2857143f)/.7142857f,0.f,1.f);
   float expected=gait+(1-gait)*u*u*(3-2*u);
   if(t<=.2857143f)assert(next.m_MovementLabBrakeSpeed==gait);
   assert(std::abs(next.m_MovementLabBrakeSpeed-expected)<.0001f);
   assert(next.m_MovementLabBrakeSpeed>=old.m_MovementLabBrakeSpeed-.0001f);
   assert(next.m_MovementLabBrakeSpeed>=1 && next.m_MovementLabBrakeSpeed<=previous);
   changed=changed || next.m_MovementLabBrakeSpeed>old.m_MovementLabBrakeSpeed+.001f;
   previous=next.m_MovementLabBrakeSpeed;
  }
 }


 // Signed lateral momentum must resist opposite input, in both orders.
 for(int fps:{30,60,144})for(bool order:{false,true}){
  game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;float dt=1.f/fps;
  api.a[2].value=1;ticks(p,m,fps,dt,order);assert(p.move.angle==-90 && p.move.speed==2);
  api.a[2].value=0;api.a[3].value=1;tick(p,m,dt,order);
  assert(p.move.angle==-90 && p.move.speed>1.7f); // Still leftward momentum.
  int crossed=0;float prev=-p.move.speed;
  for(int i=0;i<fps;i++){
   tick(p,m,dt,order);float velocity=p.move.angle<0?-p.move.speed:p.move.speed;
   assert(std::abs(velocity-prev)<=6*dt+.001f);prev=velocity;
   if(!crossed && velocity>0)crossed=i+1;
   assert(!m.m_MovementLabBraking && !p.MovementLabIsStarting());
  }
  assert(crossed>fps*.25f && crossed<fps*.40f && p.move.speed==2 && p.move.angle==90);
  for(int i=0;i<fps*3;i++){
   api.a[2].value=i%2;api.a[3].value=1-i%2;tick(p,m,dt,order);
   float velocity=p.move.angle<0?-p.move.speed:p.move.speed;assert(std::abs(velocity-prev)<=6*dt+.001f);prev=velocity;
  }
  api.a[2].value=0;api.a[3].value=1;ticks(p,m,fps,dt,order);assert(p.move.angle==90 && p.move.speed==2);
  api.a[2].value=1;api.a[3].value=0;tick(p,m,dt,order);assert(p.move.angle==90);
  api.a[2].value=0;ticks(p,m,fps,dt,order);assert(p.move.speed==0 && !p.input.angleOn);
  api.a[0].value=1;ticks(p,m,fps,dt,order);assert(!p.input.angleOn && p.move.speed==2);
 }

 // Releasing movement midway through returning from sprint to walk must
 // continue from the current slowing gait, not boost back to sprint.
 game={};api={};MovementLabStartGate::Enabled=true;Probe returning;MissionProbe rm;game.player=&returning;
 api.a[0].value=1;api.a[4].value=1;tick(returning,rm,.016f,false);api.a[4].value=0;
 ticks(returning,rm,30,.016f,false);api.a[6].value=1;ticks(returning,rm,90,.016f,false);
 api.a[6].value=0;ticks(returning,rm,8,.016f,false);float slowing=returning.move.speed;
 api.a[0].value=0;tick(returning,rm,.016f,false);
 assert(rm.m_MovementLabBrakeTarget==0 && returning.move.speed<=slowing+.001f);
 ticks(returning,rm,100,.016f,false);assert(returning.move.speed==0);
 // A partial diagonal release still moves in the remaining direction.
 game={};api={};MovementLabStartGate::Enabled=true;Probe p;MissionProbe m;game.player=&p;
 api.a[0].value=api.a[2].value=api.a[6].value=1;ticks(p,m,90,.016f,false);
 api.a[2].value=0;tick(p,m,.016f,false);assert(!m.m_MovementLabBraking && p.move.speed==3);
 // A brief sprint request cannot inflate the achieved walking stop.
 game={};api={};Probe brief;MissionProbe bm;game.player=&brief;api.a[0].value=1;api.a[6].value=1;
 tick(brief,bm,.016f,false);api.a[0].value=0;tick(brief,bm,.016f,false);assert(bm.m_MovementLabBrakeStart<=1);
 std::cout<<"Standing/crouch/start/stop regression checks and signed pure-strafe momentum checks passed at 30/60/144 FPS, both callback orders. Opposite momentum persists initially; zero crossing within 0.25-0.40s; spam slew bounded; native ownership restored on release. Native DayZ compile/animation validation pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='ctrl-modes-') as temp:
    cpp=Path(temp)/'check.cpp';binary=Path(temp)/'check'
    cpp.write_text(sdk+source+tests)
    subprocess.run(['g++','-std=c++17',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
