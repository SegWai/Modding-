from pathlib import Path
import re,subprocess,tempfile
root=Path(__file__).resolve().parents[1];src=root/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision35';s=(src/'StartGateSource/Scripts/5_Mission/MovementLabSpeedHUD.c').read_text()
s=s.replace('modded class IngameHud','class TestHUD:public BaseHUD').replace('protected ','public: ').replace('override ','').replace('ref array<TextWidget> m_MovementLabSpeedCells = new array<TextWidget>()','std::vector<TextWidget*> m_MovementLabSpeedCells')
s=s.replace('Widget hud_panel_widget','Widget* hud_panel_widget').replace('Widget m_MovementLabSpeedRoot','Widget* m_MovementLabSpeedRoot').replace('TextWidget m_MovementLabSpeedLabel','TextWidget* m_MovementLabSpeedLabel').replace('TextWidget speedCell','TextWidget* speedCell').replace('TextWidget speedBar','TextWidget* speedBar').replace('PlayerBase speedPlayer','PlayerBase* speedPlayer').replace('Widget speedStance','Widget* speedStance').replace('WidgetFlags speedFlags','int speedFlags')
s=s.replace('foreach (TextWidget readyCell: m_MovementLabSpeedCells)','for(auto readyCell:m_MovementLabSpeedCells)').replace('string ','std::string ').replace('TextWidget.Cast','TextWidget::Cast').replace('PlayerBase.Cast','PlayerBase::Cast').replace('WidgetFlags.','WidgetFlags::').replace('Math.','Math::').replace('MovementLabStartGate.','MovementLabStartGate::').replace('super.','BaseHUD::')
s=s.replace('GetGame().','GetGame()->').replace('GetWorkspace().','GetWorkspace()->')
for name in ['hud_panel_widget','m_MovementLabSpeedRoot','m_MovementLabSpeedLabel','m_Presence','m_HudPanelWidget','speedCell','speedBar','speedPlayer','speedStance']:
 s=s.replace(name+'.',name+'->')
s=s.replace('readyCell.', 'readyCell->').replace('.Clear()', '.clear()').replace('.Insert(', '.push_back(').replace('.Count()', '.size()')
s=s.replace('"MovementLabSpeedCell" + speedCellIndex','"MovementLabSpeedCell" + std::to_string(speedCellIndex)').replace('speedMode + " " + speedLevel','speedMode + " " + std::to_string(speedLevel)')
s=re.sub(r'^\s*Print\([^\n]*\);','',s,flags=re.M);s=s.rstrip()+';'
# Native method signatures are checked separately; this executes the actual HUD control flow.
mock=(root/'tools/fixtures/movementlab_speed_hud_mock.cpp').read_text()
tests=r'''
int main(){
 Widget root,presence,stance;root.w=1920;root.h=1080;presence.name="PresencePanel";presence.x=80;presence.y=990;presence.w=54;presence.h=32;presence.parent=&root;stance.name="StancePanel";stance.x=300;stance.y=995;stance.w=32;stance.h=32;stance.parent=&root;root.children={&presence,&stance};PlayerBase player;game.player=&player;TestHUD hud;hud.Init(&root);assert(hud.m_MovementLabSpeedReady && hud.m_MovementLabSpeedCells.size()==5);int childCount=root.children.size();hud.Init(&root);assert(root.children.size()==childCount && hud.m_MovementLabSpeedCells.size()==5);
 for(int level=1;level<=5;level++){player.selected=level;player.automatic=false;hud.Update(.016);assert(hud.m_MovementLabSpeedRoot->visible && hud.m_MovementLabSpeedLabel->text=="WALK "+std::to_string(level));for(int i=0;i<5;i++)assert(hud.m_MovementLabSpeedCells[i]->color==ARGB(i<level?255:70,255,255,255));}
 assert(hud.m_MovementLabSpeedRoot->x==344 && hud.m_MovementLabSpeedRoot->y==990);player.automatic=true;player.selected=4;player.mode="CROUCH";hud.Update(.016);assert(hud.m_MovementLabSpeedLabel->text=="CROUCH 4 AUTO");assert(hud.m_MovementLabSpeedCells[0]->color==ARGB(255,235,193,100));presence.visible=false;hud.Update(.016);assert(!hud.m_MovementLabSpeedRoot->visible);presence.visible=true;player.alive=false;hud.Update(.016);assert(!hud.m_MovementLabSpeedRoot->visible);player.alive=true;MovementLabStartGate::Enabled=false;hud.Update(.016);assert(!hud.m_MovementLabSpeedRoot->visible);MovementLabStartGate::Enabled=true;root.w=640;root.h=360;hud.Update(.016);assert(hud.m_MovementLabSpeedRoot->x<=490 && hud.m_MovementLabSpeedRoot->y<=316);
 Widget failedRoot;failedRoot.children={&presence};game.workspace.failText=true;TestHUD failed;failed.Init(&failedRoot);failed.Update(.016);assert(!failed.m_MovementLabSpeedReady && !failed.m_MovementLabSpeedRoot->visible);
 std::cout<<"Actual HUD Init/Update:5 cells,selectedlevels1..5,AUTO,placement bounds,HUD/death/mod hiding,no duplicate roots and failed-widget guards passed. Native rendering pending.\n";
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(mock+s+tests);subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
config=(src/'StartGateSource/config.cpp').read_text();assert 'missionScriptModule' in config and 'MovementLabStartGate/Scripts/5_Mission' in config
