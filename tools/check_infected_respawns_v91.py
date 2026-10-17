from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'hud-icons-test/MovementLabLocomotion_v91/StartGateSource/Scripts/5_Mission/MovementLabInfectedRange.c').read_text()
method=s[s.index('    void Update()'):s.index('    void Shutdown()')]
method=method.replace('GetGame().','GetGame()->').replace('MovementLabInfectedSlot slot','MovementLabInfectedSlot* slot').replace('slot.','slot->').replace('slot->Body.','slot->Body->')
code=r'''
#include <cassert>
#include <vector>
struct Zombie {bool alive=true;int id;bool IsAlive(){return alive;}};
struct MovementLabInfectedSlot {Zombie* Body;int RespawnAt=0;};
struct Slots {std::vector<MovementLabInfectedSlot*> a;int Count(){return a.size();}MovementLabInfectedSlot* operator[](int i){return a[i];}};
struct Game {bool multi=false;int now=1000,deletes=0;bool IsMultiplayer(){return multi;}int GetTime(){return now;}void ObjectDelete(Zombie* b){deletes++;delete b;}} game;
Game* GetGame(){return &game;}
struct Range {
 Slots m_Slots;int spawns=0;
 Range(){for(int i=0;i<5;i++)m_Slots.a.push_back(new MovementLabInfectedSlot{new Zombie{true,i+1},0});}
 void SpawnOne(MovementLabInfectedSlot* slot){spawns++;slot->Body=new Zombie{true,100+spawns};slot->RespawnAt=0;}
 METHOD
};
int main(){
 Range r;r.Update();assert(r.spawns==0);
 r.m_Slots[0]->Body->alive=false;r.Update();assert(r.m_Slots[0]->RespawnAt==6000);
 game.now=2500;r.m_Slots[1]->Body->alive=false;r.Update();assert(r.m_Slots[1]->RespawnAt==7500&&r.m_Slots[0]->RespawnAt==6000);
 game.now=5999;r.Update();assert(r.spawns==0);
 game.now=6000;r.Update();assert(r.spawns==1&&game.deletes==1&&r.m_Slots[0]->Body->IsAlive());assert(r.m_Slots[1]->RespawnAt==7500&&r.m_Slots[4]->Body->id==5);
 game.now=7500;r.Update();assert(r.spawns==2&&game.deletes==2);
 game.now=8000;r.m_Slots[2]->Body->alive=false;r.m_Slots[3]->Body->alive=false;r.Update();assert(r.m_Slots[2]->RespawnAt==13000&&r.m_Slots[3]->RespawnAt==13000);
 game.now=13000;r.Update();assert(r.spawns==4&&game.deletes==4&&r.m_Slots[4]->Body->id==5);
 r.Update();assert(r.spawns==4);
 delete r.m_Slots[0]->Body;r.m_Slots[0]->Body=nullptr;game.now=14000;r.Update();assert(r.m_Slots[0]->RespawnAt==19000);
 game.now=19000;r.Update();assert(r.spawns==5&&game.deletes==4);
 game.multi=true;r.m_Slots[4]->Body->alive=false;r.Update();assert(r.m_Slots[4]->RespawnAt==0&&r.spawns==5);
}
'''.replace('METHOD',method).replace('= null;','= nullptr;')
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Actual infected Update method passed mock tests: independent/staggered/simultaneous deadlines, living preservation, corpse deletion, missing body, no repeated respawns, multiplayer guard.')
