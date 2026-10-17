from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
s=(r/'hud-icons-test/MovementLabLocomotion_v95/StartGateSource/Scripts/4_World/MovementLabZombieRagdoll.c').read_text()
visibility=s[s.index('    void MovementLabZombieDriverVisibility'):s.index('    void MovementLabMakeZombiePhysicsDriver')].replace('EntityFlags.','EntityFlags::')
methods=s[s.index('    void Update()'):s.rindex('}')].replace('GetGame().','GetGame()->').replace('m_Driver.','m_Driver->').replace('m_Visual.','m_Visual->').replace('EntityFlags.','EntityFlags::').replace('= null;','= nullptr;')
code=r'''
#include <cassert>
#include <cmath>
#include <vector>
#include <string>
struct vector {float v[3]={0,0,0};float Length(){return std::sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);}vector operator*(float x){return {{v[0]*x,v[1]*x,v[2]*x}};}};
struct EntityFlags{enum {VISIBLE=1};};struct Body;std::vector<Body*> bodies;void CheckRendering();
using vobject=void*;
struct Body {bool ragdoll=false,disabled=false,deleted=false,visible=false,m_MovementLabZombieMeshRevealed=false;int layer=63,mask=0,impulses=0;vobject model=(void*)7;
 vobject GetVObject(){return model;}bool PhysicsIsRagdoll(){return ragdoll;}void DisableSimulation(bool v){disabled=v;}void SetInvisible(bool){}int SetCameraMask(int x){int old=mask;mask=x;CheckRendering();return old;}void SetFlags(int,bool){visible=true;CheckRendering();}void ClearFlags(int,bool){visible=false;CheckRendering();}
 VISIBILITY
};
void CheckRendering(){int visible=0;for(auto* b:bodies)if(!b->deleted&&b->visible&&b->mask!=0)visible++;assert(visible<=1);}
using PlayerBase=Body;using ZombieBase=Body;
struct Game {int now=0,deletes=0;int GetTime(){return now;}void ObjectDelete(Body* b){assert(!b->deleted);b->deleted=true;deletes++;CheckRendering();}}game;
Game* GetGame(){return &game;}void Print(std::string){}
int dBodyGetInteractionLayer(Body* b){return b->layer;}void dBodySetInteractionLayer(Body* b,int layer){b->layer=layer;}void dBodyApplyImpulse(Body* b,vector){b->impulses++;}
struct Driver {
 PlayerBase* m_Driver=nullptr;ZombieBase* m_Visual=nullptr;vobject m_ZombieModel=(void*)7;int m_OriginalLayer=0,m_ActivationDeadline=500;bool m_VisualSuspended=false;vector m_InitialVelocity={{1,0,0}};
 METHODS
};
void Setup(Body& human,Body& zombie,Driver& d){bodies={&human,&zombie};zombie.visible=true;zombie.mask=-1;d.m_Driver=&human;d.m_Visual=&zombie;CheckRendering();}
int main(){
 Body human,zombie;Driver d;Setup(human,zombie,d);
 d.Update();assert(!human.visible&&human.mask==0&&zombie.visible&&zombie.mask==-1&&!zombie.disabled);
 game.now=499;d.Update();assert(game.deletes==0);
 human.ragdoll=true;d.Update();assert(human.visible&&human.mask==-1&&!zombie.visible&&zombie.mask==0&&zombie.disabled&&zombie.layer==0&&human.impulses==1);
 // Simulate a native visibility reset on the hidden original; mask still blocks it.
 zombie.visible=true;d.Update();assert(!zombie.visible&&human.visible&&human.impulses==1);
 d.Stop();assert(human.deleted&&!human.visible&&human.mask==0&&zombie.visible&&zombie.mask==-1&&!zombie.disabled&&zombie.layer==63&&game.deletes==1);d.Stop();assert(game.deletes==1);
 Body failed,original;Driver f;Setup(failed,original,f);game.now=500;f.Update();assert(failed.deleted&&original.visible&&original.mask==-1&&!original.disabled&&game.deletes==2);
 Body changed,preserved;Driver c;Setup(changed,preserved,c);changed.model=(void*)1;game.now=0;c.Update();assert(changed.deleted&&!changed.visible&&preserved.visible&&game.deletes==3);
 Driver missing;missing.Update();missing.Stop();assert(game.deletes==3);
}
'''.replace('VISIBILITY',visibility).replace('METHODS',methods)
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Actual visibility/Update/Stop methods passed mocks: at-most-one rendered body at each render-state change, pending activation, takeover, reassertion, timeout, wrong-model fallback, one-shot momentum and cleanup. Native mesh binding UNVERIFIED.')
