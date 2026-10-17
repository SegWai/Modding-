from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'hud-icons-test/MovementLabLocomotion_v90/StartGateSource/Scripts/4_World/MovementLabRangePatrol.c').read_text()
method=s[s.index('    void MovementLabUpdateRangePatrol()'):s.rindex('}')]
method=method.replace('HumanInputController input','HumanInputController* input').replace('GetGame().','GetGame()->').replace('input.','input->').replace('HumanInputControllerOverrideType.','HumanInputControllerOverrideType::').replace('MovementLabStartGate.','MovementLabStartGate::')
code=r'''
#include <cassert>
struct vector {float v[3]={0,0,0};float& operator[](int i){return v[i];}vector operator-(vector b){return {{v[0]-b.v[0],v[1]-b.v[1],v[2]-b.v[2]}};}};
struct HumanInputControllerOverrideType {enum {DISABLED,ENABLED};};
struct HumanInputController {float speed=0,angle=0;int releases=0;void OverrideMovementSpeed(int mode,float v){speed=v;if(mode==0)releases++;}void OverrideMovementAngle(int,float v){angle=v;}};
struct Game {bool multi=false;void* player=nullptr;bool IsMultiplayer(){return multi;}void* GetPlayer(){return player;}} game;
Game* GetGame(){return &game;}
struct MovementLabStartGate{static bool Enabled;};bool MovementLabStartGate::Enabled=true;
struct Target {
 bool m_MovementLabRangePatrolEnabled=true,m_MovementLabRangePatrolOwnsInput=false,alive=true,unconscious=false,moving=true;
 vector m_MovementLabRangePatrolCenter,m_MovementLabRangePatrolRight={{1,0,0}},position;
 float m_MovementLabRangePatrolSign=-1;HumanInputController input;
 HumanInputController* GetInputController(){return &input;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool GetCommand_Move(){return moving;}vector GetPosition(){return position;}
 METHOD
};
int main(){
 Target t;t.MovementLabUpdateRangePatrol();assert(t.input.speed==2&&t.input.angle==-90);
 t.position[0]=-0.99f;t.MovementLabUpdateRangePatrol();assert(t.input.angle==-90);
 t.position[0]=-1;t.MovementLabUpdateRangePatrol();assert(t.input.angle==90);
 t.position[0]=0;t.MovementLabUpdateRangePatrol();assert(t.input.angle==90);
 t.position[0]=1;t.MovementLabUpdateRangePatrol();assert(t.input.angle==-90);
 t.alive=false;t.MovementLabUpdateRangePatrol();assert(t.input.speed==0&&t.input.releases==1&&!t.m_MovementLabRangePatrolOwnsInput);
 t.MovementLabUpdateRangePatrol();assert(t.input.releases==1);
 Target notInitialized;notInitialized.m_MovementLabRangePatrolEnabled=false;notInitialized.MovementLabUpdateRangePatrol();assert(notInitialized.input.speed==0);
 Target selected;game.player=&selected;selected.MovementLabUpdateRangePatrol();assert(selected.input.speed==0);game.player=nullptr;
 Target multiplayer;game.multi=true;multiplayer.MovementLabUpdateRangePatrol();assert(multiplayer.input.speed==0);game.multi=false;
 Target unconscious;unconscious.unconscious=true;unconscious.MovementLabUpdateRangePatrol();assert(unconscious.input.speed==0);
 Target respawn;respawn.MovementLabUpdateRangePatrol();assert(respawn.input.speed==2&&respawn.input.angle==-90);
 Target rotated;rotated.m_MovementLabRangePatrolRight={{0,0,-1}};rotated.position[2]=1;rotated.MovementLabUpdateRangePatrol();assert(rotated.input.angle==90);
}
'''.replace('METHOD',method)
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Actual patrol method passed mocked checks: endpoint reversal, body axes, death release, guards and fresh-instance restart. Native movement unverified.')
