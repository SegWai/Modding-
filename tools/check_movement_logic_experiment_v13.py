#!/usr/bin/env python3
"""Execute translated actual v13 command methods against a small SDK mock.

Checks duration, cancellation and translation ownership. Does NOT compile
Enforce, emulate native graph transitions or validate gameplay animation.
"""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
world_root = ROOT / 'movement-logic-experiments/MovementLabMovementLogicTest_v13/StartGateSource/Scripts/4_World'
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
source = (ROOT / "movement-logic-experiments/MovementLabMovementLogicTest_v13/StartGateSource/Scripts/4_World/MovementLabPoseHold.c").read_text()
source = re.sub(r'^\s*Print\([^\n]*\);', '', source, flags=re.M)
source = source.replace('protected ', '').replace('override ', '')
source = source.replace('void MovementLabPoseTable(', 'MovementLabPoseTable(')
source = source.replace('void MovementLabPoseCommand(', 'MovementLabPoseCommand(')
source = source.replace('ref MovementLabPoseTable', 'MovementLabPoseTable*')
source = source.replace('PlayerBase m_Player', 'PlayerBase* m_Player')
source = source.replace('Human player', 'Human* player')
source = source.replace('PlayerBase player', 'PlayerBase* player')
source = source.replace('MovementLabPoseTable table', 'MovementLabPoseTable* table')
source = source.replace('HumanAnimInterface anim', 'HumanAnimInterface& anim')
source = source.replace('player.', 'player->').replace('m_Player.', 'm_Player->').replace('m_Table.', 'm_Table->')
source = source.replace(' : HumanCommandScript', ' : public HumanCommandScript')
source = source.replace('static ', 'inline static ')
source = source.replace('vector.Zero', 'Vec{}').replace('vector ', 'Vec ')
for name in ('MovementLabStartGate', 'MovementLabPoseSettings', 'DayZPlayerConstants', 'Math'):
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
struct Math { static float Max(float a,float b){return std::max(a,b);}static float Sqrt(float v){return std::sqrt(v);} };
struct MovementLabStartGate { inline static bool Enabled=true; };
struct DayZPlayerConstants { static const int STANCEIDX_ERECT=0, MOVEMENT_RUN=2; };
struct HumanAnimInterface { int invalid=-1;int BindCommand(const char*){return invalid>=0?-1:0;}int BindVariableFloat(const char* s){return s[8]=='S'?1:2;} };
struct PlayerBase { HumanAnimInterface anim;bool alive=true,unconscious=false,raised=false,emote=false,item=false,falling=false,ended=false;Vec position;
 HumanAnimInterface& GetAnimInterface(){return anim;}Vec GetPosition(){return position;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsEmotePlaying(){return emote;}void* GetEntityInHands(){return item?this:nullptr;}bool PhysicsIsFalling(bool){return falling;}void MovementLabPoseEnded(){ended=true;}
};
using Human=PlayerBase;
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
  game={};MovementLabStartGate::Enabled=true;MovementLabPoseSettings::Enabled=true;
  PlayerBase player;MovementLabPoseTable table(&player);assert(table.Valid());
  MovementLabPoseCommand cmd(&player,&table,angle);cmd.OnActivate();
  float dt=1.f/fps,total=0;int frames=0;bool running=true;
  while(running && frames++<fps){
   cmd.translation={{.1f,-.02f,-.3f}};cmd.PreAnimUpdate(dt);cmd.PrePhysUpdate(dt);running=cmd.PostPhysUpdate(dt);total+=dt;
   assert(cmd.translation[0]==0 && cmd.translation[2]==0);assert(cmd.translation[1]==-.02f);
   assert(cmd.variables[table.Speed]==2);assert(cmd.variables[table.Direction]==angle);assert(cmd.rotationLocked);
  }
  assert(!running && total>=.32f && total<.32f+dt+.0001f);assert(cmd.commands==frames);cmd.OnDeactivate();assert(player.ended);
 }
 for(int reason=0;reason<10;reason++){
  game={};MovementLabStartGate::Enabled=true;MovementLabPoseSettings::Enabled=true;
  PlayerBase player;MovementLabPoseTable table(&player);MovementLabPoseCommand cmd(&player,&table,90);
  cmd.OnActivate();
  if(reason==0)MovementLabStartGate::Enabled=false;if(reason==1)MovementLabPoseSettings::Enabled=false;
  if(reason==2)player.alive=false;if(reason==3)player.unconscious=true;if(reason==4)player.raised=true;
  if(reason==5)player.item=true;if(reason==6)player.falling=true;if(reason==7)game.ui.menu=true;if(reason==8)game.mission.pause=true;
  cmd.PreAnimUpdate(reason==9?.3f:.016f);assert(cmd.finished);assert(!cmd.PostPhysUpdate(.016f));assert(cmd.commands==0);
 }
 PlayerBase invalid;invalid.anim.invalid=0;MovementLabPoseTable table(&invalid);assert(!table.Valid());
 std::cout<<"Actual translated pose command passed duration/direction/translation tests at 30/60/144 FPS, cancellation and invalid binding. Native graph behavior and Enforce compilation unverified.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-v13-check-') as temp:
    cpp = Path(temp) / 'check.cpp'
    binary = Path(temp) / 'check'
    cpp.write_text(sdk + source + tests)
    subprocess.run(['g++', '-std=c++17', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
