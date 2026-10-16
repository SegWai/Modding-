from pathlib import Path
import subprocess,tempfile,sys
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'hud-icons-test/MovementLabLocomotion_v85/StartGateSource/Scripts/4_World/MovementLabRangeNPC.c'
s=p.read_text();method=s[s.index('    void MovementLabUpdateRangeRagdoll()'):s.index('    override void OnUnconsciousStart()')].replace('GetGame().','GetGame()->')
harness=r'''
#include <cassert>
struct Game {int now=10000; bool multi=false; int GetTime(){return now;} bool IsMultiplayer(){return multi;}} game;
Game* GetGame(){return &game;}
struct Target {
 bool m_MovementLabRangeTarget=true, m_MovementLabRangeRagdollStarted=false, m_MovementLabRangeRagdollStopped=false;
 int m_MovementLabRangeRagdollOnAt=10100,m_MovementLabRangeRagdollOffAt=12000;
 bool physics=false,frozen=false;int enables=0,disables=0;
 void PhysicsSetRagdoll(bool v){physics=v;if(v)++enables;else ++disables;}
 void DisableSimulation(bool v){frozen=v;}
 METHOD
};
int main(){
 Target t;
 for(int time: {10000,10099}) {game.now=time;t.MovementLabUpdateRangeRagdoll();assert(!t.physics&&!t.frozen&&t.enables==0);}
 game.now=10100;t.MovementLabUpdateRangeRagdoll();assert(t.physics&&!t.frozen&&t.enables==1);
 game.now=11999;t.MovementLabUpdateRangeRagdoll();assert(t.physics&&t.enables==1);
 game.now=12000;t.MovementLabUpdateRangeRagdoll();assert(!t.physics&&t.frozen&&t.disables==1);
 game.now=15000;t.MovementLabUpdateRangeRagdoll();assert(!t.physics&&t.disables==1);
 Target skipped;game.now=13000;skipped.MovementLabUpdateRangeRagdoll();assert(skipped.enables==0&&skipped.frozen);
 Target multiplayer;game.multi=true;multiplayer.MovementLabUpdateRangeRagdoll();assert(!multiplayer.frozen&&multiplayer.enables==0);game.multi=false;
 Target unmarked;unmarked.m_MovementLabRangeTarget=false;unmarked.MovementLabUpdateRangeRagdoll();assert(!unmarked.frozen);
 Target idle;idle.m_MovementLabRangeRagdollOffAt=0;idle.MovementLabUpdateRangeRagdoll();assert(!idle.frozen);
 // A second knockout resets both phase flags and deadlines.
 t.m_MovementLabRangeRagdollStarted=false;t.m_MovementLabRangeRagdollStopped=false;
 t.m_MovementLabRangeRagdollOnAt=20100;t.m_MovementLabRangeRagdollOffAt=22000;
 game.now=20100;t.MovementLabUpdateRangeRagdoll();assert(t.physics&&!t.frozen&&t.enables==2);
 game.now=22000;t.MovementLabUpdateRangeRagdoll();assert(!t.physics&&t.frozen&&t.disables==2);
}
'''.replace('METHOD',method).replace('#include <cassert>','#include <cassert>\n#include <initializer_list>')
with tempfile.TemporaryDirectory() as d:
 path=Path(d);(path/'test.cpp').write_text(harness)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(path/'test.cpp'),'-o',str(path/'test')],check=True)
 subprocess.run([str(path/'test')],check=True)
print('Actual ragdoll timer method passed: 100ms/2s edges, skipped interval, guards, repeat cycle (mock native calls; no game verification).')
