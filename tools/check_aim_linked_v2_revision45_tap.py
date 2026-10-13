from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision45'
s=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text();a=s.index('    override void OnMouseButtonPress(');b=s.index('    override void OnKeyPress(',a);methods=s[a:b].replace('override ','').replace('super.','NativeMission::').replace('MouseState.','MouseState::').replace('PlayerBase directADSPlayer','PlayerBase* directADSPlayer').replace('PlayerBase.Cast(GetGame().GetPlayer())','GetGame()->GetPlayer()')
for name in ('GetGame()','GetInput()','GetUIManager()','GetMission()','directADSPlayer'):methods=methods.replace(name+'.',name+'->')
cpp=r'''
#include <cassert>
#include <iostream>
struct PlayerBase{int requests=0;void MovementLabRightClickADS(){requests++;}};
struct Input{bool focus=true;bool HasGameFocus(){return focus;}};struct UI{bool menu=false;void* GetMenu(){return menu?this:nullptr;}};struct Mission{bool pause=false;bool IsPaused(){return pause;}};
struct Game{int time=0;Input input;UI ui;Mission mission;PlayerBase player;int GetTime(){return time;}Input* GetInput(){return &input;}UI* GetUIManager(){return &ui;}Mission* GetMission(){return &mission;}PlayerBase* GetPlayer(){return &player;}}game;
Game* GetGame(){return &game;}struct MouseState{static constexpr int RIGHT=1,LEFT=0;};
struct NativeMission{int presses=0,releases=0;void OnMouseButtonPress(int){presses++;}void OnMouseButtonRelease(int){releases++;}};
struct Probe:NativeMission{bool m_MovementLabRightADSDown=false,m_MovementLabRightADSEligible=false;int m_MovementLabRightADSTime=0;
'''+methods+r'''
};
int main(){
 for(int duration:{0,50,100,199,200,201,500,1500}){game={};Probe p;p.OnMouseButtonPress(MouseState::RIGHT);assert(game.player.requests==0);game.time=duration;p.OnMouseButtonRelease(MouseState::RIGHT);assert(game.player.requests==(duration<=200?1:0));assert(!p.m_MovementLabRightADSDown && !p.m_MovementLabRightADSEligible);p.OnMouseButtonRelease(MouseState::RIGHT);assert(game.player.requests==(duration<=200?1:0));}
 {game={};Probe p;p.OnMouseButtonPress(1);game.time=500;p.OnMouseButtonPress(1);game.time=550;p.OnMouseButtonRelease(1);assert(game.player.requests==0);game.time=600;p.OnMouseButtonPress(1);game.time=700;p.OnMouseButtonRelease(1);assert(game.player.requests==1);}
 for(int blocked:{0,1,2}){game={};Probe p;if(blocked==0)game.ui.menu=true;if(blocked==1)game.input.focus=false;if(blocked==2)game.mission.pause=true;p.OnMouseButtonPress(1);game.ui.menu=false;game.input.focus=true;game.mission.pause=false;game.time=100;p.OnMouseButtonRelease(1);assert(game.player.requests==0);}
 {game={};Probe p;p.OnMouseButtonPress(0);game.time=100;p.OnMouseButtonRelease(0);assert(game.player.requests==0 && p.presses==1 && p.releases==1);}
 std::cout<<"Actual mission RMB callbacks: noADS onpress; taps<=200ms onrelease; holds/duplicatepress/menu-start ignored; native callbacks preserved. In-game confirmation pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-ads-tap-') as d:
 p=Path(d);(p/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
