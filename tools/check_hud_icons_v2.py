"""Regression checks for individual-image HUD; no multidimensional native calls."""
from pathlib import Path
import re, json, subprocess, tempfile, struct
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'hud-icons-test/MovementLabHUDIcons_v2'
PREVIOUS=ROOT/'hud-icons-test/MovementLabHUDIcons_v1'
assert (SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_bytes()==(PREVIOUS/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_bytes()
assert (SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes()==(PREVIOUS/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes()
# Run the actual accessor tests and movement identity checks from v1 against v2.
base=(ROOT/'tools/check_hud_icons_v1.py').read_text().split('hud=(SOURCE/',1)[0]
base=base.replace("SOURCE=ROOT/'hud-icons-test/MovementLabHUDIcons_v1'", "SOURCE=ROOT/'hud-icons-test/MovementLabHUDIcons_v2'")
exec(compile(base,'unchanged-icon-accessor','exec'))
manifest=json.loads((SOURCE/'ImageSources/individual-textures.json').read_text())
assert len(manifest)==24
for entry in manifest:
    b=(SOURCE/'StartGateSource/GUI/Textures'/entry['file']).read_bytes()
    assert struct.unpack_from('<H',b)[0]==0xff05
    at=2; offsets=None
    while b[at:at+4]==b'GGAT':
        n=struct.unpack_from('<I',b,at+8)[0]
        if b[at+4:at+8]==b'SFFO':offsets=struct.unpack_from('<16I',b,at+12)
        at+=12+n
    assert offsets and struct.unpack_from('<HH',b,offsets[0])==tuple(entry['texture_size'])
    previous=None; count=0
    for offset in offsets:
        if not offset:break
        w,h=struct.unpack_from('<HH',b,offset)
        if not w:assert b[offset:offset+6]==b'\0'*6;break
        size=int.from_bytes(b[offset+4:offset+7],'little')
        assert size==w*h and offset+7+size<=len(b)
        if previous:assert (w,h)==(previous[0]//2,previous[1]//2)
        previous=(w,h);count+=1
    assert count==entry['mip_levels']
hud=(SOURCE/'StartGateSource/Scripts/5_Mission/MovementLabSpeedHUD.c').read_text()
assert not any(word in hud for word in ('SetUV','CUSTOMUV','float uv[','MovementLabSetIconUV'))
s=hud.replace('modded class IngameHud','struct TestHUD:BaseHUD').replace('protected ','').replace('override ','')
s=s.replace('ref array<ImageWidget> m_MovementLabSpeedImages = new array<ImageWidget>();','std::vector<ImageWidget*> m_MovementLabSpeedImages;')
for type in ('Widget','ImageWidget','TextWidget','PlayerBase'):
    s=re.sub(r'\b'+type+r' (\w+)',type+r'* \1',s)
s=s.replace('WidgetFlags iconFlags','int iconFlags').replace('string ','std::string ')
for name in ('ImageWidget','TextWidget','PlayerBase','WidgetFlags','Math','MovementLabStartGate'):
    s=s.replace(name+'.',name+'::')
s=s.replace('super.','BaseHUD::').replace('GetGame().','GetGame()->').replace('GetWorkspace().','GetWorkspace()->')
for name in ('hud_panel_widget','m_MovementLabSpeedRoot','m_MovementLabSpeedLabel','m_Presence','m_HudPanelWidget','speedPlayer','speedStance','speedImage'):
    s=s.replace(name+'.',name+'->')
s=s.replace('].Show(',']->Show(').replace('.Clear()','.clear()').replace('.Count()','.size()').replace('.Insert(','.push_back(')
s=s.replace('"MovementLabSpeedImage" + iconIndex','"MovementLabSpeedImage" + std::to_string(iconIndex)').replace('"" + iconIndex','std::to_string(iconIndex)').replace('speedLabel + " L" + speedLevel','speedLabel + " L" + std::to_string(speedLevel)')
s=re.sub(r'^\s*Print\([^\n]*\);','',s,flags=re.M)
s=re.sub(r'\bbool m_MovementLabSpeedReady;', 'bool m_MovementLabSpeedReady=false;',s)
s=re.sub(r'\b(Widget|TextWidget)\* (m_\w+);',r'\1* \2=nullptr;',s).rstrip()+';'
mock=(ROOT/'tools/fixtures/movementlab_speed_hud_mock.cpp').read_text()
mock=mock.replace('NOFOCUS=64;', 'NOFOCUS=64,STRETCH=128,SOURCEALPHA=256,BLEND=512;')
mock=mock.replace('constexpr int FrameWidgetTypeID=1,TextWidgetTypeID=2;', 'constexpr int FrameWidgetTypeID=1,TextWidgetTypeID=2,ImageWidgetTypeID=3;')
mock=mock.replace('void SetName(', 'void SetPos(float a,float b){x=a;y=b;}void SetSize(float a,float b){w=a;h=b;}void SetName(')
at=mock.index('struct Workspace')
mock=mock[:at]+'''struct ImageWidget:Widget{bool failLoad=false,badSize=false;int loads=0,index=-1;std::string file;
static ImageWidget* Cast(Widget* w){return dynamic_cast<ImageWidget*>(w);}bool LoadImageFile(int n,std::string p){assert(n==0);file=p;loads++;auto at=p.find("icon_");assert(at!=std::string::npos);index=std::stoi(p.substr(at+5,2));return !failLoad;}void GetImageSize(int n,int& w,int& h){assert(n==0);w=badSize?1:(index==16||index==22?512:256);h=256;}bool SetImage(int n){assert(n==0);return !failLoad;}};
'''+mock[at:]
mock=mock.replace('bool failText=false;', 'bool failText=false,failImage=false,failLoad=false,badSize=false;')
mock=mock.replace('if(failText&&type==TextWidgetTypeID)return nullptr;', 'if((failText&&type==TextWidgetTypeID)||(failImage&&type==ImageWidgetTypeID))return nullptr;')
mock=mock.replace('Widget* v=type==TextWidgetTypeID?new TextWidget:new Widget;', 'Widget* v=type==TextWidgetTypeID?new TextWidget:type==ImageWidgetTypeID?new ImageWidget:new Widget;if(auto image=ImageWidget::Cast(v)){image->failLoad=failLoad;image->badSize=badSize;}')
mock=mock.replace('int selected=1;', 'int selected=1,icon=11;')
mock=mock.replace('void MovementLabGetHUDSpeed(int& l,std::string& m,bool& a){l=selected;m=mode;a=automatic;}', 'void MovementLabGetHUDIcon(int& i,int& l,std::string& m,bool& a){i=icon;l=selected;m=mode;a=automatic;}')
tests=r'''
int main(){Widget root,presence,stance;root.w=1920;root.h=1080;presence.name="PresencePanel";presence.x=80;presence.y=990;presence.w=54;presence.h=32;presence.parent=&root;stance.name="StancePanel";stance.x=300;stance.y=995;stance.w=32;stance.h=32;stance.parent=&root;root.children={&presence,&stance};PlayerBase p;game.player=&p;TestHUD hud;hud.Init(&root);assert(hud.m_MovementLabSpeedReady && hud.m_MovementLabSpeedImages.size()==24);auto count=hud.m_MovementLabSpeedRoot->children.size();hud.Init(&root);assert(count==hud.m_MovementLabSpeedRoot->children.size());
 for(int i=0;i<24;i++){p.icon=i;hud.Update(.016f);assert(hud.m_MovementLabSpeedRoot->visible);for(int j=0;j<24;j++){auto img=hud.m_MovementLabSpeedImages[j];assert(img->visible==(i==j));assert(img->index==j && img->loads==2);assert(img->w==(j==16||j==22?132:80));}}
 for(int i=0;i<100;i++)hud.Update(.016f);for(auto img:hud.m_MovementLabSpeedImages)assert(img->loads==2);
 p.icon=22;p.mode="AIM FAST";p.selected=2;p.automatic=true;hud.Update(.016f);assert(hud.m_MovementLabSpeedLabel->text=="AIM FAST L2 AUTO" && hud.m_MovementLabSpeedLabel->color==ARGB(255,235,193,100));
 p.icon=-1;hud.Update(.016f);assert(!hud.m_MovementLabSpeedRoot->visible);p.icon=11;presence.visible=false;hud.Update(.016f);assert(!hud.m_MovementLabSpeedRoot->visible);presence.visible=true;p.alive=false;hud.Update(.016f);assert(!hud.m_MovementLabSpeedRoot->visible);p.alive=true;MovementLabStartGate::Enabled=false;hud.Update(.016f);assert(!hud.m_MovementLabSpeedRoot->visible);MovementLabStartGate::Enabled=true;
 root.w=640;root.h=360;hud.Update(.016f);assert(hud.m_MovementLabSpeedRoot->x<=508 && hud.m_MovementLabSpeedRoot->y<=256);
 for(int fault=0;fault<4;fault++){Widget failedRoot;failedRoot.children={&presence};game.workspace={};game.workspace.failText=fault==0;game.workspace.failImage=fault==1;game.workspace.failLoad=fault==2;game.workspace.badSize=fault==3;TestHUD failed;failed.Init(&failedRoot);failed.Update(.016f);assert(!failed.m_MovementLabSpeedReady && !failed.m_MovementLabSpeedRoot->visible);}
 std::cout<<"Actual v2 HUD:24 preloaded resources, one visible icon, zero scroll-time loads, reinit, AUTO, hiding, bounds and failure guards passed. No UV API exists in this code. Native compile/render still pending.\n";}
'''
run_cpp(mock+s+tests,'HUD')
print('All24 PAA mip chains verified; world and mission bytes unchanged from v1.')
