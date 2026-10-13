from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'viewmodel-prototype/MovementLabViewmodelPrototype_v1'
# Exercise unchanged actual movement controller and existing pose mappings.
base=(ROOT/'tools/check_aim_linked_v2_revision49.py').read_text().replace("ctrl-mode-test/MovementLabAim_Linked_v2_Revision49", "viewmodel-prototype/MovementLabViewmodelPrototype_v1")
exec(compile(base,'inherited-movement-regressions','exec'))
s=(SOURCE/'StartGateSource/Scripts/5_Mission/MovementLabViewmodelUI.c').read_text()
sdk=Path('/tmp/dayz-script-diff/scripts/3_game/gameplay.c').read_text()
for name in ('GetDummyPlayer','SetModelOrientation','SetModelPosition','UpdateItemInHands','SetPlayer'):assert name+'(' in sdk
assert not any(word in s for word in ('CreatePlayer(', 'CreateObject', 'SetOrientation(', 'SetTransform(', 'OverrideMovement', 'OverrideAim', 'StartAction(', 'Fire('))
assert 'previewDummy == player' in s and 'm_PoseVar < 0' in s
prior=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision49'
for p in (prior/'StartGateSource').rglob('*'):
 if p.is_file():assert p.read_bytes()==(SOURCE/'StartGateSource'/p.relative_to(prior/'StartGateSource')).read_bytes(),p
master=(SOURCE/'WorkspacePatches/master.agr').read_text();native=Path('/tmp/player-main-upload/player_main/master.agr').read_text()
extra='$Node AnimNodeBlend { "InventoryViewmodelBlend" "" "MovementLabViewmodelPreview" "InventoryIdleG" "APoseSrc" 3 }'
assert master.replace('\n'+extra,'',1).replace('"InventoryIK" "" "InventoryViewmodelBlend"','"InventoryIK" "" "InventoryIdleG"',1)==native
assert '"APoseSrc" "" "Locomotion.ErcRas.Idle" "0.0"' in master
assert '#Var MovementLabViewmodelPreview float 0 0 1 ""' in (SOURCE/'WorkspacePatches/player_main.agr').read_text()
layout=(SOURCE/'StartGateSource/GUI/MovementLabViewmodel.layout').read_text();assert 'PlayerPreviewWidgetClass MovementLabViewmodelPreview' in layout and layout.count('ignorepointer 1')==2
# Compile the actual UI state/ownership logic; mock renderer cannot validate pixels.
code=s[:s.index('modded class IngameHud')]
code=code.replace('class MovementLabViewmodelUI','struct MovementLabViewmodelUI').replace('protected ','')
code=code.replace('static ref MovementLabViewmodelUI s_Instance;', 'inline static MovementLabViewmodelUI* s_Instance=nullptr;')
code=code.replace('ref array<EntityAI> m_HiddenClothes = new array<EntityAI>();','EntityArray m_HiddenClothes;')
code=code.replace('void ~MovementLabViewmodelUI()', '~MovementLabViewmodelUI()')
for typ in ('Widget','PlayerPreviewWidget','PlayerBase','EntityAI','DayZPlayer','HumanAnimInterface','HumanCommandWeapons','MovementLabViewmodelUI'):
 code=re.sub(r'\b'+typ+r' (\w+)',typ+r'* \1',code)
code=code.replace('MovementLabViewmodelUI* GetInstance()', 'MovementLabViewmodelUI* GetInstance()')
code=code.replace('foreach (EntityAI* clothing : m_HiddenClothes)', 'for (EntityAI* clothing : m_HiddenClothes.vals)')
code=re.sub(r'\bnull\b','nullptr',code).replace('s_Instance = nullptr;', 'delete s_Instance; s_Instance = nullptr;')
code=code.replace('inline static MovementLabViewmodelUI* delete s_Instance; s_Instance = nullptr;', 'inline static MovementLabViewmodelUI* s_Instance=nullptr;')
for name in ('MovementLabStartGate','WidgetFlags','Camera','PlayerBase','PlayerPreviewWidget'):code=code.replace(name+'.',name+'::')
for name in ('GetGame()','GetInput()','GetUIManager()','GetMission()','GetWorkspace()','m_Root','m_Preview','instance','m_HiddenPlayer','player','clothing','held','previewDummy','m_Dummy','previewAnim','GetAnimInterface()','GetItemAccessor()','GetItemInHands()','GetInputController()','GetWeaponManager()','realWeapons','s_Instance'):
 code=code.replace(name+'.',name+'->')
code=re.sub(r'Print\([^\n]+\);','Print("trace");',code)
code=re.sub(r'\bbool (m_\w+);',r'bool \1=false;',code)
code=re.sub(r'\bint (m_\w+);',r'int \1=0;',code)
code=re.sub(r'\b(Widget|PlayerPreviewWidget|PlayerBase|EntityAI|DayZPlayer)\* (m_\w+);',r'\1* \2=nullptr;',code)
code=re.sub(r'\bstring\b','std::string',code)
code=code.rstrip()+';\n'
prefix=r'''
#include <cassert>
#include <string>
#include <vector>
#include <iostream>
struct EntityAI{bool invisible=false,deleted=false,weapon=true;int invisWrites=0;bool ToDelete(){return deleted;}void SetInvisible(bool value){invisible=value;invisWrites++;}bool IsWeapon(){return weapon;}std::string GetType(){return "M4A1";}};
struct EntityArray{std::vector<EntityAI*> vals;void Insert(EntityAI* e){vals.push_back(e);}void Clear(){vals.clear();}};
struct Accessor{bool hidden=false;void HideItemInHands(bool x){hidden=x;}};
struct Input{bool free=false,tracking=false;bool CameraIsFreeLook(){return free;}bool CameraIsTracking(){return tracking;}};
struct Manager{bool running=false;bool IsRunning(){return running;}};
struct HumanCommandWeapons{int action=-1;int GetRunningAction(){return action;}};
struct HumanAnimInterface{bool marker=true;int BindVariableFloat(const char* s){std::string n=s;if(n=="MovementLabViewmodelPreview")return marker?50:-1;if(n=="AimX")return 51;if(n=="AimY")return 52;if(n=="AimIKX")return 53;return -1;}int BindVariableBool(const char*){return 54;}};
struct DayZPlayer:EntityAI{HumanAnimInterface anim;Accessor accessor;Input input;Manager manager;HumanCommandWeapons weapons;EntityAI gun,body,gloves,vest;bool alive=true,unconscious=false,raised=true,third=false,iron=false,optics=false,lift=false,blocked=false,move=true,hasGun=true;int animWrites=0;float pose=0,aimX=99,aimY=99,aimIK=99;bool poseRaised=false;
 bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsInThirdPerson(){return third;}bool IsInIronsights(){return iron;}bool IsInOptics(){return optics;}bool IsLiftWeapon(){return lift;}bool IsWeaponObstructionBlockingADS(){return blocked;}void* GetCommand_Move(){return move?this:nullptr;}EntityAI* GetItemInHands(){return hasGun?&gun:nullptr;}Input* GetInputController(){return &input;}Manager* GetWeaponManager(){return &manager;}HumanCommandWeapons* GetCommandModifier_Weapons(){return &weapons;}HumanAnimInterface* GetAnimInterface(){return &anim;}Accessor* GetItemAccessor(){return &accessor;}
 void AnimSetFloat(int id,float x){animWrites++;if(id==50)pose=x;if(id==51)aimX=x;if(id==52)aimY=x;if(id==53)aimIK=x;}void AnimSetBool(int id,bool x){assert(id==54);animWrites++;poseRaised=x;}
 EntityAI* FindAttachmentBySlotName(std::string n){if(n=="Body")return &body;if(n=="Gloves")return &gloves;if(n=="Vest")return &vest;return nullptr;}
};
struct PlayerBase:DayZPlayer{static PlayerBase* Cast(PlayerBase* p){return p;}};
struct Widget{bool visible=false,linked=true;int flags=0;virtual ~Widget(){};virtual Widget* FindAnyWidget(const char*){return nullptr;}void SetFlags(int x){flags|=x;}void Show(bool x){visible=x;}void Unlink(){linked=false;visible=false;}};
struct PlayerPreviewWidget:Widget{PlayerBase* source=nullptr;DayZPlayer dummy;DayZPlayer* overrideDummy=nullptr;bool ready=true;int binds=0,updates=0;std::string orientation,position;float x=0,y=0,w=0,h=0;static PlayerPreviewWidget* Cast(Widget* p){return dynamic_cast<PlayerPreviewWidget*>(p);}void SetPlayer(PlayerBase* p){source=p;binds++;}void UpdateItemInHands(EntityAI*){updates++;}DayZPlayer* GetDummyPlayer(){if(!ready)return nullptr;return overrideDummy?overrideDummy:&dummy;}void SetModelOrientation(std::string v){orientation=v;}void SetModelPosition(std::string v){position=v;}void SetPos(float a,float b){x=a;y=b;}void SetSize(float a,float b){w=a;h=b;}};
struct Root:Widget{PlayerPreviewWidget preview;bool child=true;Widget* FindAnyWidget(const char* n){assert(std::string(n)=="MovementLabViewmodelPreview");return child?&preview:nullptr;}};
struct Workspace{Root root;bool fail=false;int creates=0;Widget* CreateWidgets(const char* path){assert(std::string(path)=="MovementLabStartGate/GUI/MovementLabViewmodel.layout");creates++;return fail?nullptr:&root;}};
struct GameInput{bool focus=true;bool HasGameFocus(){return focus;}};struct UI{bool menu=false;void* GetMenu(){return menu?this:nullptr;}};struct Mission{bool pause=false;bool IsPaused(){return pause;}};
struct Game{int time=0;int GetTime(){return time;}PlayerBase* player=nullptr;bool multi=false;GameInput input;UI ui;Mission mission;Workspace workspace;bool IsMultiplayer(){return multi;}PlayerBase* GetPlayer(){return player;}GameInput* GetInput(){return &input;}UI* GetUIManager(){return &ui;}Mission* GetMission(){return &mission;}Workspace* GetWorkspace(){return &workspace;}}game;
Game* GetGame(){return &game;}struct MovementLabStartGate{inline static bool Enabled=true;};struct Camera{inline static bool external=false;static void* GetCurrentCamera(){return external?&external:nullptr;}};struct WidgetFlags{static constexpr int IGNOREPOINTER=1,NOFOCUS=2,SOURCEALPHA=4,BLEND=8;};int prints=0;void Print(const char*){prints++;}
'''
main=r'''
int main(){
 // Separate dummy gets pose writes; real player's gameplay/angles never do.
 {PlayerBase p;game={};game.player=&p;MovementLabViewmodelUI vm;vm.m_Enabled=true;vm.Update();assert(p.invisible && p.accessor.hidden && p.body.invisible && p.gloves.invisible && p.vest.invisible);auto& preview=game.workspace.root.preview;assert(game.workspace.root.visible && preview.dummy.pose==1 && preview.dummy.aimX==0 && preview.dummy.aimY==0 && preview.dummy.aimIK==0 && preview.dummy.poseRaised);assert(p.animWrites==0 && preview.orientation=="0 180 0");for(int n=0;n<100;n++)vm.Update();assert(preview.binds==1 && game.workspace.creates==1 && p.animWrites==0);vm.Stop();assert(!p.invisible && !p.accessor.hidden && !p.body.invisible && !p.gloves.invisible && !p.vest.invisible && !game.workspace.root.visible && preview.dummy.pose==0);}
 // All exit states restore the real body/weapon instead of leaving it hidden.
 for(int exit=0;exit<13;exit++){PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;Camera::external=false;MovementLabViewmodelUI vm;vm.m_Enabled=true;vm.Update();assert(p.invisible);
  if(exit==0)p.iron=true;if(exit==1)p.optics=true;if(exit==2)p.third=true;if(exit==3)p.raised=false;if(exit==4)p.input.free=true;if(exit==5)p.manager.running=true;if(exit==6)p.weapons.action=1;if(exit==7)game.ui.menu=true;if(exit==8)p.alive=false;if(exit==9)p.unconscious=true;if(exit==10)game.multi=true;if(exit==11)Camera::external=true;if(exit==12)MovementLabStartGate::Enabled=false;vm.Update();assert(!p.invisible && !p.accessor.hidden && !game.workspace.root.visible && p.animWrites==0);}
 // Renderer/missing variable failures never hide or freeze the world player.
 for(int fault=0;fault<5;fault++){PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;Camera::external=false;MovementLabViewmodelUI vm;vm.m_Enabled=true;if(fault==0)game.workspace.fail=true;if(fault==1)game.workspace.root.child=false;if(fault==2)game.workspace.root.preview.ready=false;if(fault==3)game.workspace.root.preview.overrideDummy=&p;if(fault==4)game.workspace.root.preview.dummy.anim.marker=false;vm.Update();assert(!p.invisible && !p.accessor.hidden && p.animWrites==0 && !game.workspace.root.visible);}

 // Missing widget is attempted once, and late graph setup can recover safely.
 {PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;Camera::external=false;MovementLabViewmodelUI vm;vm.m_Enabled=true;game.workspace.fail=true;for(int n=0;n<100;n++)vm.Update();assert(game.workspace.creates==1 && !p.invisible);}
 {PlayerBase p;game={};game.player=&p;MovementLabViewmodelUI vm;vm.m_Enabled=true;game.workspace.root.preview.dummy.anim.marker=false;vm.Update();assert(!p.invisible);game.workspace.root.preview.dummy.anim.marker=true;game.time=600;vm.Update();assert(p.invisible && p.animWrites==0);}
 // Toggle cleanup and framing are independent of mouse/world direction.
 {PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;MovementLabViewmodelUI::Toggle();MovementLabViewmodelUI::Tick();assert(p.invisible);MovementLabViewmodelUI::CycleFrame();assert(game.workspace.root.preview.position=="0 -0.8 0.05");MovementLabViewmodelUI::Toggle();assert(!p.invisible && !p.accessor.hidden);MovementLabViewmodelUI::Shutdown();assert(!game.workspace.root.linked);}
 std::cout<<"Actual viewmodel controller: independent dummy ownership/fixed pose, no real animation writes, cached renderer, all exit visibility recovery, missing renderer/marker failures, toggle/framing/shutdown passed. Native overlay pixels/pose/framing still unverified.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-viewmodel-') as d:
 p=Path(d);(p/'test.cpp').write_text(prefix+code+main);subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
