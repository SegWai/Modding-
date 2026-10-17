from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];b=r/'hud-icons-test/MovementLabLocomotion_v92/StartGateSource/Scripts'
u=(b/'5_Mission/MovementLabInfectedRange.c').read_text();u=u[u.index('    void Update()'):u.index('    void Shutdown()')]
u=u.replace('GetGame().','GetGame()->').replace('MovementLabInfectedSlot slot','MovementLabInfectedSlot* slot').replace('slot.','slot->').replace('slot->Body.','slot->Body->').replace('= null;','= nullptr;')
k=(b/'4_World/MovementLabRangeInfected.c').read_text();k=k[k.index('    override void EEKilled('):k.index('    override bool HandleDeath(')]
k=k.replace('override void EEKilled(Object killer)','void EEKilled(void* killer)').replace('super.EEKilled(killer)','SuperEEKilled(killer)').replace('GetGame().','GetGame()->').replace('m_MovementLabInfectedSlot.','m_MovementLabInfectedSlot->').replace('DayZInfectedDeathAnims.','DayZInfectedDeathAnims::')
code=r'''
#include <cassert>
#include <vector>
#include <string>
void Print(std::string){}
struct Zombie;
struct MovementLabInfectedSlot {Zombie* Body=nullptr;std::string ClassName="test";int RespawnAt=0;bool DeathConfirmed=false,MissingLogged=false;};
struct Game {bool multi=false;int now=1000,deletes=0;bool IsMultiplayer(){return multi;}int GetTime(){return now;}void ObjectDelete(Zombie*); }game;
Game* GetGame(){return &game;}
struct DayZInfectedDeathAnims{enum{ANIM_DEATH_IMPULSE=1};};
struct Zombie {bool alive=true,m_MovementLabPhysicsDeathStarted=false;int id=0,nativeDeaths=0,m_DeathType=0,m_DamageHitDirection=0,m_MovementSpeed=0,m_MindState=0;MovementLabInfectedSlot* m_MovementLabInfectedSlot=nullptr;
 bool IsAlive(){return alive;}void SuperEEKilled(void*){alive=false;}void StartCommand_Death(int t,int){assert(t==1);nativeDeaths++;}void SetSynchDirty(){}std::string GetType(){return "Zombie";}
 KILLED
};
void Game::ObjectDelete(Zombie* b){deletes++;delete b;}
struct Slots {std::vector<MovementLabInfectedSlot*> a;int Count(){return a.size();}MovementLabInfectedSlot* operator[](int i){return a[i];}};
struct Range {Slots m_Slots;int spawns=0;
 Range(){for(int i=0;i<5;i++){auto* s=new MovementLabInfectedSlot;s->Body=new Zombie;s->Body->id=i+1;s->Body->m_MovementLabInfectedSlot=s;m_Slots.a.push_back(s);}}
 void SpawnOne(MovementLabInfectedSlot* s){assert(!s->Body);spawns++;s->Body=new Zombie;s->Body->id=100+spawns;s->Body->m_MovementLabInfectedSlot=s;s->DeathConfirmed=false;s->RespawnAt=0;}
 UPDATE
};
int main(){
 Range r;
 for(int time=1000;time<=30000;time+=1000){game.now=time;r.Update();assert(r.spawns==0&&game.deletes==0);}
 Zombie* lost=r.m_Slots[4]->Body;r.m_Slots[4]->Body=nullptr;game.now=40000;r.Update();game.now=50000;r.Update();assert(r.spawns==0&&r.m_Slots[4]->RespawnAt==0);r.m_Slots[4]->Body=lost;
 r.m_Slots[0]->Body->EEKilled(nullptr);assert(r.m_Slots[0]->DeathConfirmed&&r.m_Slots[0]->RespawnAt==55000&&r.m_Slots[0]->Body->nativeDeaths==1);
 game.now=51000;r.m_Slots[0]->Body->EEKilled(nullptr);assert(r.m_Slots[0]->RespawnAt==55000&&r.m_Slots[0]->Body->nativeDeaths==1);
 r.m_Slots[1]->Body->EEKilled(nullptr);assert(r.m_Slots[1]->RespawnAt==56000);
 game.now=54999;r.Update();assert(r.spawns==0);
 game.now=55000;r.Update();assert(r.spawns==1&&game.deletes==1&&r.m_Slots[0]->Body->IsAlive());assert(r.m_Slots[1]->RespawnAt==56000&&r.m_Slots[4]->Body->id==5);
 game.now=56000;r.Update();assert(r.spawns==2&&game.deletes==2);
 game.now=90000;r.Update();assert(r.spawns==2&&r.m_Slots.Count()==5);
 // Two more simultaneous deaths have their own deadlines and replacements.
 r.m_Slots[2]->Body->EEKilled(nullptr);r.m_Slots[3]->Body->EEKilled(nullptr);game.now=95000;r.Update();assert(r.spawns==4&&game.deletes==4&&r.m_Slots[4]->Body->id==5);
 Zombie untracked;untracked.EEKilled(nullptr);assert(untracked.nativeDeaths==0);
}
'''.replace('KILLED',k).replace('UPDATE',u)
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Actual death hook + manager Update passed mock checks: no periodic spawn, no null-reference spawn, one-shot native death command, independent deadlines, corpse replacement, living preservation and five-slot cap.')
