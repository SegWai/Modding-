"""Check production camera-pivot geometry against the fixed body-space anchor."""
from pathlib import Path
import subprocess,tempfile
from dayz_graph_formats import end
root=Path(__file__).resolve().parents[1]
s=(root/'hud-icons-test/MovementLabLocomotion_v72/StartGateSource/Scripts/4_World/MovementLabRightShoulder.c').read_text()
methods=[]
for name in ['MovementLabHeadingVectorToBody','MovementLabFixedShoulderPivot']:
 start=s.index('    protected vector '+name+'(')
 methods.append(s[start:end(s,start)].replace('protected vector','Vec3').replace('vector ','Vec3 ').replace('Math.','Math::'))
h='''#include <cmath>
#include <cassert>
#include <initializer_list>
struct Vec3 {float x,y,z;float& operator[](int i){return i==0?x:(i==1?y:z);}float operator[](int i)const{return i==0?x:(i==1?y:z);}};
Vec3 Vector(float x,float y,float z){return{x,y,z};}
Vec3 operator+(Vec3 a,Vec3 b){return{a.x+b.x,a.y+b.y,a.z+b.z};}
Vec3 operator-(Vec3 a,Vec3 b){return{a.x-b.x,a.y-b.y,a.z-b.z};}
Vec3 operator*(Vec3 a,float b){return{a.x*b,a.y*b,a.z*b};}
namespace Math {constexpr float DEG2RAD=3.14159265358979323846f/180;float Sin(float a){return std::sin(a);}float Cos(float a){return std::cos(a);}}
struct Probe {'''+ '\n'.join(methods)+'''\n};
float error(Vec3 a,Vec3 b){return std::abs(a.x-b.x)+std::abs(a.y-b.y)+std::abs(a.z-b.z);}
int main(){Probe p;int cases=0;
 for(float bodyYaw:{-179.f,-90.f,0.f,90.f,179.f})
 for(float headingYaw:{-179.f,-90.f,0.f,90.f,179.f})
 for(float localYaw:{-100.f,-90.f,-45.f,0.f,45.f,90.f,100.f})
 for(float pitch:{-80.f,-30.f,0.f,30.f,80.f})
 for(float distance:{0.8f,1.f,1.4f,1.6f})
 for(float shoulder:{0.3f,0.4f,0.5f}){
  float yaw=localYaw*Math::DEG2RAD;float pit=pitch*Math::DEG2RAD;
  Vec3 headingForward={std::sin(yaw)*std::cos(pit),std::sin(pit),std::cos(yaw)*std::cos(pit)};
  Vec3 bodyForward=p.MovementLabHeadingVectorToBody(headingForward,headingYaw-bodyYaw);
  Vec3 base={0.05f,0.7f,0.1f},ls={0.f,0.3f,0.f};
  Vec3 pivot=p.MovementLabFixedShoulderPivot(base,ls,shoulder,distance,bodyForward);
  // Native camera evaluates its distance along the current look vector.
  Vec3 finalOrigin=pivot-bodyForward*distance;
  Vec3 expected={base.x+ls.x+shoulder,base.y+ls.y,base.z+ls.z-distance};
  assert(error(finalOrigin,expected)<0.00001f);
  assert(finalOrigin.x>0);
  cases++;
 }
 // With default forward look and aligned body/heading, retain native framing.
 Vec3 base={0.f,1.4f,0.f},ls={0.f,0.3f,0.f},forward={0.f,0.f,1.f};
 Vec3 nativePivot={0.3f,1.7f,0.f};
 assert(error(p.MovementLabFixedShoulderPivot(base,ls,0.3f,1.6f,forward),nativePivot)<0.00001f);
 return cases==10500?0:1;
}
'''
with tempfile.TemporaryDirectory(prefix='right-shoulder-') as tmp:
 f=Path(tmp)/'geometry.cpp';binary=Path(tmp)/'geometry';f.write_text(h)
 subprocess.run(['c++','-std=c++17','-O2',str(f),'-o',str(binary)],check=True)
 subprocess.run([str(binary)],check=True)
assert 'result.m_fDistance =' not in s
assert 'result.m_fUseHeading =' not in s
assert 'Override3rdIsRightShoulder(HumanInputControllerOverrideType.ONE_FRAME, true)' in s
old=root/'hud-icons-test/MovementLabLocomotion_v71'
new=root/'hud-icons-test/MovementLabLocomotion_v72'
for sub in ['WorkspacePatches','Missions']:
 for f in (old/sub).rglob('*'):
  if f.is_file():assert f.read_bytes()==(new/sub/f.relative_to(old/sub)).read_bytes()
assert (old/'StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_bytes()==(new/'StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_bytes()
print('PASS: 10,500 production geometry scenarios; fixed right-side camera origin across body/look yaw and pitch; default forward framing preserved; native distance/orientation and working graphs unchanged. Native renderer/collision testing pending.')
