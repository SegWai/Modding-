from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'hud-icons-test/MovementLabLocomotion_v100/StartGateSource/Scripts/4_World/MovementLabConfiguredCorpse.c').read_text()
methods=source[source.index('    protected void Visibility'):source.rindex('}')]
methods=methods.replace('null,','nullptr,').replace('MovementLabHermitPhysicsCorpse.Cast(', 'MovementLabHermitPhysicsCorpse::Cast(')
methods=methods.replace('protected void','void').replace('GetGame().','GetGame()->').replace('= null;','= nullptr;').replace('EntityFlags.','EntityFlags::')
methods='\n'.join(l for l in methods.splitlines() if 'Print(' not in l)
for name in ['body','original','m_Corpse','m_Original','selections']:
 methods=methods.replace(name+'.',name+'->')
methods=methods.replace('original->GetHiddenSelections()', 'original->GetHiddenSelections()')
# Enforce native entity variables are handles; C++ uses explicit pointer types.
methods=methods.replace('Visibility(EntityAI body','Visibility(Body* body').replace('Start(ZombieBase corpse','Start(Body* corpse').replace('Start(ZombieBase original','Start(Body* original')
code=r'''
#include <cassert>
#include <string>
#include <vector>
#include <algorithm>
struct string:std::string {using std::string::string;string(const std::string& x):std::string(x){} void ToLower(){std::transform(begin(),end(),begin(),[](unsigned char c){return std::tolower(c);});}int IndexOf(const char* s){auto p=find(s);return p==npos?-1:int(p);}};
struct Selections{int Count(){return 1;}} selections;
using TStringArray=Selections*;
struct EntityFlags{enum{VISIBLE=1};};
struct Body{bool alive=false,ragdoll=false,allowRagdoll=true,visible=false,disabled=false,deleted=false,correctClass=true;int layer=63,mask=0;string shape="hermit_above0.p3d";
 bool IsAlive(){return alive;}int GetPosition(){return 1;}int GetOrientation(){return 2;}void SetOrientation(int){}TStringArray GetHiddenSelections(){return &selections;}string GetObjectTexture(int){return "texture";}string GetObjectMaterial(int){return "material";}void SetObjectTexture(int,string){}void SetObjectMaterial(int,string){}
 void SetHealth(string,string,int){alive=false;}void DisableSimulation(bool v){disabled=v;}void PhysicsSetRagdoll(bool v){ragdoll=v&&allowRagdoll;}bool PhysicsIsRagdoll(){return ragdoll;}string GetShapeName(){return shape;}void SetCameraMask(int v){mask=v;}void SetInvisible(bool){}void SetFlags(int,bool){visible=true;}void ClearFlags(int,bool){visible=false;}
 static Body* Cast(Body* b){return b&&b->correctClass?b:nullptr;}
};
using Object=Body*;using MovementLabHermitPhysicsCorpse=Body;
struct Game{int now=0,created=0,deletes=0;bool multiplayer=false,failCreate=false,allowRagdoll=true;Body* next=nullptr;bool IsMultiplayer(){return multiplayer;}int GetTime(){return now;}Object CreatePlayer(void*,string,int,int,string){created++;if(failCreate)return nullptr;next->allowRagdoll=allowRagdoll;return next;}void ObjectDelete(Body* b){assert(!b->deleted);b->deleted=true;deletes++;}}game;
Game* GetGame(){return &game;}
int dBodyGetInteractionLayer(Body* b){return b->layer;}void dBodySetInteractionLayer(Body* b,int n){b->layer=n;}
struct Test{Body* m_Corpse=nullptr;Body* m_Original=nullptr;bool m_Replaced=false;int m_Deadline=0,m_OldLayer=0;
METHODS
};
void Reset(Body& original,Body& corpse){game=Game();original=Body();corpse=Body();original.visible=true;original.mask=-1;game.next=&corpse;}
int main(){
 Body original,corpse;Reset(original,corpse);Test t;
 assert(t.Start(&original));assert(game.created==1&&original.visible&&!original.disabled&&!corpse.visible&&corpse.ragdoll);
 t.Update();assert(!original.visible&&original.disabled&&original.layer==0&&corpse.visible&&corpse.mask==-1);
 t.Update();assert(game.created==1&&game.deletes==0);t.Stop();assert(corpse.deleted&&original.visible&&!original.disabled&&original.layer==63&&game.deletes==1);t.Stop();assert(game.deletes==1);
 Reset(original,corpse);corpse.shape="m_denis_2.p3d";Test badMesh;assert(badMesh.Start(&original));badMesh.Update();assert(corpse.deleted&&original.visible&&!original.disabled&&game.deletes==1);badMesh.Update();badMesh.Stop();assert(game.deletes==1);
 Reset(original,corpse);game.allowRagdoll=false;Test timeout;assert(timeout.Start(&original));game.now=499;timeout.Update();assert(!corpse.deleted&&original.visible&&!original.disabled);game.now=500;timeout.Update();assert(corpse.deleted&&original.visible&&!original.disabled);
 Reset(original,corpse);game.failCreate=true;Test missing;assert(!missing.Start(&original));missing.Stop();assert(game.deletes==0&&original.visible);
 Reset(original,corpse);corpse.correctClass=false;Test badClass;assert(!badClass.Start(&original));badClass.Stop();assert(game.deletes==1&&original.visible);
 Reset(original,corpse);original.alive=true;Test living;assert(!living.Start(&original));assert(game.created==0);
 Reset(original,corpse);game.multiplayer=true;Test multi;assert(!multi.Start(&original));assert(game.created==0);
}
'''.replace('METHODS',methods)
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Actual helper lifecycle passed adapted C++ mocks: success, repeated cleanup, wrong mesh, timeout, null/wrong class, living and multiplayer guards. Does not verify native model/physics behavior.')
