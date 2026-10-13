"""Validate the narrow ADS correction; native render/IK still needs game test."""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision40'
native=Path('/tmp/dayz-script-diff/scripts/4_world/entities/manbase/dayzplayer/dayzplayercameraironsights.c').read_text()
s=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabWeaponSway.c').read_text()
def onupdate(text):
 m=re.search(r'override void\s+OnUpdate\(',text);a=text.index('{',m.start());i=a+1;depth=1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[m.start():i]
actual=onupdate(s);original=onupdate(native)
guard='''
        if (!MovementLabWeaponSway.ShouldSuppress(PlayerBase.Cast(m_pPlayer)))
        {
            super.OnUpdate(pDt, pOutResult);
            return;
        }
'''
patch='''
        // Remove only input-driven sight misalignment. Keep native walking
        // bob, breathing, horizontal noise, recoil and hold-breath behavior.
        aimChangeX = 0;
        aimChangeY = 0;
'''
assert actual.replace(guard,'',1).replace(patch,'',1)==original
assert 'DayZPlayerImplementAiming' not in s and 'm_dynamicsStrength = 0' not in s
# All prior movement sources remain byte-identical to Revision38.
a=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision38/StartGateSource'
for p in a.rglob('*'):
 if p.is_file(): assert p.read_bytes()==(SOURCE/'StartGateSource'/p.relative_to(a)).read_bytes(),p
fragment=actual[actual.index('vector aimChangeYPR;'):actual.index('vector dynamics[4];')]
fragment=fragment.replace('vector aimChangeYPR;', 'Vec aimChangeYPR;').replace('HumanCommandMove hcm =', 'HumanCommandMove* hcm =')
fragment=fragment.replace('m_pInput.', 'm_pInput->').replace('m_pPlayer.', 'm_pPlayer->').replace('hcm.', 'hcm->').replace('Math.','Math::')
cpp=r'''
#include <cassert>
#include <cmath>
#include <iostream>
struct Vec{float v[3]={0,0,0};float& operator[](int i){return v[i];}};
struct Input{Vec delta;Vec GetAimDelta(float){return delta;}};
struct HumanCommandMove{float speed=0;float GetCurrentMovementSpeed(){return speed;}};
struct Player{HumanCommandMove move;int lean=0;HumanCommandMove* GetCommand_Move(){return &move;}};
struct Math{static constexpr float RAD2DEG=57.2957795f,PI2=6.2831853f;static float Sin(float x){return std::sin(x);}static float SmoothCD(float value,float target,float* velocity,float smooth,float,float dt){float result=value+(target-value)*(1-std::exp(-dt/smooth));velocity[0]=(result-value)/dt;return result;}};
struct Camera{
 Input* m_pInput;Player* m_pPlayer;float m_movementTimeAcc=0,m_movementAmplitudeX=1,m_movementAmplitudeY=1,m_movementFrequencyX=1,m_movementFrequencyY=2,m_dynamicsStrength=2,m_dynamicsSmoothTime=.3f,m_velocityYaw[1]={0},m_velocityPitch[1]={0};
 Vec update(float pDt){
'''+fragment+'return aimChangeYPR;}\n};\n'
cpp+=r'''
int main(){
 for(int fps:{30,60,144})for(float speed:{0.f,1.f,2.f})for(int lean:{-1,0,1}){
  Input still,moving;moving.delta[0]=.2f;moving.delta[1]=-.3f;Player p;p.move.speed=speed;p.lean=lean;Camera a,b;a.m_pInput=&still;b.m_pInput=&moving;a.m_pPlayer=b.m_pPlayer=&p;
  for(int n=0;n<fps;n++){
   Vec x=a.update(1.f/fps),y=b.update(1.f/fps);assert(std::abs(x[0]-y[0])<.000001f && std::abs(x[1]-y[1])<.000001f);if(speed==0)assert(x[0]==0 && x[1]==0);if(speed>0 && n==0)assert(x[0]!=0 && x[1]!=0);
  }
  assert(a.m_dynamicsStrength==2 && a.m_dynamicsSmoothTime==.3f);
 }
 std::cout<<"ADS input-driven misalignment removed; actual native bob fragment remains active with native strength/smoothing at30/60/144FPS and all lean angles. Original camera code otherwise identical; native breathing/holdbreath/recoil scripts untouched. In-game visual check pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-sight-') as d:
 p=Path(d);(p/'test.cpp').write_text(cpp)
 subprocess.run(['g++','-std=c++17','-O0',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
