"""Run the production handoff remainder calculation against delayed native-heading updates."""
from pathlib import Path
import subprocess,tempfile
from dayz_graph_formats import end
root=Path(__file__).resolve().parents[1]
s=(root/'hud-icons-test/MovementLabLocomotion_v67/StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_text()
a=s.index('    protected float MovementLabHandoffRemainder(')
method=s[a:end(s,a)].replace('protected float','float').replace('Math.Clamp','std::clamp')
# Native Enforce literals are floats here; C++ std::clamp needs homogeneous types.
method=method.replace(', 0,',', 0.f,').replace(', 0);',', 0.f);')
harness='''#include <algorithm>
#include <cassert>
#include <cmath>
struct Probe {
 float m_MovementLabHandoffHeading=0;
 float m_MovementLabHandoffYaw=0;
'''+method+'''\n};
float wrap(float angle) {while(angle>180)angle-=360;while(angle < -180)angle+=360;return angle;}
int main(){
 int scenarios=0;
 for(float heading:{-179.f,-90.f,0.f,90.f,179.f})
 for(float look:{-100.f,-60.f,-1.f,0.f,1.f,60.f,100.f})
 for(int fps:{30,60,144})for(int delay:{0,1,2}){
  Probe p;p.m_MovementLabHandoffHeading=heading;p.m_MovementLabHandoffYaw=look;
  // Camera may evaluate before heading updates, or while native turning settles.
  for(int frame=0;frame<=fps/2+delay;frame++){
   float fraction=std::clamp(float(frame-delay)/float(fps/2),0.f,1.f);
   float actual=wrap(heading+look*fraction);
   float offset=p.MovementLabHandoffRemainder(actual);
   assert(std::abs(wrap(actual+offset-heading-look))<0.0001f);
   if(frame<=delay)assert(std::abs(offset-look)<0.0001f);
  }
  assert(std::abs(p.MovementLabHandoffRemainder(wrap(heading+look)))<0.0001f);
  if(look!=0){float overshoot=look>0?3.f:-3.f;
   assert(std::abs(p.MovementLabHandoffRemainder(wrap(heading+look+overshoot)))<0.0001f);
  }
  scenarios++;
 }
 return scenarios==315?0:1;
}
'''
with tempfile.TemporaryDirectory(prefix='movement-look-') as tmp:
 source=Path(tmp)/'handoff.cpp';binary=Path(tmp)/'handoff';source.write_text(harness)
 subprocess.run(['c++','-std=c++17','-O2',str(source),'-o',str(binary)],check=True)
 subprocess.run([str(binary)],check=True)
assert 'MovementLabTakeLookOffsetReset' not in s
assert 'pAngleAdd = 0;' not in s
assert s.index('m_MovementLabHandoffHeading = GetInputController().GetHeadingAngle()')<s.index('OverrideAimChangeX(')
old=root/'hud-icons-test/MovementLabLocomotion_v66/WorkspacePatches'
for f in old.rglob('*'):
 if f.is_file():assert f.read_bytes()==(root/'hud-icons-test/MovementLabLocomotion_v67/WorkspacePatches'/f.relative_to(old)).read_bytes()
print('PASS: 315 production-math scenarios (left/right, wrap, delayed headings, 30/60/144 FPS); native movement input preserved; working 1.30 graphs unchanged. Native playback pending.')
