#!/usr/bin/env python3
"""Exercise the actual isolated command hook using the existing SDK mock.
No native Enforce compilation, animation frames or physics are modeled.
"""
from pathlib import Path
import ast,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
w=(ROOT/'walk-blend-test/MovementLabJogWalkBlendTest/StartGateSource/Scripts/4_World/MovementLabWalkBlend.c').read_text()
for banned in ['SetVelocity(', 'SetPosition(', 'StartCommand_Script', 'SetRunSprintFilterModifier', 'MovementLabBeginBrake']:
    assert banned not in w
assert 'override void CommandHandler(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)' in w
sdk=None
for node in ast.parse((ROOT/'tools/check_ctrl_modes.py').read_text()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='sdk' for t in node.targets):
        sdk=ast.literal_eval(node.value)
assert sdk
sdk=sdk.replace('move.speed=input.speedOn?input.speed:0;', 'bool moving=false;for(int i=0;i<4;i++)moving=moving||api.a[i].value>.05f;float native=api.a[6].value>.05f?3:api.a[4].value>.05f?1:2;move.speed=input.speedOn?input.speed:moving?native:0;')
s=w.replace('modded class PlayerBase','class Probe : public SDKPlayer').replace('protected ','').replace('override ','').replace('super.CommandHandler(', 'SDKPlayer::CommandHandler(')
s=s.replace('HumanMovementState state = new HumanMovementState();','HumanMovementState state;').replace('static bool Enabled;', 'inline static bool Enabled = false;')
for name in ['Math','MovementLabStartGate','HumanInputControllerOverrideType','DayZPlayerConstants']:s=s.replace(name+'.',name+'::')
s=re.sub(r'(class [^\n]+\n\{)',r'\1\npublic:',s)
s=re.sub(r'^    (float|int|bool) (\w+);',r'    \1 \2 = 0;',s,flags=re.M)
s=re.sub(r'^}', '};',s,flags=re.M)
tests=r'''
void reset(Probe& p){game={};api={};MovementLabStartGate::Enabled=true;game.player=&p;}
int main(){
 for(int fps:{30,60,144})for(float gait:{1.5f,1.9f,2.f,2.05f})for(int keys:{1,2,4,8,5,9}){
  Probe p;reset(p);p.move.speed=gait;float dt=1.f/fps;
  for(int k=0;k<4;k++)api.a[k].value=(keys&(1<<k))?1:0;
  api.a[4].value=1;float previous=gait;int frames=0;
  do{
   p.CommandHandler(dt,1,false);frames++;
   assert(p.move.speed<=previous+.00001 && p.move.speed>=1);
   if(p.m_MovementLabBlendOwnsSpeed){
    float t=std::min(frames*dt/.45f,1.f);
    float expected=gait+(1-gait)*t*t*(3-2*t);
    assert(std::abs(p.move.speed-expected)<.0001);
    assert(!p.input.angleOn);
   }
   previous=p.move.speed;
  }while(p.m_MovementLabBlendOwnsSpeed);
  assert(p.move.speed==1 && frames*dt>=.45f && frames*dt<.45f+dt+.0001);
  for(int i=0;i<fps;i++){p.CommandHandler(dt,1,false);assert(!p.m_MovementLabBlendOwnsSpeed && p.move.speed==1);}
  api.a[4].value=0;p.CommandHandler(dt,1,false);assert(p.move.speed==2);
 }
 // Cancellations release ownership before native handler: no generated coast.
 for(int reason=0;reason<9;reason++){
  Probe p;reset(p);p.move.speed=2;api.a[0].value=api.a[4].value=1;
  p.CommandHandler(.016f,1,false);assert(p.m_MovementLabBlendOwnsSpeed);
  switch(reason){case 0:api.a[0].value=0;break;case 1:api.a[4].value=0;break;
   case 2:api.a[6].value=1;break;case 3:game.ui.menu=true;break;
   case 4:p.stance=1;break;case 5:MovementLabStartGate::Enabled=false;break;
   case 6:p.raised=true;break;case 7:api.a[0].value=0;api.a[2].value=1;break;
   case 8:game.multi=true;break;}
  p.CommandHandler(.016f,1,false);assert(!p.m_MovementLabBlendOwnsSpeed && !p.input.speedOn);
  if(reason==0)assert(p.move.speed==0);
 }
 // Native jogging/sprinting/startup unaffected outside this one handoff.
 for(float gait:{0.f,1.f,2.2f,3.f}){
  Probe p;reset(p);p.move.speed=gait;api.a[0].value=api.a[4].value=1;
  p.CommandHandler(.016f,1,false);assert(!p.m_MovementLabBlendOwnsSpeed);
 }
 Probe p;reset(p);api.a[0].value=1;p.CommandHandler(.016f,1,false);assert(p.move.speed==2 && !p.input.speedOn);
 api.a[6].value=1;p.CommandHandler(.016f,1,false);assert(p.move.speed==3 && !p.input.speedOn);
 std::cout<<"Isolated jog-to-walk actual translated hook passed: monotonic 0.45s easing and native walking handoff at 30/60/144 FPS across directions; input/UI/stance/turbo/toggle cancellations; no speed or angle ownership outside transition. Native compile/visual/physics test pending.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='jog-walk-blend-') as temp:
    cpp=Path(temp)/'check.cpp';binary=Path(temp)/'check'
    cpp.write_text(sdk+s+tests)
    subprocess.run(['g++','-std=c++17',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
