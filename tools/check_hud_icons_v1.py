"""Actual icon accessor and HUD translated to C++ mocks. Native render pending."""
from pathlib import Path
import json, re, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'hud-icons-test/MovementLabHUDIcons_v1'
PREVIOUS=ROOT/'viewmodel-prototype/MovementLabArmsOnlyTest_v2'
world=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
oldworld=(PREVIOUS/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
start=world.index('    // Read-only HUD selection.')
end=world.index('    protected void MovementLabLeaveAimForSprint()',start)
assert world[:start]+world[end:]==oldworld
for file in (PREVIOUS/'StartGateSource/Scripts').rglob('*.c'):
    if file.name not in ('MovementLabStartGate.c','MovementLabSpeedHUD.c'):
        assert file.read_bytes()==(SOURCE/'StartGateSource/Scripts'/file.relative_to(PREVIOUS/'StartGateSource/Scripts')).read_bytes()
assert (SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes()==(PREVIOUS/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes()
manifest=json.loads((SOURCE/'ImageSources/icon-map.json').read_text())
assert len(manifest['icons'])==24 and len({i['name'] for i in manifest['icons']})==24

getter=world[world.index('    void MovementLabGetHUDSpeed'):end]
getter=getter.replace('out int ','int& ').replace('out string ','std::string& ').replace('out bool ','bool& ')
getter=getter.replace('HumanMovementState hudState = new HumanMovementState();','HumanMovementState hudState;').replace('HumanMovementState iconState = new HumanMovementState();','HumanMovementState iconState;')
getter=getter.replace('Math.','Math::').replace('DayZPlayerConstants.','DayZPlayerConstants::').replace('MovementLabStartGate.','MovementLabStartGate::')
prefix='''#include <cassert>
#include <algorithm>
#include <string>
#include <iostream>
struct Math{static int Clamp(int x,int a,int b){return std::clamp(x,a,b);}};
struct DayZPlayerConstants{static const int STANCEIDX_CROUCH=1,STANCEIDX_RAISEDCROUCH=4;};
struct HumanMovementState{int m_iStanceIdx=0,m_iMovement=1;};
struct MovementLabStartGate{inline static bool NativeAimComparison=false;};
struct Probe{int stance=0,movement=1;bool raised=false;bool m_MovementLabAimSlowMode=false,m_MovementLabJogCrouchFade=false,m_MovementLabScrollSprint=false,m_MovementLabWalkMode=true;
int m_MovementLabAimCrouchLevel=4,m_MovementLabAimSlowLevel=1,m_MovementLabAimFastLevel=2,m_MovementLabCrouchLevel=4,m_MovementLabJogCrouchTarget=4,m_MovementLabWalkLevel=1,m_MovementLabJogLevel=2;
float m_MovementLabAimSprintTime=0;
bool IsRaised(){return raised;}void GetMovementState(HumanMovementState& x){x.m_iStanceIdx=stance;x.m_iMovement=movement;}
'''
tests='''};
int main(){Probe p;int icon,level;std::string mode;bool automatic;
 p.stance=1;for(int i=1;i<=5;i++){p.m_MovementLabCrouchLevel=i;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==i-1 && level==i && !automatic);}
 p.raised=true;for(int i=1;i<=4;i++){p.m_MovementLabAimCrouchLevel=i;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==i+4 && level==i && !automatic);}
 p.stance=0;p.m_MovementLabAimSlowMode=true;for(int i=1;i<=3;i++){p.m_MovementLabAimSlowLevel=i;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==(i==1?17:i==2?18:23) && level==i);}
 p.m_MovementLabAimSlowMode=false;for(int i=1;i<=3;i++){p.m_MovementLabAimFastLevel=i;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==i+18 && level==i);}
 p.m_MovementLabAimSprintTime=.5f;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==22 && automatic && level==2);
 p.m_MovementLabAimSprintTime=0;p.raised=false;p.stance=1;p.m_MovementLabJogCrouchFade=true;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==16 && automatic);
 p.m_MovementLabJogCrouchFade=false;p.movement=0;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==10 && level==0);p.stance=0;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==9 && level==0);
 p.movement=1;p.m_MovementLabWalkMode=true;for(int i=1;i<=2;i++){p.m_MovementLabWalkLevel=i;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==i+10 && level==i);}
 p.m_MovementLabWalkMode=false;for(int i=2;i<=3;i++){p.m_MovementLabJogLevel=i;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==i+11 && level==i-1);}
 p.m_MovementLabScrollSprint=true;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==15 && level==1);
 p.stance=2;p.MovementLabGetHUDIcon(icon,level,mode,automatic);assert(icon==-1 && mode=="PRONE");
 std::cout<<"Actual read-only accessor: all24 icons, selected vs idle, crouch/aim momentum, internal jog offsets and native prone fallback passed.\\n";}
'''

def run_cpp(code,label):
    with tempfile.TemporaryDirectory(prefix='movementlab-hud-icons-') as d:
        p=Path(d);(p/'test.cpp').write_text(code)
        subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
        subprocess.run([str(p/'test')],check=True)
run_cpp(prefix+getter+tests,'accessor')

hud=(SOURCE/'StartGateSource/Scripts/5_Mission/MovementLabSpeedHUD.c').read_text()
assert 'LoadImageFile' in hud and 'CUSTOMUV' in hud and 'SpeedCell' not in hud
s=hud.replace('modded class IngameHud','struct TestHUD:BaseHUD').replace('protected ','').replace('override ','')
for type in ('Widget','ImageWidget','TextWidget','PlayerBase'):
    s=re.sub(r'\b'+type+r' (\w+)',type+r'* \1',s)
s=s.replace('WidgetFlags iconFlags','int iconFlags').replace('string ','std::string ')
for name in ('ImageWidget','TextWidget','PlayerBase','WidgetFlags','Math','MovementLabStartGate'):
    s=s.replace(name+'.',name+'::')
s=s.replace('super.','BaseHUD::').replace('GetGame().','GetGame()->').replace('GetWorkspace().','GetWorkspace()->')
for name in ('hud_panel_widget','m_MovementLabSpeedRoot','m_MovementLabSpeedLabel','m_MovementLabSpeedImage','m_Presence','m_HudPanelWidget','speedPlayer','speedStance'):
    s=s.replace(name+'.',name+'->')
s=s.replace('speedLabel + " L" + speedLevel','speedLabel + " L" + std::to_string(speedLevel)')
s=re.sub(r'^\s*Print\([^\n]*\);','',s,flags=re.M)
s=re.sub(r'\bbool m_MovementLabSpeedReady;', 'bool m_MovementLabSpeedReady=false;',s)
s=re.sub(r'\b(Widget|ImageWidget|TextWidget)\* (m_\w+);',r'\1* \2=nullptr;',s).rstrip()+';'
mock=(ROOT/'tools/fixtures/movementlab_speed_hud_mock.cpp').read_text()
mock=mock.replace('static float Max(float a,float b)', 'static float Min(float a,float b){return std::min(a,b);}static float Max(float a,float b)')
mock=mock.replace('NOFOCUS=64;', 'NOFOCUS=64,CUSTOMUV=128,SOURCEALPHA=256,BLEND=512;')
mock=mock.replace('constexpr int FrameWidgetTypeID=1,TextWidgetTypeID=2;', 'constexpr int FrameWidgetTypeID=1,TextWidgetTypeID=2,ImageWidgetTypeID=3;')
mock=mock.replace('void SetName(', 'void SetPos(float a,float b){x=a;y=b;}void SetSize(float a,float b){w=a;h=b;}void SetName(')
at=mock.index('struct Workspace')
mock=mock[:at]+'''struct ImageWidget:Widget{bool failLoad=false,badSize=false,failSelect=false;int slot=0,loads=0,uvWrites=0;float uv[4][2]{};
static ImageWidget* Cast(Widget* w){return dynamic_cast<ImageWidget*>(w);}bool LoadImageFile(int n,std::string p){loads++;assert(n==0||n==1);assert(p.find(".paa")!=std::string::npos);return !failLoad;}void GetImageSize(int n,int& w,int& h){w=badSize?512:2048;h=n?2048:1024;}bool SetImage(int n){slot=n;return !failSelect;}void SetUV(float v[4][2]){uvWrites++;for(int i=0;i<4;i++)for(int j=0;j<2;j++)uv[i][j]=v[i][j];}};
'''+mock[at:]
mock=mock.replace('bool failText=false;', 'bool failText=false,failImage=false,failLoad=false,badSize=false;')
mock=mock.replace('if(failText&&type==TextWidgetTypeID)return nullptr;', 'if((failText&&type==TextWidgetTypeID)||(failImage&&type==ImageWidgetTypeID))return nullptr;')
mock=mock.replace('Widget* v=type==TextWidgetTypeID?new TextWidget:new Widget;', 'Widget* v=type==TextWidgetTypeID?new TextWidget:type==ImageWidgetTypeID?new ImageWidget:new Widget;if(auto image=ImageWidget::Cast(v)){image->failLoad=failLoad;image->badSize=badSize;}')
mock=mock.replace('int selected=1;', 'int selected=1,icon=11;')
mock=mock.replace('void MovementLabGetHUDSpeed(int& l,std::string& m,bool& a){l=selected;m=mode;a=automatic;}', 'void MovementLabGetHUDIcon(int& i,int& l,std::string& m,bool& a){i=icon;l=selected;m=mode;a=automatic;}')
uvs='float expected[24][4]={'+','.join('{'+','.join(str(v)+'f' for v in row['uv'])+'}' for row in manifest['icons'])+'};\n'
hudtests=r'''
int main(){Widget root,presence,stance;root.w=1920;root.h=1080;presence.name="PresencePanel";presence.x=80;presence.y=990;presence.w=54;presence.h=32;presence.parent=&root;stance.name="StancePanel";stance.x=300;stance.y=995;stance.w=32;stance.h=32;stance.parent=&root;root.children={&presence,&stance};PlayerBase p;game.player=&p;TestHUD hud;hud.Init(&root);assert(hud.m_MovementLabSpeedReady);int childCount=root.children.size();hud.Init(&root);assert(root.children.size()==childCount);auto image=hud.m_MovementLabSpeedImage;
 for(int i=0;i<24;i++){p.icon=i;hud.Update(.016f);assert(hud.m_MovementLabSpeedRoot->visible && image->slot==(i==23?1:0));assert(std::abs(image->uv[0][0]-expected[i][0])<1e-7f && std::abs(image->uv[0][1]-expected[i][1])<1e-7f && std::abs(image->uv[2][0]-expected[i][2])<1e-7f && std::abs(image->uv[2][1]-expected[i][3])<1e-7f);float textureH=i==23?2048:1024;float ratio=(expected[i][2]-expected[i][0])*2048/((expected[i][3]-expected[i][1])*textureH);assert(std::abs(image->w/image->h-ratio)<.0001f);assert(image->w<=(i==16||i==22?132.001f:88.001f) && image->h<=80.001f);}
 int loads=image->loads,writes=image->uvWrites;for(int i=0;i<100;i++)hud.Update(.016f);assert(image->loads==loads && image->uvWrites==writes);
 p.icon=22;p.mode="AIM FAST";p.selected=2;p.automatic=true;hud.Update(.016f);assert(hud.m_MovementLabSpeedLabel->text=="AIM FAST L2 AUTO" && hud.m_MovementLabSpeedLabel->color==ARGB(255,235,193,100));
 p.icon=-1;hud.Update(.016f);assert(!hud.m_MovementLabSpeedRoot->visible);p.icon=11;presence.visible=false;hud.Update(.016f);assert(!hud.m_MovementLabSpeedRoot->visible);presence.visible=true;p.alive=false;hud.Update(.016f);assert(!hud.m_MovementLabSpeedRoot->visible);p.alive=true;MovementLabStartGate::Enabled=false;hud.Update(.016f);assert(!hud.m_MovementLabSpeedRoot->visible);MovementLabStartGate::Enabled=true;
 root.w=640;root.h=360;hud.Update(.016f);assert(hud.m_MovementLabSpeedRoot->x<=508 && hud.m_MovementLabSpeedRoot->y<=256);
 for(int fault=0;fault<4;fault++){Widget failedRoot;failedRoot.children={&presence};game.workspace={};game.workspace.failText=fault==0;game.workspace.failImage=fault==1;game.workspace.failLoad=fault==2;game.workspace.badSize=fault==3;TestHUD failed;failed.Init(&failedRoot);failed.Update(.016f);assert(!failed.m_MovementLabSpeedReady && !failed.m_MovementLabSpeedRoot->visible);}
 std::cout<<"Actual image HUD:24 UV regions/two textures, cached updates, momentum aspect/label, HUD/death/mod hiding, bounds, reinit and load failure guards passed. Native rendering pending.\n";}
'''
run_cpp(mock+s+uvs+hudtests,'HUD')
print('Movement/mission code preserved; only a read-only accessor and image HUD changed.')
