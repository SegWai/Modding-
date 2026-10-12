from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1];s=(root/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision18/Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text();a=s.index('    protected void MovementLabRemoveExtraRangeCharacters()');b=s.index('    protected void MovementLabSpawnRangeTarget',a);method=s[a:b].replace('protected ','').replace('array<Object> rangeObjects = new array<Object>();','std::vector<Object*> rangeObjects;').replace('array<CargoBase> rangeCargos = new array<CargoBase>();','std::vector<int> rangeCargos;').replace('foreach (Object rangeObject: rangeObjects)','for (auto rangeObject: rangeObjects)').replace('foreach (MovementLabRangeSlot retainedSlot: m_MovementLabRangeSlots)','for (auto retainedSlot: m_MovementLabRangeSlots)').replace('PlayerBase rangePerson','PlayerBase* rangePerson').replace('PlayerBase.Cast','PlayerBase::Cast').replace('retainedSlot.Character','retainedSlot->Character').replace('GetGame().','GetGame()->')
cpp='''#include <vector>
#include <cassert>
struct Object{bool deleted=false;virtual ~Object(){} };struct PlayerBase:Object{static PlayerBase* Cast(Object* o){return dynamic_cast<PlayerBase*>(o);}};struct MovementLabRangeSlot{PlayerBase* Character=nullptr;};
struct Game{bool multi=false;PlayerBase player;std::vector<Object*> objects;bool IsMultiplayer(){return multi;}PlayerBase* GetPlayer(){return &player;}void GetObjectsAtPosition3D(int,float,std::vector<Object*>& out,std::vector<int>&){out=objects;}void ObjectDelete(Object* o){o->deleted=true;}}game;Game* GetGame(){return &game;}
struct Range{int m_MovementLabRangeOrigin=0;std::vector<MovementLabRangeSlot*>m_MovementLabRangeSlots;
'''+method+'''};
int main(){Range range;game.objects.push_back(&game.player);Object prop;game.objects.push_back(&prop);PlayerBase people[25];for(auto& p:people)game.objects.push_back(&p);MovementLabRangeSlot slots[5];for(int i=0;i<5;i++){slots[i].Character=&people[i*5];range.m_MovementLabRangeSlots.push_back(&slots[i]);}range.MovementLabRemoveExtraRangeCharacters();int alive=0;for(auto& p:people)alive+=!p.deleted;assert(alive==5 && !game.player.deleted && !prop.deleted);game.multi=true;PlayerBase outsider;game.objects.push_back(&outsider);range.MovementLabRemoveExtraRangeCharacters();assert(!outsider.deleted);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
print('Actual range cleanup translated:25 people ->five assigned targets, player/props preserved, multiplayer cleanup disabled. Native object query pending.')
