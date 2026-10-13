"""Test actual click/raise ownership methods; native raise and cameras need game."""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision45'
s=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabAltADS.c').read_text()
def extract(name):
 a=s.index('    void '+name+'(');b=s.index('{',a);i=b+1;depth=1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i]
methods='\n'.join(extract(n) for n in ('MovementLabCancelDirectADS','MovementLabCancelAltADS','MovementLabRightClickADS','MovementLabUpdateDirectADS'))
methods=methods.replace('Weapon_Base directAimWeapon','Weapon_Base* directAimWeapon').replace('Weapon_Base.Cast(GetEntityInHands())','GetEntityInHands()').replace('null','nullptr').replace('MovementLabStartGate.','MovementLabStartGate::').replace('HumanInputControllerOverrideType.','HumanInputControllerOverrideType::')
for name in ('GetGame()','GetInput()','GetUIManager()','GetMission()','GetInputController()','directAimWeapon','GetDayZPlayerInventory()','GetWeaponManager()'):methods=methods.replace(name+'.',name+'->')
mission=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text();assert 'override void OnMouseButtonPress(int button)' in mission and 'button == MouseState.RIGHT' in mission and 'directADSPlayer.MovementLabRightClickADS();' in mission
assert s.index('MovementLabUpdateDirectADS();',s.index('override void HandleADS()')) < s.index('super.HandleADS();',s.index('override void HandleADS()'))
assert '(!IsRaised() && !m_MovementLabDirectRaise)' in s
assert 'ForceStance' not in extract('MovementLabRightClickADS')
w=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text();escape=w[w.index('protected void MovementLabLeaveAimForSprint()'):w.index('protected void MovementLabCaptureStandingModeKeys(')]
assert escape.index('MovementLabCancelAltADS();') < escape.index('OverrideRaise(HumanInputControllerOverrideType.ENABLED, false)')
cpp=r'''
#include <cassert>
#include <iostream>
struct Player;
struct Input{bool focus=true;bool HasGameFocus(){return focus;}};
struct UI{bool menu=false;void* GetMenu(){return menu?this:nullptr;}};
struct Mission{bool paused=false;bool IsPaused(){return paused;}};
struct Game{Player* player=nullptr;bool multi=false;Input input;UI ui;Mission mission;Player* GetPlayer(){return player;}bool IsMultiplayer(){return multi;}Input* GetInput(){return &input;}UI* GetUIManager(){return &ui;}Mission* GetMission(){return &mission;}}game;
Game* GetGame(){return &game;}
struct MovementLabStartGate{inline static bool Enabled=true;};
struct HumanInputControllerOverrideType{static constexpr int ENABLED=1,DISABLED=0;};
struct Controller{bool raiseOverride=false,raise=false;void OverrideRaise(int type,bool value){raiseOverride=type==1;raise=value;}};
struct ItemOptics{};
struct Weapon_Base{bool iron=true,scope=true;ItemOptics optic;bool CanEnterIronsights(){return iron;}ItemOptics* GetAttachedOptics(){return scope?&optic:nullptr;}};
struct Inventory{bool processing=false;bool IsProcessing(){return processing;}};
struct Manager{bool running=false;bool IsRunning(){return running;}};
struct Player{
 bool m_MovementLabDirectRaise=false,m_MovementLabAltADS=false,m_bADS=false,m_CameraIronsight=false,m_CameraOptics=false;
 Weapon_Base weapon,other;Weapon_Base* m_MovementLabDirectWeapon=nullptr;bool alive=true,unconscious=false,movingCommand=true,fighting=false,melee=false,hasWeapon=true,hasController=true,hasManager=true;int stance=0,exitCount=0;bool otherInHands=false;Controller controller;Inventory inventory;Manager manager;
 bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}Controller* GetInputController(){return hasController?&controller:nullptr;}void* GetCommand_Move(){return movingCommand?this:nullptr;}bool IsFighting(){return fighting;}void* GetCommand_Melee2(){return melee?this:nullptr;}Weapon_Base* GetEntityInHands(){return hasWeapon?(otherInHands?&other:&weapon):nullptr;}Inventory* GetDayZPlayerInventory(){return &inventory;}Manager* GetWeaponManager(){return hasManager?&manager:nullptr;}void ExitSights(){m_CameraIronsight=false;m_CameraOptics=false;exitCount++;}
'''+methods+r'''
};
int main(){
 for(int stance:{0,1,2,3,4,5})for(bool initiallyScoped:{false,true}){
  Player p;game={};game.player=&p;MovementLabStartGate::Enabled=true;p.stance=stance;
  p.MovementLabRightClickADS();assert(p.m_MovementLabAltADS && p.m_MovementLabDirectRaise && p.controller.raiseOverride && p.controller.raise);assert(p.stance==stance);
  for(int frame=0;frame<100;frame++){p.MovementLabUpdateDirectADS();assert(p.m_MovementLabAltADS && p.controller.raiseOverride && p.controller.raise);}
  if(initiallyScoped)p.m_CameraOptics=true;else p.m_CameraIronsight=true;p.m_bADS=true;p.MovementLabRightClickADS();assert(!p.m_MovementLabAltADS && !p.m_bADS && !p.m_CameraIronsight && !p.m_CameraOptics && !p.controller.raiseOverride && !p.m_MovementLabDirectRaise);assert(p.stance==stance);
 }
 for(int reason=0;reason<13;reason++){
  Player p;game={};game.player=&p;MovementLabStartGate::Enabled=true;
  if(reason==0)MovementLabStartGate::Enabled=false;if(reason==1)game.multi=true;if(reason==2)game.input.focus=false;if(reason==3)game.ui.menu=true;if(reason==4)game.mission.paused=true;if(reason==5)p.alive=false;if(reason==6)p.unconscious=true;if(reason==7)p.movingCommand=false;if(reason==8)p.hasWeapon=false;if(reason==9)p.weapon.iron=p.weapon.scope=false;if(reason==10)p.inventory.processing=true;if(reason==11)p.manager.running=true;if(reason==12)p.fighting=true;
  p.MovementLabRightClickADS();assert(!p.m_MovementLabAltADS && !p.m_MovementLabDirectRaise && !p.controller.raiseOverride);
 }
 for(int reason=0;reason<7;reason++){
  Player p;game={};game.player=&p;MovementLabStartGate::Enabled=true;p.MovementLabRightClickADS();assert(p.m_MovementLabDirectRaise);
  if(reason==0)p.alive=false;if(reason==1)p.unconscious=true;if(reason==2)p.hasWeapon=false;if(reason==3)p.otherInHands=true;if(reason==4)p.movingCommand=false;if(reason==5)MovementLabStartGate::Enabled=false;if(reason==6)game.multi=true;
  p.MovementLabUpdateDirectADS();assert(!p.m_MovementLabDirectRaise && !p.m_MovementLabAltADS && !p.controller.raiseOverride);
 }
 {Player p;game={};game.player=&p;MovementLabStartGate::Enabled=true;p.MovementLabRightClickADS();p.MovementLabCancelAltADS();p.controller.OverrideRaise(HumanInputControllerOverrideType::ENABLED,false);p.MovementLabUpdateDirectADS();assert(!p.m_MovementLabDirectRaise && p.controller.raiseOverride && !p.controller.raise);}
 std::cout<<"Actual RMB ADS handlers: standing/crouch/prone request and retained raise, secondclick cancel, invalidclick gates, weapon/death/stance/disable cleanup, sprint escape ownership passed. Native raise/camera confirmation pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-direct-ads-') as d:
 p=Path(d);(p/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17','-O0',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
