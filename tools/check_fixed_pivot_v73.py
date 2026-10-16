"""Test the actual pivot conversion in the SDK's documented heading/model spaces."""
from pathlib import Path
import subprocess,tempfile
from dayz_graph_formats import end
root=Path(__file__).resolve().parents[1]
p=root/'hud-icons-test/MovementLabLocomotion_v73/StartGateSource/Scripts/4_World/MovementLabFixedPivot.c'
s=p.read_text();methods=[]
for name in ['MovementLabRotateOffsetYaw','MovementLabPivotForFixedOrigin']:
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
Vec3 look(float yaw,float pitch){float y=yaw*Math::DEG2RAD,p=pitch*Math::DEG2RAD;return{std::sin(y)*std::cos(p),std::sin(p),std::cos(y)*std::cos(p)};}
int main(){Probe p;int cases=0;
 for(int modelPosition:{0,1})
 for(float initialBody:{-179.f,0.f,179.f})
 for(float initialHeading:{-170.f,0.f,170.f})
 for(float distance:{0.8f,1.f,1.4f,1.6f}){
  Vec3 nativePivot={0.3f,1.7f,0.1f};Vec3 initialLook=look(20.f,-15.f);
  float positionYaw=modelPosition?initialBody:initialHeading;
  Vec3 nativeOrigin=p.MovementLabRotateOffsetYaw(nativePivot,positionYaw)-p.MovementLabRotateOffsetYaw(initialLook,initialHeading)*distance;
  // Capture the existing native framing. The first converted frame must match.
  Vec3 firstPivot=p.MovementLabPivotForFixedOrigin(nativeOrigin,initialLook,initialHeading,distance);
  Vec3 firstOrigin=p.MovementLabRotateOffsetYaw(firstPivot-initialLook*distance,initialHeading);
  assert(error(firstOrigin,nativeOrigin)<0.00002f);
  for(float heading:{-179.f,-90.f,0.f,90.f,179.f})
  for(float yaw:{-100.f,-60.f,0.f,60.f,100.f})
  for(float pitch:{-80.f,-30.f,0.f,30.f,80.f}){
   Vec3 direction=look(yaw,pitch);
   Vec3 pivot=p.MovementLabPivotForFixedOrigin(nativeOrigin,direction,heading,distance);
   Vec3 finalOffset=p.MovementLabRotateOffsetYaw(pivot-direction*distance,heading);
   assert(error(finalOffset,nativeOrigin)<0.00002f);
   Vec3 playerTranslation={13.f,2.f,-21.f};
   assert(error((playerTranslation+finalOffset)-nativeOrigin,playerTranslation)<0.00002f);
   cases++;
  }
 }
 return cases==9000?0:1;
}
'''
with tempfile.TemporaryDirectory(prefix='fixed-pivot-') as tmp:
 f=Path(tmp)/'geometry.cpp';binary=Path(tmp)/'geometry';f.write_text(h)
 subprocess.run(['c++','-std=c++17','-O2',str(f),'-o',str(binary)],check=True)
 subprocess.run([str(binary)],check=True)
assert 'result.m_fDistance =' not in s and 'result.m_fUseHeading =' not in s
assert 'Override3rdIsRightShoulder' not in s
assert 'result.m_fPositionModelSpace = 0.0;' in s
old=root/'hud-icons-test/MovementLabLocomotion_v71';new=root/'hud-icons-test/MovementLabLocomotion_v73'
assert (old/'StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_bytes()==(new/'StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_bytes()
assert not (new/'StartGateSource/Scripts/4_World/MovementLabRightShoulder.c').exists()
for f in (old/'WorkspacePatches').rglob('*'):
 if f.is_file():assert f.read_bytes()==(new/'WorkspacePatches'/f.relative_to(old/'WorkspacePatches')).read_bytes()
print('PASS: 9,000 actual-source geometry cases: initial native framing retained; fixed origin across look yaw/pitch and heading changes; player translation followed. v71 look/head code and animation graphs unchanged; v72 absent. Native rendering/collisions pending.')
