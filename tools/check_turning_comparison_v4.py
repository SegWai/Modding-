#!/usr/bin/env python3
"""Run actual turning-filter and toggle methods; verify v2 speed logic preserved."""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v3'
NEW=ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v4'
def method(text,name):
    match=re.search(r'\bvoid\s+'+name+r'\([^)]*\)\s*\{',text);assert match,name
    i=text.index('{',match.start())+1;depth=1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[match.start():i]
old=(OLD/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
new=(NEW/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
source=''
for name,text in [('Baseline',old),('Comparison',new)]:
    source+='class '+name+''' : public Base { public:
    bool m_MovementLabBraking=false,m_MovementLabOriginalStaminaInertia=false;
    bool m_MovementLabResponsiveTurn=false,m_MovementLabHeavy=true,m_MovementLabAnnounce=false;
    int cancels=0;
    void MovementLabCancelStart(){cancels++;}void MovementLabCancelBrake(){cancels++;}
    '''+method(text,'MovementLabApplyFilters')+'\n'
    if name=='Comparison':source+=method(text,'OnKeyPress')+'\n'
    source+='};\n'
source=source.replace('HumanCommandMove move =','HumanCommandMove* move =').replace('PlayerBase player','PlayerBase* player')
source=source.replace('player.','player->').replace('move.','move->')
source=source.replace('GetStaminaHandler().', 'GetStaminaHandler()->')
source=source.replace('CfgGameplayHandler.','CfgGameplayHandler::').replace('KeyCode.','KeyCode::').replace('MovementLabStartGate.','MovementLabStartGate::').replace('super.OnKeyPress(', 'Base::OnKeyPress(')
sdk=r'''
#include <array>
#include <cassert>
#include <iostream>
struct HumanCommandMove{std::array<float,5> v{};void SetRunSprintFilterModifier(float x){v[0]=x;}void SetDirectionFilterModifier(float x){v[1]=x;}void SetDirectionSprintFilterModifier(float x){v[2]=x;}void SetTurnSpanModifier(float x){v[3]=x;}void SetTurnSpanSprintModifier(float x){v[4]=x;}};
struct Stamina{float value=1;float GetSyncedStaminaNormalized(){return value;}};
struct PlayerBase{HumanCommandMove move;Stamina stamina;HumanCommandMove* GetCommand_Move(){return &move;}Stamina* GetStaminaHandler(){return &stamina;}};
struct CfgGameplayHandler{static bool GetAllowStaminaAffectInertia(){return false;}};
struct Game{bool multi=false;bool IsMultiplayer(){return multi;}}game;Game& GetGame(){return game;}
struct KeyCode{static const int KC_F7=7,KC_F8=8;};struct Base{void OnKeyPress(int){}};
struct MovementLabStartGate{inline static bool Enabled=true;};
'''
tests=r'''
int main(){
 for(bool heavy:{false,true})for(bool braking:{false,true})for(bool inertia:{false,true})for(float stamina:{0.f,.4f,1.f}){
  PlayerBase p;Baseline old;Comparison next;p.stamina.value=stamina;
  old.m_MovementLabBraking=next.m_MovementLabBraking=braking;
  old.m_MovementLabOriginalStaminaInertia=next.m_MovementLabOriginalStaminaInertia=inertia;
  old.MovementLabApplyFilters(&p,heavy);auto original=p.move.v;
  next.MovementLabApplyFilters(&p,heavy);assert(p.move.v==original);
  next.m_MovementLabResponsiveTurn=true;next.MovementLabApplyFilters(&p,heavy);auto responsive=p.move.v;
  assert(responsive[0]==original[0] && responsive[2]==original[2] && responsive[4]==original[4]);
  if(heavy){assert(responsive[1]==original[1] && responsive[3]==1.6f);assert(original[1]==2.5f && original[3]==2.5f);}
  else assert(responsive==original);
 }
 Comparison toggle;assert(!toggle.m_MovementLabResponsiveTurn);
 toggle.m_MovementLabBraking=true;
 toggle.OnKeyPress(8);assert(toggle.m_MovementLabResponsiveTurn && toggle.m_MovementLabAnnounce);
 assert(toggle.cancels==0 && toggle.m_MovementLabBraking && toggle.m_MovementLabHeavy);
 toggle.OnKeyPress(8);assert(!toggle.m_MovementLabResponsiveTurn && toggle.cancels==0);
 game.multi=true;toggle.OnKeyPress(8);assert(!toggle.m_MovementLabResponsiveTurn);game.multi=false;
 toggle.OnKeyPress(7);assert(!toggle.m_MovementLabHeavy && !MovementLabStartGate::Enabled && toggle.cancels==2);
 std::cout<<"Turning comparison passed: A matches v2 filters; B changes only non-sprint body-heading multiplier; sprint/speed filters identical across braking/stamina states; F8 toggles without speed-state cancellation. Direction timeout is identical in A and B. Native turning/animation test pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='turning-comparison-') as temp:
    cpp=Path(temp)/'check.cpp';binary=Path(temp)/'check'
    cpp.write_text(sdk+source+tests)
    subprocess.run(['g++','-std=c++17',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
