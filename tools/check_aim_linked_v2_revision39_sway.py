"""Exercise new sway hooks through the SDK's actual ProcessAimFilters body.
Native rendering/animation engine is not emulated by these checks.
"""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision39'
SDK=Path('/tmp/dayz-script-diff/scripts')
s=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabWeaponSway.c').read_text()
native=(SDK/'4_world/entities/dayzplayerimplementaiming.c').read_text()
def method(text,name):
 start=re.search(r'(?:override\s+)?(?:protected\s+)?(?:static\s+)?(?:bool|void)\s+'+name+r'\s*\(',text).start()
 begin=text.index('{',start);depth=1;i=begin+1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[start:i]
def cpp(text,base=None):
 text=text.replace('override ','').replace('protected ','').replace('out float ', 'float& ').replace('out DayZPlayerCameraResult ', 'DayZPlayerCameraResult& ')
 text=text.replace('PlayerBase player','PlayerBase* player').replace('EntityAI held','EntityAI* held').replace('SDayZPlayerAimingModel pModel','SDayZPlayerAimingModel* pModel').replace('PlayerBase.Cast(m_pPlayer)','m_pPlayer')
 text=text.replace('MovementLabWeaponSway.','MovementLabWeaponSway::').replace('MovementLabStartGate.','MovementLabStartGate::').replace('Math.','Math::').replace('DayZPlayerConstants.','DayZPlayerConstants::').replace('PlayerSwayConstants.','PlayerSwayConstants::').replace('EStaminaModifiers.','EStaminaModifiers::').replace('DayZPlayerUtils.','DayZPlayerUtils::')
 for p in ('player','held','GetGame()','m_PlayerPb','m_PlayerDpi','m_CurrentRecoil','m_KuruShake','pModel','GetStaminaHandler()'):
  text=text.replace(p+'.',p+'->')
 if base:text=text.replace('super.',base+'::')
 text=re.sub(r'float (\w+);',r'float \1=0;',text)
 return text
# Check native override parameter names/types, avoiding Enforce prototype mismatch.
for name in ('ApplyBreathingPattern','ApplyHorizontalNoise'):
 ours=method(s,name).split('{')[0].replace('override ','').split(name)[1]
 theirs=method(native,name).split('{')[0].split(name)[1]
 assert re.sub(r'\s+','',ours)==re.sub(r'\s+','',theirs),name
camera=(SDK/'4_world/entities/manbase/dayzplayer/dayzplayercameraironsights.c').read_text()
assert 'class DayZPlayerCameraOptics : DayZPlayerCameraIronsights' in camera
assert 'm_dynamicsStrength * aimChangeY' in camera
assert 'm_dynamicsStrength * aimChangeX' in camera
assert 'ProcessAimFilters' not in s and 'AimingModel(' not in s
prefix=r'''
#include <cassert>
#include <algorithm>
#include <cmath>
#include <iostream>
struct EntityAI{bool weapon=true;bool IsWeapon(){return weapon;}};
struct Stamina{float GetSyncedStaminaNormalized(){return .8f;}};
struct PlayerBase{bool raised=true,alive=true,unconscious=false,breath=false,optics=false;int lean=0;EntityAI held;Stamina stamina;bool IsRaised(){return raised;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}EntityAI* GetItemInHands(){return &held;}Stamina* GetStaminaHandler(){return &stamina;}bool IsHoldingBreath(){return breath;}int GetShakeLevel(){return 1;}bool IsInOptics(){return optics;}void DepleteStaminaEx(int,float,float){}};
struct Game{bool multi=false;PlayerBase* player=nullptr;bool IsMultiplayer(){return multi;}PlayerBase* GetPlayer(){return player;}}game;
Game* GetGame(){return &game;}
struct MovementLabStartGate{inline static bool Enabled=true;};
struct Math{static float InverseLerp(float a,float b,float c){return(c-a)/(b-a);}static float Clamp(float x,float a,float b){return std::clamp(x,a,b);}static float Lerp(float a,float b,float t){return a+(b-a)*t;}static float AbsFloat(float x){return std::abs(x);}};
struct PlayerSwayConstants{static constexpr float SWAY_MULTIPLIER_DEFAULT=1,HOLD_BREATH_STAMINA_THRESHOLD=.1f;};
struct DayZPlayerConstants{static constexpr int STANCEIDX_RAISEDPRONE=5;};
struct EStaminaModifiers{static constexpr int HOLD_BREATH=0;};
struct SDayZPlayerAimingModel{float m_fCurrentAimX=0,m_fCurrentAimY=0,m_fAimXHandsOffset=0,m_fAimYHandsOffset=0,m_fAimXCamOffset=0,m_fAimYCamOffset=0,m_fAimXMouseShift=0,m_fAimYMouseShift=0;};
struct DayZPlayerUtils{static float LinearRangeClamp(float,float y,float*){return y;}};
struct Recoil{void Update(SDayZPlayerAimingModel*,float& mx,float& my,float& hx,float& hy,float){mx=2;my=3;hx=4;hy=5;}};
struct KuruShake{void Update(float,float& x,float& y){x=.2f;y=.4f;}};
'''
base=r'''
struct AimBase{
 PlayerBase *m_PlayerPb=nullptr,*m_PlayerDpi=nullptr;Recoil recoil;Recoil* m_CurrentRecoil=&recoil;KuruShake kuru;KuruShake* m_KuruShake=&kuru;
 float m_TotalTime=0,m_ReferenceTime=0,m_StaminaPercentage=0,m_HoldBreathSwayCoef=1,m_LastSwayMultiplier=1,m_SwayWeight=1,m_CamShakeX=.7f,m_CamShakeY=.8f,m_HorizontalNoiseXAxisOffset=.5f,m_BreathingXAxisOffset=.5f,m_BreathingYAxisOffset=.5f,m_SwayModifier[3]={1,1,1},m_AimXClampRanges[1]={0};bool m_HoldingBreathSet=false;int breatheCalls=0,noiseCalls=0;
 float CalculateSpeedMultiplier(float){return 1;}float CalculateSwayMultiplier(){return 1;}float CalculateWeight(int,float,float,bool){return 1;}
 virtual void ApplyBreathingPattern(float& x,float& y,float,float,float){breatheCalls++;x=7;y=8;}
 virtual void ApplyHorizontalNoise(float& x,float& y,float,float,float,float,float,float,float){noiseCalls++;x=9;y=10;}
 void ApplyShakes(float& x,float& y,int){x=.1f;y=.3f;}
'''
actual_filter=cpp(method(native,'ProcessAimFilters'))
base+=actual_filter+'\n};\n'
guard='struct MovementLabWeaponSway{'+cpp(method(s,'ShouldSuppress'))+'};\n'
aim='struct Aim: AimBase{'+cpp(method(s,'ApplyBreathingPattern'),'AimBase')+cpp(method(s,'ApplyHorizontalNoise'),'AimBase')+'};\n'
cam=r'''
struct DayZPlayerCameraResult{float strengthSeen=-1,yawSeen=-1,pitchSeen=-1;};
struct CameraBase{PlayerBase* m_pPlayer=nullptr;float m_dynamicsStrength=2,m_velocityYaw[1]={9},m_velocityPitch[1]={8};int calls=0;virtual void OnUpdate(float,DayZPlayerCameraResult& result){calls++;result.strengthSeen=m_dynamicsStrength;result.yawSeen=m_velocityYaw[0];result.pitchSeen=m_velocityPitch[0];}};
'''
cam+='struct Camera:CameraBase{'+cpp(method(s,'OnUpdate'),'CameraBase')+'};struct Optics:Camera{};\n'
main=r'''
int main(){
 for(int fps:{30,60,144})for(bool ads:{false,true})for(int lean:{-1,0,1})for(bool hold:{false,true})for(bool off:{false,true}){
  PlayerBase p;p.optics=ads;p.lean=lean;p.breath=hold;game={};game.player=&p;MovementLabStartGate::Enabled=!off;Aim a;a.m_PlayerPb=&p;a.m_PlayerDpi=&p;SDayZPlayerAimingModel model;
  a.ProcessAimFilters(1.f/fps,&model,ads?4:3);
  float nativeSway=off?16:0;assert(std::abs(model.m_fAimXHandsOffset-(nativeSway+4+.1f+.2f))<.0001f);assert(std::abs(model.m_fAimYHandsOffset-((off?18:0)+5+.3f+.4f))<.0001f);
  assert(std::abs(model.m_fAimXCamOffset-(-.1f-4-.2f+.7f))<.0001f);assert(std::abs(model.m_fAimYCamOffset-(-.3f-5-.4f+.8f))<.0001f);assert(std::abs(model.m_fAimXMouseShift-1.98f)<.0001f);assert(std::abs(model.m_fAimYMouseShift-3.04f)<.0001f);assert(a.breatheCalls==1 && a.noiseCalls==1);
  Optics c;c.m_pPlayer=&p;DayZPlayerCameraResult result;c.OnUpdate(1.f/fps,result);assert(result.strengthSeen==(off?2:0));assert(result.yawSeen==(off?9:0));assert(result.pitchSeen==(off?8:0));assert(c.m_dynamicsStrength==2 && c.calls==1);
 }
 for(int bypass=0;bypass<7;bypass++){
  PlayerBase p,other;game={};game.player=&p;MovementLabStartGate::Enabled=true;
  if(bypass==0)game.multi=true;if(bypass==1)game.player=&other;if(bypass==2)p.raised=false;if(bypass==3)p.held.weapon=false;if(bypass==4)p.alive=false;if(bypass==5)p.unconscious=true;
  assert(!MovementLabWeaponSway::ShouldSuppress(bypass==6?nullptr:&p));
  if(bypass==6)continue;Aim a;a.m_PlayerPb=&p;float x=0,y=0;a.ApplyBreathingPattern(x,y,1,1,1);assert(x==7 && y==8);a.ApplyHorizontalNoise(x,y,1,1,1,1,1,1,1);assert(x==9 && y==10);
 }
 std::cout<<"Actual SDK aim-filter integration: sway removed, recoil/shake/mouse/clamps retained; hip/ADS/lean/holdbreath and native fallbacks passed. ADS dynamics hook passed. Native rendering pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-sway-') as d:
 p=Path(d);(p/'test.cpp').write_text(prefix+guard+base+aim+cam+main)
 subprocess.run(['g++','-std=c++17','-O0',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
