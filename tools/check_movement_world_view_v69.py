"""Exercise production world-view offset with independently delayed engine headings."""
from pathlib import Path
import subprocess,tempfile
from dayz_graph_formats import end
root=Path(__file__).resolve().parents[1]
s=(root/'hud-icons-test/MovementLabLocomotion_v69/StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_text()
a=s.index('    protected float MovementLabWorldViewOffset(')
method=s[a:end(s,a)].replace('protected float','float')
harness='''#include <cassert>
#include <cmath>
#include <initializer_list>
struct Probe {'''+method+'''\n};
float wrap(float a){while(a>180)a-=360;while(a < -180)a+=360;return a;}
int main(){Probe p;int scenarios=0;
 for(float world:{-179.f,-100.f,-1.f,0.f,1.f,100.f,179.f})
 for(float initialHeading:{-179.f,-90.f,0.f,90.f,179.f})
 for(int fps:{30,60,144})for(int delayedFrames:{0,2,30}){
  float desired=world;
  float originalWorld=world;
  float remaining=wrap(-world-initialHeading);
  for(int frame=0;frame<=fps*2+delayedFrames;frame++){
   float t=float(frame-delayedFrames)/float(fps*2);
   t=t<0?0:(t>1?1:t);
   // Actual engine heading is delayed independently of the raw input angle.
   float engineHeading=wrap(initialHeading+remaining*t);
   float offset=p.MovementLabWorldViewOffset(desired,engineHeading);
   assert(std::abs(wrap(-engineHeading+offset-desired))<0.0001f);
   assert(std::abs(wrap(-engineHeading+offset-originalWorld))<0.0001f);
  }
  assert(std::abs(p.MovementLabWorldViewOffset(world,wrap(-world)))<0.0001f);
  // Continued mouse movement must change the held world target, including wrap.
  float engine=initialHeading;
  for(int frame=0;frame<fps*4;frame++){
   float mouse=37.f/fps;
   desired=wrap(desired+mouse);
   engine=wrap(engine-mouse*0.8f);
   float offset=p.MovementLabWorldViewOffset(desired,engine);
   assert(std::abs(wrap(-engine+offset-desired))<0.0001f);
  }
  scenarios++;
 }
 return scenarios==315?0:1;
}
'''
with tempfile.TemporaryDirectory(prefix='movement-world-view-') as tmp:
 f=Path(tmp)/'world.cpp';binary=Path(tmp)/'world';f.write_text(harness)
 subprocess.run(['c++','-std=c++17','-O2',str(f),'-o',str(binary)],check=True)
 subprocess.run([str(binary)],check=True)
# Scope of the native HeadingModel observation: forward values and return unchanged.
a=s.index('    override bool HeadingModel(');b=s[a:end(s,a)]
assert 'super.HeadingModel(pDt, pModel)' in b and 'return changed;' in b
assert 'pModel.m_fHeadingAngle =' not in b and 'pModel.m_fOrientationAngle =' not in b
assert 'm_MovementLabHandoffUntil' not in s
assert 'm_MovementLabHandoffWorldYaw += GetInputController().GetAimDelta(pDt)[0]' in s
assert 'pAngleAdd = handoffOffset;' in s and 'm_LookAtLRAngle = handoffOffset;' in s
for f in (root/'hud-icons-test/MovementLabLocomotion_v68/WorkspacePatches').rglob('*'):
 if f.is_file():assert f.read_bytes()==(root/'hud-icons-test/MovementLabLocomotion_v69/WorkspacePatches'/f.relative_to(root/'hud-icons-test/MovementLabLocomotion_v68/WorkspacePatches')).read_bytes()
print('PASS: 315 production-math scenarios with delayed engine heading beyond 500ms, angle wrap, mouse input, 30/60/144 FPS; HeadingModel is read-only; working 1.30 graph files unchanged. Native playback pending.')
