from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'hud-icons-test/MovementLabLocomotion_v104/StartGateSource/Scripts'
s=(BASE/'4_World/MovementLabConfiguredCorpse.c').read_text()
methods=s[s.index('    protected void Visibility'):s.rindex('}')]
methods='\n'.join(l for l in methods.splitlines() if 'Print(' not in l)
methods=methods.replace('vector travel =','[[maybe_unused]] vector travel =')
methods=methods.replace('MovementLabHermitPhysicsCorpse configured =', 'Body* configured =').replace('configured.', 'configured->').replace('vector.Distance(', 'vector::Distance(')
methods=methods.replace('protected void','void').replace('GetGame().','GetGame()->').replace('= null;','= nullptr;').replace('null,','nullptr,').replace('EntityFlags.','EntityFlags::').replace('ActiveState.','ActiveState::').replace('MovementLabHermitPhysicsCorpse.Cast(','MovementLabHermitPhysicsCorpse::Cast(')
for name in ['body','original','m_Corpse','m_Original','selections']:
 methods=methods.replace(name+'.',name+'->')
methods=methods.replace('Visibility(EntityAI body','Visibility(Body* body').replace('Start(ZombieBase original','Start(Body* original')
slot=(BASE/'4_World/MovementLabRangeInfected.c').read_text()
slot=slot[slot.index('class MovementLabInfectedSlot'):slot.index('modded class ZombieBase')]
slot=slot.replace('class MovementLabInfectedSlot','struct MovementLabInfectedSlot')
slot=slot.replace('ref MovementLabConfiguredCorpse Corpse;','void* Corpse;').replace('Body.','Body->')+';'
capture=(BASE/'4_World/MovementLabRangeInfected.c').read_text()
capture=capture[capture.index('            vector velocity = "0 0 0";'):capture.index('            m_MovementLabInfectedSlot.DeathCrawling')]
capture='\n'.join(line for line in capture.splitlines() if 'string source =' not in line and 'source =' not in line)
capture=capture.replace('vector velocity = "0 0 0";', 'vector velocity;').replace('m_MovementLabInfectedSlot.', 'slot->')
code=r'''
#include <cassert>
#include <cmath>
#include <string>
#include <algorithm>
struct vector{float v[3]={0,0,0};float& operator[](int i){return v[i];}static float Distance(vector a,vector b){return (a-b).Length();}float Length(){return std::sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);}vector operator-(vector b){return {{v[0]-b[0],v[1]-b[1],v[2]-b[2]}};}vector operator*(float x){return {{v[0]*x,v[1]*x,v[2]*x}};}vector& operator=(const char*){v[0]=v[1]=v[2]=0;return *this;}};
struct string:std::string{using std::string::string;string(const std::string& x):std::string(x){}void ToLower(){std::transform(begin(),end(),begin(),[](unsigned char c){return std::tolower(c);});}int IndexOf(const char* s){auto p=find(s);return p==npos?-1:int(p);}};
struct Selections{int Count(){return 1;}}selections;using TStringArray=Selections*;
struct EntityFlags{enum{VISIBLE=1};};struct ActiveState{enum{ACTIVE=1};};
struct Body{bool alive=true,ragdoll=false,allowRagdoll=true,visible=false,disabled=false,deleted=false,correctClass=true,ready=true,damage=true,crawl=false,raised=false,poseBlocked=false;int layer=63,mask=0,impulses=0,positions=0;float mass=80,proneHead=.35f,pronePelvis=.2f;string shape="hermit_above0.p3d";vector velocity,impulse,position;
 bool IsAlive(){return alive;}vector GetPosition(){return position;}void SetPosition(vector v){position=v;positions++;}void SetOrientation(vector){}TStringArray GetHiddenSelections(){return &selections;}string GetObjectTexture(int){return "texture";}string GetObjectMaterial(int){return "material";}void SetObjectTexture(int,string){}void SetObjectMaterial(int,string){}void SetAllowDamage(bool b){damage=b;}
 void SetHealth(string,string,int){alive=false;}void DisableSimulation(bool v){disabled=v;}void PhysicsSetRagdoll(bool v){ragdoll=v&&allowRagdoll;}bool PhysicsIsRagdoll(){return ragdoll;}string GetShapeName(){return shape;}void SetCameraMask(int v){mask=v;}void SetInvisible(bool){}void SetFlags(int,bool){visible=true;}void ClearFlags(int,bool){visible=false;}
 vector GetBonePositionWS(int index){return GetBonePositionMS(index);}void MovementLabSetCorpseVisible(bool v){visible=v;mask=v?-1:0;}bool MovementLabInPronePose(){return crawl;}void MovementLabPrimeDeathPose(bool c,bool r,float){if(!poseBlocked){crawl=c;raised=r;}}void MovementLabReleaseDeathPoseInput(){}int GetBoneIndexByName(string s){if(s=="Head")return 1;if(s=="Pelvis")return 2;return 3;}vector GetBonePositionMS(int index){if(!ready)return vector{};if(crawl)return vector{{0,index==1?proneHead:pronePelvis,0}};return vector{{0,index==1?1.62f:(index==2?1.f:(raised?1.4f:.7f)),0}};}static Body* Cast(Body* b){return b&&b->correctClass?b:nullptr;}
};
using Object=Body*;using MovementLabHermitPhysicsCorpse=Body;using ZombieBase=Body*;
struct Game{int now=0,created=0,deletes=0;bool multiplayer=false,failCreate=false,allowRagdoll=true;Body* next=nullptr;bool IsMultiplayer(){return multiplayer;}int GetTime(){return now;}Object CreatePlayer(void*,string,vector,int,string){created++;if(failCreate)return nullptr;next->allowRagdoll=allowRagdoll;return next;}void ObjectDelete(Body* b){assert(!b->deleted);b->deleted=true;deletes++;}}game;
Game* GetGame(){return &game;}int dBodyGetInteractionLayer(Body* b){return b->layer;}void dBodySetInteractionLayer(Body* b,int n){b->layer=n;}
vector GetVelocity(Body* b){return b->velocity;}float dBodyGetMass(Body* b){return b->mass;}void dBodyActive(Body*,int){}void dBodyApplyImpulse(Body* b,vector impulse){b->impulses++;b->impulse=impulse;}
struct Test{Body* m_Corpse=nullptr;Body* m_Original=nullptr;bool m_Replaced=false,m_Activated=false,m_OriginalSuspended=false,m_DeathCrawling=false,m_DeathArmsRaised=false;float m_DeathGait=0;int m_Deadline=0,m_OldLayer=0,m_CorpseLayer=0,m_CreatedAt=0,m_RevealedAt=0,m_TraceStage=0,m_ProneStableAt=-1;vector m_DeathPosition,m_DeathVelocity,m_RevealPelvis,m_SeedLeftHand,m_SeedRightHand,m_ProneStableHead,m_ProneStablePelvis;
METHODS
};
SLOT
vector Select(MovementLabInfectedSlot* slot,vector nativeVelocity,int now){CAPTURE
return velocity;}
void Reset(Body& o,Body& c){game=Game();o=Body();o.alive=false;c=Body();o.visible=true;o.mask=-1;game.next=&c;}
int main(){
 vector v={{3,0,4}},zero;Body original,corpse;Reset(original,corpse);Test t;assert(t.Start(&original,zero,zero,v,false,false,2,false));t.Update();assert(corpse.alive&&!corpse.ragdoll&&original.visible&&corpse.layer==0&&corpse.impulses==0);game.now=116;t.Update();assert(!corpse.alive&&corpse.ragdoll&&corpse.visible&&original.disabled&&original.layer==0);assert(corpse.impulses==1&&corpse.impulse[0]==240&&corpse.impulse[1]==0&&corpse.impulse[2]==320);assert(corpse.positions==1);t.Update();assert(corpse.impulses==1&&corpse.positions==1);t.Stop();assert(corpse.deleted&&original.visible&&!original.disabled&&original.layer==63);t.Stop();assert(game.deletes==1);
 Reset(original,corpse);corpse.ready=false;Test warm;assert(warm.Start(&original,zero,zero,v,false,false,2,false));game.now=999;warm.Update();assert(corpse.alive&&original.visible&&!original.disabled);game.now=1000;warm.Update();assert(corpse.deleted&&original.visible&&!original.disabled&&corpse.impulses==0);
 Reset(original,corpse);game.allowRagdoll=false;Test timeout;assert(timeout.Start(&original,zero,zero,v,false,false,2,false));game.now=116;timeout.Update();assert(original.disabled&&!original.visible&&!corpse.visible);game.now=616;timeout.Update();assert(corpse.deleted&&original.visible&&!original.disabled&&original.layer==63);
 Reset(original,corpse);corpse.shape="m_denis_2.p3d";Test bad;assert(bad.Start(&original,zero,zero,v,false,false,2,false));bad.Update();assert(corpse.deleted&&original.visible&&corpse.impulses==0);
 Reset(original,corpse);corpse.mass=0;Test stationary;assert(stationary.Start(&original,zero,zero,zero,false,false,0,false));game.now=116;stationary.Update();assert(corpse.impulses==1&&corpse.impulse.Length()==0);
 Reset(original,corpse);corpse.velocity={{1,-.326843f,0}};Test delta;assert(delta.Start(&original,zero,zero,v,false,false,2,false));game.now=116;delta.Update();assert(corpse.impulse[0]==160&&corpse.impulse[1]==0&&corpse.impulse[2]==320);
 Reset(original,corpse);Test crawl;assert(crawl.Start(&original,zero,zero,v,true,false,1,false));game.now=116;crawl.Update();assert(!corpse.ragdoll&&!corpse.visible);game.now=232;crawl.Update();assert(corpse.crawl&&corpse.ragdoll&&corpse.visible&&corpse.GetBonePositionMS(1)[1]<.8f);
 Reset(original,corpse);corpse.poseBlocked=true;Test noStandingFallback;assert(noStandingFallback.Start(&original,zero,zero,v,true,false,1,false));game.now=2000;noStandingFallback.Update();assert(corpse.deleted&&original.visible&&!original.disabled&&corpse.impulses==0);
 Reset(original,corpse);Test raised;assert(raised.Start(&original,zero,zero,v,false,true,2,false));game.now=116;raised.Update();assert(corpse.raised&&corpse.ragdoll&&corpse.visible&&corpse.GetBonePositionMS(3)[1]>1.12f);
 Reset(original,corpse);corpse.poseBlocked=true;Test noDroppedArms;assert(noDroppedArms.Start(&original,zero,zero,v,false,true,2,false));game.now=1000;noDroppedArms.Update();assert(corpse.deleted&&original.visible&&!original.disabled);
 Reset(original,corpse);corpse.proneHead=.59f;corpse.pronePelvis=.537f;Test midTransition;assert(midTransition.Start(&original,zero,zero,v,true,false,1,false));game.now=116;midTransition.Update();assert(!corpse.ragdoll&&!corpse.visible);corpse.proneHead=.35f;corpse.pronePelvis=.2f;game.now=300;midTransition.Update();assert(!corpse.ragdoll);game.now=350;midTransition.Update();assert(!corpse.ragdoll);game.now=401;midTransition.Update();assert(corpse.ragdoll&&corpse.visible);
 Reset(original,corpse);original.disabled=true;game.failCreate=true;Test frozenFailure;assert(!frozenFailure.Start(&original,zero,zero,v,true,false,1,true));frozenFailure.Stop();assert(!original.disabled&&original.visible);
 MovementLabInfectedSlot selected{};selected.VelocityAt=1000;selected.LastVelocity={{3,0,4}};assert(Select(&selected,vector{{0,0,.215f}},1017).Length()==5);selected.LastVelocity=zero;assert(Select(&selected,v,1017).Length()==0);assert(Select(&selected,v,1200).Length()==5);assert(Select(&selected,vector{{21,0,0}},1200).Length()==0);
 Body moving;MovementLabInfectedSlot slot{};slot.Body=&moving;slot.SampleMotion(1000);moving.position={{.24f,0,.32f}};slot.SampleMotion(1080);assert(std::abs(slot.LastVelocity[0]-3)<.001&&std::abs(slot.LastVelocity[2]-4)<.001);slot.SampleMotion(1160);assert(slot.LastVelocity.Length()==0);moving.position={{100,0,100}};slot.SampleMotion(1240);assert(slot.VelocityAt==0&&slot.LastVelocity.Length()==0);
}
'''.replace('METHODS',methods).replace('SLOT',slot).replace('CAPTURE',capture)
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Actual adapted helper/sample methods passed: warmup, one-shot mass-scaled delta-v, stationary/no lift, cleanup/rollback, sampling stop and teleport rejection. Native physics propagation unverified.')
