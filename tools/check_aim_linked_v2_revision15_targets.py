from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1];src=root/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision15'
s=(src/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text();a=s.index('    protected void MovementLabUpdateRangeTargets()');b=s.index('    // PlayerBase normally reapplies',a);method=s[a:b].replace('protected ','').replace('foreach (MovementLabRangeSlot targetSlot: m_MovementLabRangeSlots)','for (auto targetSlot: m_MovementLabRangeSlots)').replace('targetSlot.','targetSlot->').replace('GetGame().','GetGame()->').replace('Character.IsAlive()','Character->IsAlive()')
cpp='''#include <array>
#include <cassert>
struct Character{bool alive=true;bool IsAlive(){return alive;}};
struct MovementLabRangeSlot{Character* Character=nullptr;int RespawnAt=-1;int count=0;};
struct Game{int time=0;int deleted=0;int GetTime(){return time;}void ObjectDelete(Character* c){delete c;deleted++;}}game;Game* GetGame(){return &game;}
struct Range{std::array<MovementLabRangeSlot*,5>m_MovementLabRangeSlots;void MovementLabSpawnRangeTarget(MovementLabRangeSlot* slot){slot->Character=new Character();slot->RespawnAt=-1;slot->count++;}
'''.replace('Character* Character','struct Character* Character')+method+'''};
int main(){Range range;for(auto& slot:range.m_MovementLabRangeSlots){slot=new MovementLabRangeSlot();range.MovementLabSpawnRangeTarget(slot);}for(int cycle=0;cycle<20;cycle++){for(auto slot:range.m_MovementLabRangeSlots)slot->Character->alive=false;range.MovementLabUpdateRangeTargets();game.time+=2999;range.MovementLabUpdateRangeTargets();for(auto slot:range.m_MovementLabRangeSlots)assert(!slot->Character->alive);game.time++;range.MovementLabUpdateRangeTargets();for(auto slot:range.m_MovementLabRangeSlots)assert(slot->Character->alive && slot->count==cycle+2);}assert(game.deleted==100);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
assert 'rangeIndex * 10' in s and 'rangeIndex < 5' in s
print('Actual target scheduler translated: five targets, no early respawn at2999ms, respawn at3000ms,20 cycles/100 replacements. Native NPC spawn/idle/death pending.')
