from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
s=(r/'hud-icons-test/MovementLabLocomotion_v94/StartGateSource/Scripts/4_World/MovementLabZombieRagdoll.c').read_text()
methods=s[s.index('    void Update()'):s.rindex('}')]
methods=methods.replace('GetGame().','GetGame()->').replace('m_Driver.','m_Driver->').replace('m_Visual.','m_Visual->').replace('= null;','= nullptr;')
code=r'''
#include <cassert>
#include <cmath>
#include <vector>
#include <string>
struct vector {float v[3]={0,0,0};float& operator[](int i){return v[i];}float Length(){return std::sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);}vector operator*(float x){return {{v[0]*x,v[1]*x,v[2]*x}};}};
struct Body {bool ragdoll=false,disabled=false,deleted=false;int layer=63,sets=0,boneReads=0,impulses=0;std::vector<int> targetBones;bool PhysicsIsRagdoll(){return ragdoll;}void DisableSimulation(bool v){disabled=v;}void GetTransform(vector (&out)[4]){out[3]={{100,2,50}};}void SetTransform(vector (&out)[4]){assert(out[3][0]==100&&out[3][2]==50);sets++;}void GetBoneTransformMS(int bone,vector (&out)[4]){out[3]={{float(bone),float(bone*2),float(bone*3)}};boneReads++;}};
using PlayerBase=Body;using ZombieBase=Body;
struct Indices {std::vector<int> a;int Count(){return a.size();}int operator[](int i){return a[i];}};
struct Game {int now=0,deletes=0;int GetTime(){return now;}void ObjectDelete(Body* b){assert(!b->deleted);b->deleted=true;deletes++;}} game;
Game* GetGame(){return &game;}void Print(std::string){}
int dBodyGetInteractionLayer(Body* b){return b->layer;}void dBodySetInteractionLayer(Body* b,int v){b->layer=v;}void dBodyApplyImpulse(Body* b,vector){b->impulses++;}
void SetBoneGlobal(Body* b,int index,vector (&pose)[4]){assert((index==12&&pose[3][0]==3)||(index==25&&pose[3][0]==7));b->targetBones.push_back(index);}
struct Driver {
 PlayerBase* m_Driver=nullptr;ZombieBase* m_Visual=nullptr;
 Indices m_SourceBones{{3,7}},m_TargetBones{{12,25}};int m_OriginalLayer=0,m_ActivationDeadline=500;bool m_VisualSuspended=false;vector m_InitialVelocity={{1,0,0}};
 METHODS
};
int main(){
 Body human,visual;Driver d;d.m_Driver=&human;d.m_Visual=&visual;
 d.Update();assert(!visual.disabled&&visual.layer==63&&visual.sets==0&&game.deletes==0);
 game.now=499;d.Update();assert(visual.sets==0);
 human.ragdoll=true;d.Update();assert(visual.disabled&&visual.layer==0&&visual.sets==1&&human.impulses==1&&visual.targetBones.size()==2);
 d.Update();assert(human.impulses==1&&visual.sets==2&&visual.targetBones.size()==4);
 d.Stop();assert(!visual.disabled&&visual.layer==63&&human.deleted&&d.m_Driver==nullptr&&d.m_Visual==nullptr&&game.deletes==1);
 d.Stop();assert(game.deletes==1);
 Body failed,untouched;Driver f;f.m_Driver=&failed;f.m_Visual=&untouched;game.now=500;f.Update();assert(failed.deleted&&!untouched.disabled&&untouched.layer==63&&untouched.sets==0&&game.deletes==2);
 f.Update();assert(game.deletes==2);
 Driver missing;missing.Update();missing.Stop();assert(game.deletes==2);
}
'''.replace('METHODS',methods)
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Actual Update/Stop methods passed mocks: delayed activation, bone/root transfer, one-shot momentum, timeout fallback, layer/simulation restoration and idempotent driver cleanup. Native bone/ragdoll behaviour UNVERIFIED.')
