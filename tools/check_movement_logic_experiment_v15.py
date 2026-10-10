#!/usr/bin/env python3
"""Execute translated actual v15 command methods against a small SDK mock.

Checks duration, cancellation and translation ownership. Does NOT compile
Enforce, emulate native graph transitions or validate gameplay animation.
"""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
world_root = ROOT / 'movement-logic-experiments/MovementLabMovementLogicTest_v15/StartGateSource/Scripts/4_World'
# Enforce requires matching parameter names as well as types on overrides.
# These names come from human.c and DayZPlayerImplement in the official SDK.
expected_names = {
    'CommandHandler': ('pDt', 'pCurrentCommandID', 'pCurrentCommandFinished'),
    'ModCommandHandlerInside': ('pDt', 'pCurrentCommandID', 'pCurrentCommandFinished'),
    'PreAnimUpdate': ('pDt',),
    'PrePhysUpdate': ('pDt',),
    'PostPhysUpdate': ('pDt',),
}
for file in world_root.glob('*.c'):
    for name, args in re.findall(r'override\s+\w+\s+(\w+)\s*\(([^)]*)\)', file.read_text()):
        if name in expected_names:
            actual = tuple(arg.strip().split()[-1] for arg in args.split(',') if arg.strip())
            assert actual == expected_names[name], (file.name, name, actual)

# Confirm the clean rebuild retained v11's ordinary methods verbatim.
baseline = ROOT / 'movement-logic-test/MovementLabMovementLogicTest'
variant = ROOT / 'movement-logic-experiments/MovementLabMovementLogicTest_v15'
def method(text, name):
    m = re.search(r'\b(?:void|bool|float)\s+' + name + r'\([^)]*\)\s*\{', text)
    assert m, name
    start = m.start(); opening = text.index('{', start); depth = 1; i = opening + 1
    while depth:
        depth += (text[i] == '{') - (text[i] == '}'); i += 1
    return text[start:i]
world = (world_root / 'MovementLabStartGate.c').read_text()
old_world = (baseline / 'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
for name in ['MovementLabCancelStart','MovementLabSetBrakingActive','MovementLabIsStarting','MovementLabGetStartSpeed','MovementLabCommandStart']:
    assert method(world, name) == method(old_world, name), name
new_mission = (variant / 'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text().replace('[MovementLab v15 / v11 base]', '[MovementLab v11]')
old_mission = (baseline / 'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
for name in ['MovementLabCancelStart','MovementLabCancelBrake','MovementLabBeginBrake','MovementLabUpdateBrake','MovementLabApplyFilters','OnInit','OnMissionFinish']:
    assert method(new_mission, name) == method(old_mission, name), name
source = (ROOT / "movement-logic-experiments/MovementLabMovementLogicTest_v15/StartGateSource/Scripts/4_World/MovementLabMovingReversal.c").read_text()

probe = """
class HandoffProbe : public PlayerBase
{
    bool m_MovementLabReversalResume;
    bool m_MovementLabReversalOwnsHandoff;
    float m_MovementLabReversalHandoffTime;
    float m_MovementLabReversalForward;
    float m_MovementLabReversalSide;
    bool m_MovementLabWasInput;
"""
for name in ['MovementLabReversalEnded','MovementLabCancelReversalHandoff','MovementLabResumeMovingReversal']:
    probe += '    ' + method(world, name) + '\n'
source += probe + '}\n'
source = re.sub(r'^\s*Print\([^\n]*\);', '', source, flags=re.M)
source = source.replace('protected ', '').replace('override ', '')
source = source.replace('void MovementLabNativeBraceTable(', 'MovementLabNativeBraceTable(')
source = source.replace('void MovementLabMovingReversalCommand(', 'MovementLabMovingReversalCommand(')
source = source.replace('ref MovementLabNativeBraceTable', 'MovementLabNativeBraceTable*')
source = source.replace('PlayerBase m_Player', 'PlayerBase* m_Player')
source = source.replace('Human player', 'Human* player')
source = source.replace('PlayerBase player', 'PlayerBase* player')
source = source.replace('MovementLabNativeBraceTable table', 'MovementLabNativeBraceTable* table')
source = source.replace('HumanMovementState state = new HumanMovementState();', 'HumanMovementState state;')
source = source.replace('HumanAnimInterface anim', 'HumanAnimInterface& anim')
source = source.replace('player.', 'player->').replace('m_Player.', 'm_Player->').replace('m_Table.', 'm_Table->')
source = source.replace(' : HumanCommandScript', ' : public HumanCommandScript')
source = source.replace('static ', 'inline static ')
source = source.replace('vector.Zero', 'Vec{}').replace('vector ', 'Vec ')
for name in ('MovementLabStartGate', 'MovementLabReversalSettings', 'MovementLabReversalCurve', 'DayZPlayerConstants', 'HumanInputControllerOverrideType', 'Math'):
    source = source.replace(name + '.', name + '::')
source = re.sub(r'(class [^\n]+\n\{)', r'\1\npublic:', source)
source = re.sub(r'^    (float|int|bool) (m_\w+);', r'    \1 \2 = 0;', source, flags=re.M)
source = re.sub(r'^}', '};', source, flags=re.M)

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
struct PlayerBase { HumanAnimInterface anim;bool alive=true,unconscious=false,raised=false,emote=false,item=false,falling=false,ended=false;Vec position;Vec velocity;InputState input;HumanCommandMove move;int stance=0;void MovementLabCancelStart(){}HumanInputController GetInputController(){return {&input};}HumanCommandMove GetCommand_Move(){return move;}void GetMovementState(HumanMovementState& s){s.m_iStanceIdx=stance;}
 HumanAnimInterface& GetAnimInterface(){return anim;}Vec GetPosition(){return position;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsEmotePlaying(){return emote;}void* GetEntityInHands(){return item?this:nullptr;}bool PhysicsIsFalling(bool){return falling;}void MovementLabReversalEnded(){ended=true;}void PhysicsGetVelocity(Vec& v){v=velocity;}
};
using Human=PlayerBase;
constexpr int UAMoveForward=0,UAMoveBack=1,UAMoveLeft=2,UAMoveRight=3,UAWalkRunTemp=4,UAWalkRunForced=5;
struct Action { float value=0;float LocalValue(){return value;} };
struct API { std::array<Action,6> a;Action& GetInputByID(int i){return a[i];} } api;
API& GetUApi(){return api;}
struct UI { bool menu=false;void* GetMenu(){return menu?this:nullptr;} };
struct Mission { bool pause=false;operator bool()const{return true;}bool IsPaused(){return pause;} };
struct Game { UI ui;Mission mission;UI& GetUIManager(){return ui;}Mission& GetMission(){return mission;} } game;
Game& GetGame(){return game;}
struct HumanCommandScript { Vec translation;bool finished=false,rotationLocked=false;int commands=0;std::array<float,3> variables{};
 void SetFlagFinished(bool v){finished=v;}void PreAnim_SetFloat(int id,float value){variables[id]=value;}void PreAnim_CallCommand(int,int,int){commands++;}void PrePhys_GetTranslation(Vec& t){t=translation;}void PrePhys_SetTranslation(Vec t){translation=t;}void PostPhys_LockRotation(){rotationLocked=true;}
};
'''
tests = r'''
int main(){
 for(int fps:{30,60,144})for(float angle:{-90.f,90.f,0.f,180.f,-45.f,135.f}){
  game={};api={};api.a[0].value=1;MovementLabStartGate::Enabled=true;MovementLabReversalSettings::Enabled=true;
  PlayerBase player;MovementLabNativeBraceTable table(&player);assert(table.Valid());
  float oldF=std::cos(angle*Math::DEG2RAD),oldS=std::sin(angle*Math::DEG2RAD);
  MovementLabMovingReversalCommand cmd(&player,&table,angle,-oldF,-oldS);cmd.OnActivate();
  float dt=1.f/fps,total=0;int frames=0,zeroFrames=0;bool running=true;float moved=0;
  while(running && frames++<fps){
   cmd.translation={{.1f,-.02f,-.3f}};cmd.PreAnimUpdate(dt);cmd.PrePhysUpdate(dt);running=cmd.PostPhysUpdate(dt);total+=dt;
   assert(cmd.translation[1]==-.02f);assert(!cmd.rotationLocked);assert(cmd.commands==1);assert(cmd.variables[table.Speed]==2);
   float perpendicular=cmd.translation[0]*oldF-cmd.translation[2]*oldS;
   assert(std::abs(perpendicular)<.00001f);
   float len=std::sqrt(cmd.translation[0]*cmd.translation[0]+cmd.translation[2]*cmd.translation[2]);moved+=len;
   if(len<.00001f)zeroFrames++;
   assert(cmd.variables[table.Direction]>=-180 && cmd.variables[table.Direction]<=180);
   assert(std::abs(cmd.variables[table.Direction] - (cmd.m_Time>=.18f ? cmd.m_TargetAngle : angle))<.0001f);
  }
  assert(!running && total>=.50f && total<.50f+dt+.0001f);assert(zeroFrames<=1);assert(moved>.2f);
  assert(std::abs(cmd.translation[0]+oldS*cmd.m_BaseSpeed*dt)<.0001f);
  assert(std::abs(cmd.translation[2]+oldF*cmd.m_BaseSpeed*dt)<.0001f);
  cmd.OnDeactivate();assert(player.ended);
 }
 for(int reason=0;reason<11;reason++){
  game={};api={};api.a[0].value=1;MovementLabStartGate::Enabled=true;MovementLabReversalSettings::Enabled=true;
  PlayerBase player;MovementLabNativeBraceTable table(&player);MovementLabMovingReversalCommand cmd(&player,&table,90,0,-1);
  cmd.OnActivate();
  if(reason==0)MovementLabStartGate::Enabled=false;if(reason==1)MovementLabReversalSettings::Enabled=false;
  if(reason==2)player.alive=false;if(reason==3)player.unconscious=true;if(reason==4)player.raised=true;
  if(reason==5)player.item=true;if(reason==6)player.falling=true;if(reason==7)game.ui.menu=true;if(reason==8)game.mission.pause=true;
  if(reason==10)api={};cmd.PreAnimUpdate(reason==9?.3f:.016f);assert(cmd.finished);assert(!cmd.PostPhysUpdate(.016f));assert(cmd.commands==1);
 }
 for(float t:{.10f,.18f}){
  assert(std::abs(MovementLabReversalCurve::OldWeight(t-.000001f)-MovementLabReversalCurve::OldWeight(t+.000001f))<.0001f);
  assert(std::abs(MovementLabReversalCurve::NewWeight(t-.000001f)-MovementLabReversalCurve::NewWeight(t+.000001f))<.0001f);
 }
 float prev=0;
 for(int i=180;i<=500;i++){float gain=MovementLabReversalCurve::NewWeight(i*.001f);assert(gain>=prev);assert(gain<=1.0001f);prev=gain;}
 assert(std::abs(prev-1)<.00001f);

 for(int fps:{30,60,144})for(int direction=0;direction<4;direction++){
  game={};api={};MovementLabStartGate::Enabled=true;MovementLabReversalSettings::Enabled=true;
  api.a[direction].value=1;HandoffProbe probe;probe.MovementLabReversalEnded();
  assert(!probe.MovementLabResumeMovingReversal(1.f/fps,2));assert(probe.m_MovementLabReversalResume);
  float expected=direction==0?0:direction==1?180:direction==2?-90:90;int frames=0;
  while(probe.m_MovementLabReversalResume && frames++<fps){
   bool handled=probe.MovementLabResumeMovingReversal(1.f/fps,1);
   if(handled){assert(probe.input.angleOn && probe.input.speedOn);assert(std::abs(probe.input.angle-expected)<.0001f);assert(probe.input.speed==2);}
  }
  assert(!probe.m_MovementLabReversalResume);assert(!probe.input.angleOn && !probe.input.speedOn);assert(probe.m_MovementLabWasInput);
 }
 for(int reason=0;reason<5;reason++){
  game={};api={};api.a[2].value=1;MovementLabStartGate::Enabled=true;MovementLabReversalSettings::Enabled=true;
  HandoffProbe probe;probe.MovementLabReversalEnded();assert(probe.MovementLabResumeMovingReversal(.016f,1));
  if(reason==0)api={};if(reason==1)MovementLabReversalSettings::Enabled=false;if(reason==2)game.ui.menu=true;if(reason==3)probe.input.walk=true;if(reason==4)probe.stance=1;
  assert(!probe.MovementLabResumeMovingReversal(.016f,1));assert(!probe.input.angleOn && !probe.input.speedOn);
 }
 PlayerBase invalid;invalid.anim.invalid=0;MovementLabNativeBraceTable table(&invalid);assert(!table.Valid());
 std::cout<<"Actual translated v15 command passed at 30/60/144 FPS: continuous directional motion, no dwell, single brace request, recovery to full speed, vertical preservation, cancellations and override signatures. Clean v11 startup/braking method equality and native direction/gait handoff checks passed. Native animation/Enforce behavior unverified.\n";
}
'''

with tempfile.TemporaryDirectory(prefix='movementlab-v15-check-') as temp:
    cpp = Path(temp) / 'check.cpp'
    binary = Path(temp) / 'check'
    cpp.write_text(sdk + source + tests)
    subprocess.run(['g++', '-std=c++17', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
