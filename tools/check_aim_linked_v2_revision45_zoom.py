"""Execute the real zoom-sight handler against native API mocks."""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision45'
s=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabAltADS.c').read_text()
a=s.index('    void MovementLabUpdateZoomSightSwitch()');start=s.index('{',a);depth=1;i=start+1
while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
method=s[a:i]
method=method.replace('UAInput sightZoomInput','UAInput* sightZoomInput').replace('Weapon_Base sightZoomWeapon','Weapon_Base* sightZoomWeapon').replace('ItemOptics sightZoomOptic','ItemOptics* sightZoomOptic').replace('Weapon_Base.Cast(GetEntityInHands())','GetEntityInHands()').replace('MovementLabStartGate.','MovementLabStartGate::')
method=method.replace('HumanInputController sightZoomController','HumanInputController* sightZoomController').replace('UAInput sightZoomHoldInput','UAInput* sightZoomHoldInput').replace('sightZoomHoldInput.','sightZoomHoldInput->').replace('sightZoomController.','sightZoomController->');method=re.sub(r'        Print\([^\n]+\);','',method)
for name in ('GetGame()','GetUApi()','GetInput()','GetUIManager()','GetMission()','GetDayZPlayerInventory()','GetWeaponManager()','sightZoomInput','sightZoomWeapon','sightZoomOptic'):method=method.replace(name+'.',name+'->')
alt=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabAltADS.c').read_text()
assert alt.count('MovementLabUpdateZoomSightSwitch();')==1
assert s.index('void MovementLabUpdateZoomSightSwitch()') < s.index('override int CameraHandler(')
assert 'super.HandleOptic(optic, inHands, pInputs, pExitOptics);' in s
assert 'pExitOptics = false;' in s
start=s.index('    override void HandleOptic(');begin=s.index('{',start);end=begin+1;depth=1
while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
opticmethod=s[start:end].replace('override ', '').replace('notnull ItemOptics optic','ItemOptics* optic').replace('HumanInputController pInputs','HumanInputController* pInputs').replace('out bool pExitOptics','bool& pExitOptics').replace('super.HandleOptic','NativePlayer::HandleOptic').replace('MovementLabStartGate.','MovementLabStartGate::').replace('GetGame().','GetGame()->')
method+=opticmethod
# Verify native API naming rather than inventing alternate camera controls.
sdk=Path('/tmp/dayz-script-diff/scripts/4_world/entities/dayzplayerimplement.c').read_text()
for symbol in ('SwitchOptics','SetIronsights','CanEnterIronsights','GetAttachedOptics','IsSightOnly'):assert symbol+'(' in sdk
cpp=r'''
#include <cassert>
#include <iostream>
struct Player;
struct UAInput{bool pressed=false;bool LocalPress(){return pressed;}float value=0;float LocalValue(){return value;}};
constexpr int UAZoomInToggle=1;
struct InputAPI{UAInput zoom,hold;UAInput* GetInputByName(const char*){return &hold;}UAInput* GetInputByID(int id){assert(id==UAZoomInToggle);return &zoom;}}api;
struct Input{bool focus=true;bool HasGameFocus(){return focus;}};
struct UI{bool menu=false;void* GetMenu(){return menu?this:nullptr;}};
struct Mission{bool paused=false;bool IsPaused(){return paused;}};
struct Game{Player* player=nullptr;bool multi=false;int time=0;int GetTime(){return time;}Input input;UI ui;Mission mission;Player* GetPlayer(){return player;}bool IsMultiplayer(){return multi;}Input* GetInput(){return &input;}UI* GetUIManager(){return &ui;}Mission* GetMission(){return &mission;}}game;
Game* GetGame(){return &game;}InputAPI* GetUApi(){return &api;}
struct MovementLabStartGate{inline static bool Enabled=true;};
struct ItemOptics{bool sightOnly=false;int magnification=2,enter=0,exit=0;bool IsSightOnly(){return sightOnly;}};
struct Weapon_Base{ItemOptics scope;bool hasScope=true,canIron=true,wasIron=true;bool CanEnterIronsights(){return canIron;}ItemOptics* GetAttachedOptics(){return hasScope?&scope:nullptr;}void SetWasIronSight(bool x){wasIron=x;}};
struct Inventory{bool processing=false;bool IsProcessing(){return processing;}};
struct Manager{bool running=false;bool IsRunning(){return running;}};
struct HumanInputController{bool zoom=false;bool IsZoom(){return zoom;}};
struct NativePlayer{int nativeOpticCalls=0;void HandleOptic(ItemOptics*,bool,HumanInputController*,bool& exit){nativeOpticCalls++;exit=true;}};
struct Player:NativePlayer{
 HumanInputController controller;HumanInputController* GetInputController(){return &controller;}int m_MovementLabSightZoomTime=-1;
 bool m_MovementLabSightZoomDown=false,m_CameraIronsight=true,m_CameraOptics=false,alive=true,unconscious=false,raised=true,lift=false,blocked=false,raiseComplete=true,fighting=false,melee=false,hasWeapon=true,hasManager=true;int switches=0;Weapon_Base weapon;Inventory inventory;Manager manager;
 bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsLiftWeapon(){return lift;}bool IsWeaponObstructionBlockingADS(){return blocked;}bool IsWeaponRaiseCompleted(){return raiseComplete;}bool IsFighting(){return fighting;}void* GetCommand_Melee2(){return melee?this:nullptr;}Weapon_Base* GetEntityInHands(){return hasWeapon?&weapon:nullptr;}Inventory* GetDayZPlayerInventory(){return &inventory;}Manager* GetWeaponManager(){return hasManager?&manager:nullptr;}
 void SetIronsights(bool x){m_CameraIronsight=x;}void SwitchOptics(ItemOptics* scope,bool state){assert(scope==&weapon.scope);m_CameraOptics=state;switches++;if(state)scope->enter++;else scope->exit++;}
'''+method+r'''
};
void press(Player& p){game.time++;api.zoom.value=1;p.MovementLabUpdateZoomSightSwitch();}
void release(Player& p){game.time++;api.zoom.value=0;p.MovementLabUpdateZoomSightSwitch();}
int main(){
 for(int fps:{30,60,144}){
  Player p;game={};game.player=&p;api={};MovementLabStartGate::Enabled=true;
  for(int cycle=0;cycle<8;cycle++){
   press(p);assert(p.m_CameraOptics && !p.m_CameraIronsight && !p.weapon.wasIron);int count=p.switches;for(int n=0;n<fps;n++)p.MovementLabUpdateZoomSightSwitch();assert(p.switches==count);assert(p.weapon.scope.magnification==2);
   release(p);press(p);assert(!p.m_CameraOptics && p.m_CameraIronsight && p.weapon.wasIron);release(p);
  }
  assert(p.weapon.scope.enter==8 && p.weapon.scope.exit==8);
 }
 for(int reason=0;reason<19;reason++){
  Player p;game={};api={};game.player=&p;MovementLabStartGate::Enabled=true;
  if(reason==0)MovementLabStartGate::Enabled=false;if(reason==1)game.multi=true;if(reason==2)game.input.focus=false;if(reason==3)game.ui.menu=true;if(reason==4)game.mission.paused=true;if(reason==5)p.alive=false;if(reason==6)p.unconscious=true;if(reason==7)p.raised=false;if(reason==8)p.m_CameraIronsight=false;if(reason==9)p.hasWeapon=false;if(reason==10)p.weapon.canIron=false;if(reason==11)p.weapon.hasScope=false;if(reason==12)p.weapon.scope.sightOnly=true;if(reason==13)p.lift=true;if(reason==14)p.blocked=true;if(reason==15)p.raiseComplete=false;if(reason==16)p.fighting=true;if(reason==17)p.inventory.processing=true;if(reason==18)p.manager.running=true;
  press(p);assert(p.switches==0);
 }


 // Wheel optics handler blocked only for local ADS attached optics.
 for(int scenario=0;scenario<6;scenario++){
  Player p;game={};api={};game.player=&p;MovementLabStartGate::Enabled=true;bool inHands=false,exit=true;
  if(scenario==1)p.m_CameraIronsight=false;if(scenario==2)inHands=true;if(scenario==3)game.multi=true;if(scenario==4)MovementLabStartGate::Enabled=false;if(scenario==5)game.player=nullptr;
  p.HandleOptic(&p.weapon.scope,inHands,&p.controller,exit);if(scenario==0)assert(!exit && p.nativeOpticCalls==0);else assert(exit && p.nativeOpticCalls==1);
 }
 // Hold-zoom and native controller zoom must both switch even with toggle unused.
 for(int source:{0,1}){Player p;game={};api={};game.player=&p;MovementLabStartGate::Enabled=true;game.time++;if(source==0)api.hold.value=1;else p.controller.zoom=true;p.MovementLabUpdateZoomSightSwitch();assert(p.switches==1);for(int n=0;n<10;n++)p.MovementLabUpdateZoomSightSwitch();assert(p.switches==1);game.time++;api.hold.value=0;p.controller.zoom=false;p.MovementLabUpdateZoomSightSwitch();game.time++;if(source==0)api.hold.value=1;else p.controller.zoom=true;p.MovementLabUpdateZoomSightSwitch();assert(p.switches==2);}
 // Duplicate LocalPress in the same frame cannot toggle twice.
 {Player p;game={};api={};game.player=&p;MovementLabStartGate::Enabled=true;api.hold.pressed=true;game.time++;p.MovementLabUpdateZoomSightSwitch();p.MovementLabUpdateZoomSightSwitch();assert(p.switches==1);api.hold.pressed=false;}
 // Press before ADS or in a menu must not become a delayed switch on entry.
 {Player p;game={};api={};game.player=&p;MovementLabStartGate::Enabled=true;p.m_CameraIronsight=false;press(p);p.m_CameraIronsight=true;p.MovementLabUpdateZoomSightSwitch();assert(p.switches==0);release(p);press(p);assert(p.switches==1);}
 {Player p;game={};api={};game.player=&p;game.ui.menu=true;press(p);game.ui.menu=false;p.MovementLabUpdateZoomSightSwitch();assert(p.switches==0);release(p);press(p);assert(p.switches==1);}
 std::cout<<"Actual ADS lookzoom handler: iron/scope switching, release/repress, hold-no-repeat, scope magnification/memory, invalid state gates, held-beforeADS/menu all passed. Other modules unchanged; native key/camera test pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-zoom-') as d:
 p=Path(d);(p/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17','-O0',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
