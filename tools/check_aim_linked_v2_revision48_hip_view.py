"""Actual first-person hip-view hook with camera API mocks; no native renderer."""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision48'
s=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabHipAimView.c').read_text();a=s.index('override void OnUpdate(');b=s.index('{',a);i=b+1;depth=1
while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
method=s[a:i].replace('override ','').replace('out DayZPlayerCameraResult pOutResult','DayZPlayerCameraResult& pOutResult').replace('super.','NativeCamera::').replace('PlayerBase hipViewPlayer','PlayerBase* hipViewPlayer').replace('PlayerBase.Cast(m_pPlayer)','m_pPlayer').replace('MovementLabStartGate.','MovementLabStartGate::').replace('Math3D.','Math3D::')
for name in ('GetGame()','hipViewPlayer','m_CommandWeapons','m_pInput','GetItemInHands()','GetWeaponManager()'):method=method.replace(name+'.',name+'->')
old=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision45/StartGateSource'
for p in old.rglob('*'):
 if p.is_file():assert p.read_bytes()==(SOURCE/'StartGateSource'/p.relative_to(old)).read_bytes(),p
sdk=Path('/tmp/dayz-script-diff/scripts/3_game/human.c').read_text();assert 'without sway/offsets' in sdk
weapon_sdk=Path('/tmp/dayz-script-diff/scripts/4_world/entities/firearms/weapon_base.c').read_text();assert 'hcw.GetBaseAimingAngleLR() + player.GetOrientation()[0]' in weapon_sdk
assert 'pOutResult.m_fUseHeading = 0;' in s
assert 'MovementLabHipFastAim' not in (SOURCE/'WorkspacePatches/locomotion.agr').read_text()
cpp=r'''
#include <cassert>
#include <cmath>
#include <iostream>
struct Vec{float v[3]={0,0,0};float& operator[](int i){return v[i];}};
struct DayZPlayerCameraResult{Vec m_CameraTM[4];int bone=9;float fov=1,near=.04f,m_fUseHeading=1;};
struct Math3D{static void YawPitchRollMatrix(Vec v,Vec* out){out[0]=v;}};
struct Item{bool weapon=true;bool IsWeapon(){return weapon;}};
struct Manager{bool running=false;bool IsRunning(){return running;}};
struct PlayerBase{Vec orientation;Vec GetOrientation(){return orientation;}bool alive=true,unconscious=false,raised=true,iron=false,optics=false,lift=false,blocked=false,hasItem=true,hasManager=true;Item item;Manager manager;bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsInIronsights(){return iron;}bool IsInOptics(){return optics;}Item* GetItemInHands(){return hasItem?&item:nullptr;}Manager* GetWeaponManager(){return hasManager?&manager:nullptr;}bool IsLiftWeapon(){return lift;}bool IsWeaponObstructionBlockingADS(){return blocked;}};
struct Input{bool free=false,tracking=false;bool CameraIsFreeLook(){return free;}bool CameraIsTracking(){return tracking;}};
struct Weapons{float yaw=0,pitch=0;float GetBaseAimingAngleLR(){return yaw;}float GetBaseAimingAngleUD(){return pitch;}};
struct Game{bool multi=false;PlayerBase* player=nullptr;bool IsMultiplayer(){return multi;}PlayerBase* GetPlayer(){return player;}}game;
Game* GetGame(){return &game;}struct MovementLabStartGate{inline static bool Enabled=true;};
struct NativeCamera{PlayerBase* m_pPlayer=nullptr;Input* m_pInput=nullptr;Weapons* m_CommandWeapons=nullptr;Vec m_OffsetLS;float m_CurrentCameraYaw=0,m_CurrentCameraPitch=0,m_fLeftRightAngle=0,m_fLeftRightAngleAdd=0,m_fUpDownAngle=0,m_fUpDownAngleAdd=0,shakeYaw=0,shakePitch=0;int calls=0;Vec GetCurrentOrientation(){Vec r;r[0]=m_CurrentCameraYaw;r[1]=m_CurrentCameraPitch;return r;}void OnUpdate(float,DayZPlayerCameraResult& r){calls++;m_CurrentCameraYaw=m_fLeftRightAngle+m_fLeftRightAngleAdd;m_CurrentCameraPitch=m_fUpDownAngle+m_fUpDownAngleAdd;Math3D::YawPitchRollMatrix(GetCurrentOrientation(),r.m_CameraTM);r.m_CameraTM[3]=m_OffsetLS;m_fLeftRightAngle+=shakeYaw;m_fUpDownAngleAdd+=shakePitch;}};
struct Camera:NativeCamera{
'''+method+r'''
};
int main(){
 for(float yaw:{-80.f,0.f,80.f})for(float pitch:{-70.f,0.f,70.f})for(bool shake:{false,true}){
  PlayerBase p;game={};game.player=&p;p.orientation[0]=37;Input input;Weapons w;w.yaw=yaw;w.pitch=pitch;Camera c;c.m_pPlayer=&p;c.m_pInput=&input;c.m_CommandWeapons=&w;c.m_OffsetLS[0]=.04f;c.m_OffsetLS[1]=.04f;c.m_fLeftRightAngle=10;c.m_fUpDownAngle=15;c.shakeYaw=shake?.5f:0;c.shakePitch=shake?.75f:0;DayZPlayerCameraResult r;c.OnUpdate(.016f,r);assert(c.calls==1 && r.m_fUseHeading==0);assert(r.m_CameraTM[0][0]==37+yaw+c.shakeYaw && r.m_CameraTM[0][1]==pitch+c.shakePitch);assert(r.m_CameraTM[3][0]==.04f && r.m_CameraTM[3][1]==.04f && r.bone==9 && r.fov==1 && r.near==.04f);assert(c.m_fLeftRightAngle==10+c.shakeYaw && c.m_fUpDownAngle==15);
 }

 // Simulated body-turn lag: base aim is body-relative. Absolute camera yaw
 // must stay at input target immediately, regardless of delayed body rotation.
 for(int fps:{30,60,144})for(float target:{-170.f,-90.f,90.f,170.f}){
  PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;Input input;Weapons w;Camera c;c.m_pPlayer=&p;c.m_pInput=&input;c.m_CommandWeapons=&w;float body=0;
  for(int frame=0;frame<fps;frame++){
   p.orientation[0]=body;w.yaw=target-body;w.pitch=frame%2?30:-30;DayZPlayerCameraResult r;c.OnUpdate(1.f/fps,r);
   assert(std::abs(r.m_CameraTM[0][0]-target)<.0001f && r.m_CameraTM[0][1]==w.pitch && r.m_fUseHeading==0);
   // The previous implementation applied input heading plus this base LR.
   if(frame==0)assert(std::abs((target+w.yaw)-target)>1);
   body+=(target-body)*.05f;
  }
 }
 for(int reason=0;reason<16;reason++){
  PlayerBase p,other;game={};game.player=&p;MovementLabStartGate::Enabled=true;Input input;Weapons w;w.yaw=70;w.pitch=60;Camera c;c.m_pPlayer=&p;c.m_pInput=&input;c.m_CommandWeapons=&w;
  if(reason==0)MovementLabStartGate::Enabled=false;if(reason==1)game.multi=true;if(reason==2)game.player=&other;if(reason==3)p.alive=false;if(reason==4)p.unconscious=true;if(reason==5)p.raised=false;if(reason==6)p.iron=true;if(reason==7)p.optics=true;if(reason==8)input.free=true;if(reason==9)input.tracking=true;if(reason==10)p.item.weapon=false;if(reason==11)p.hasItem=false;if(reason==12)p.lift=true;if(reason==13)p.blocked=true;if(reason==14)p.manager.running=true;if(reason==15)p.hasManager=false;
  DayZPlayerCameraResult r;c.OnUpdate(.016f,r);assert(c.calls==1 && r.m_fUseHeading==1 && r.m_CameraTM[0][0]==0 && r.m_CameraTM[0][1]==0);
 }
 std::cout<<"Actual hipcamera matches native gun worldyaw/body+baseLR with engineheading addedzero times; body-turn-lag scenarios immediate; native pose/recoil/sway modules byte-identical; camera shake preserved; ADS/freeLook/invalid states untouched. Native weapon projection/inputfeel still needs test.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-hip-view-') as d:
 p=Path(d);(p/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
