from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1];s=(root/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision34/StartGateSource/Scripts/4_World/MovementLabAltADS.c').read_text();a=s.index('    override int CameraHandler');b=s.index('    void MovementLabToggleAltADS',a);method=s[a:b].replace('override ','').replace('MovementLabStartGate.','MovementLabStartGate::').replace('GetGame().','GetGame()->').replace('cameraADSInput.','cameraADSInput->').replace('HumanInputController cameraADSInput','HumanInputController* cameraADSInput').replace('super.CameraHandler','Base::CameraHandler')
cpp='''#include <cassert>
#include <initializer_list>
struct MovementLabStartGate{inline static bool Enabled=true;};struct HumanInputController{bool nativeADS=true;bool WeaponADS(){return nativeADS;}void ResetADS(){nativeADS=false;}};
struct Game{bool multi=false;void* player=nullptr;bool IsMultiplayer(){return multi;}void* GetPlayer(){return player;}}game;Game* GetGame(){return &game;}
struct Base{HumanInputController input;bool sights=false;int stance=0;HumanInputController* GetInputController(){return &input;}int CameraHandler(int){return sights?2:input.WeaponADS()?1:3;}};
struct Player:Base{
'''+method+'''};
int main(){Player p;game.player=&p;for(int stance:{0,1,2,3,4,5}){p.stance=stance;p.input.nativeADS=true;p.sights=false;assert(p.CameraHandler(0)==3 && !p.input.nativeADS);p.sights=true;p.input.nativeADS=true;assert(p.CameraHandler(0)==2);}game.multi=true;p.input.nativeADS=true;p.sights=false;assert(p.CameraHandler(0)==1 && p.input.nativeADS);}
'''.replace('#include <cassert>','#include <cassert>\n#include <initializer_list>')
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
print('Actual camera wrapper clears native ADS request for all six stance IDs, preserves existing sights and native multiplayer behavior. Native camera test pending.')
