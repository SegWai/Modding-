"""Validate experimental IK selection; native IK numeric semantics unverified."""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision47'
s=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text();a=s.index('    protected void MovementLabUpdateHipAimResponse()');b=s.index('    override void CommandHandler(',a);method=s[a:b].replace('protected ','').replace('MovementLabStartGate.','MovementLabStartGate::')
for name in ('GetGame()','GetAnimInterface()','GetItemInHands()','GetInputController()','GetWeaponManager()'):method=method.replace(name+'.',name+'->')
graph=(SOURCE/'WorkspacePatches/locomotion.agr').read_text()
def node(text,name):
 m=re.search(r'\$Node \w+ \{\s*"'+name+'"',text);start=text.index('{',m.start());i=start+1;depth=1;quoted=False;escaped=False
 while depth:
  c=text[i]
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='{':depth+=1
  elif c=='}':depth-=1
  i+=1
 return text[m.start():i]
prior=(ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision46/WorkspacePatches/locomotion.agr').read_text();original=node(prior,'NormalWeaponIK')
assert node(graph,'NormalWeaponIKMLNative')==original.replace('"NormalWeaponIK"','"NormalWeaponIKMLNative"',1)
assert node(graph,'NormalWeaponIKMLHipFast')==original.replace('"NormalWeaponIK"','"NormalWeaponIKMLHipFast"',1).replace('0.36 0.15 "AimIKX" "AimY"','0.04 0.04 "AimIKX" "AimY"',1)
assert '"MovementLabHipFastAim" "NormalWeaponIKMLNative" "NormalWeaponIKMLHipFast"' in node(graph,'NormalWeaponIK')
assert '#Var MovementLabHipFastAim float 0 0 1 ""' in (SOURCE/'WorkspacePatches/player_main.agr').read_text()
for name in ('MovementLabAltADS.c','MovementLabWeaponSway.c','MovementLabHipAimView.c'):
 assert (SOURCE/'StartGateSource/Scripts/4_World'/name).read_bytes()==(ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision46/StartGateSource/Scripts/4_World'/name).read_bytes()
cpp=r'''
#include <cassert>
#include <string>
#include <iostream>
struct Probe;
struct Game{Probe* player=nullptr;bool multi=false;Probe* GetPlayer(){return player;}bool IsMultiplayer(){return multi;}}game;
Game* GetGame(){return &game;}struct MovementLabStartGate{inline static bool Enabled=true;};
struct Anim{int BindVariableFloat(const char* n){assert(std::string(n)=="MovementLabHipFastAim");return 47;}};
struct Item{bool weapon=true;bool IsWeapon(){return weapon;}};
struct Input{bool free=false,tracking=false;bool CameraIsFreeLook(){return free;}bool CameraIsTracking(){return tracking;}};
struct Manager{bool running=false;bool IsRunning(){return running;}};
struct Probe{int m_MovementLabHipFastAimVar=-1;bool alive=true,unconscious=false,raised=true,third=false,iron=false,optics=false,lift=false,blocked=false,hasItem=true,hasInput=true,hasMove=true,hasManager=true;Anim anim;Item item;Input input;Manager manager;float selected=-1;
 Anim* GetAnimInterface(){return &anim;}Item* GetItemInHands(){return hasItem?&item:nullptr;}Input* GetInputController(){return hasInput?&input:nullptr;}Manager* GetWeaponManager(){return hasManager?&manager:nullptr;}void* GetCommand_Move(){return hasMove?this:nullptr;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}bool IsRaised(){return raised;}bool IsInThirdPerson(){return third;}bool IsInIronsights(){return iron;}bool IsInOptics(){return optics;}bool IsLiftWeapon(){return lift;}bool IsWeaponObstructionBlockingADS(){return blocked;}void AnimSetFloat(int id,float x){assert(id==47);selected=x;}
'''+method+r'''
};
int main(){
 for(int reason=-1;reason<18;reason++){
  Probe p,other;game={};game.player=&p;MovementLabStartGate::Enabled=true;
  if(reason==0)MovementLabStartGate::Enabled=false;if(reason==1)game.multi=true;if(reason==2)game.player=&other;if(reason==3)p.alive=false;if(reason==4)p.unconscious=true;if(reason==5)p.raised=false;if(reason==6)p.third=true;if(reason==7)p.iron=true;if(reason==8)p.optics=true;if(reason==9)p.input.free=true;if(reason==10)p.input.tracking=true;if(reason==11)p.hasItem=false;if(reason==12)p.item.weapon=false;if(reason==13)p.hasInput=false;if(reason==14)p.hasMove=false;if(reason==15)p.hasManager=false;if(reason==16)p.lift=true;if(reason==17)p.manager.running=true;
  p.MovementLabUpdateHipAimResponse();assert(p.selected==(reason<0?1:0));
 }
 {Probe p;game={};game.player=&p;p.MovementLabUpdateHipAimResponse();assert(p.selected==1);p.iron=true;p.MovementLabUpdateHipAimResponse();assert(p.selected==0);p.iron=false;p.MovementLabUpdateHipAimResponse();assert(p.selected==1);p.raised=false;p.MovementLabUpdateHipAimResponse();assert(p.selected==0);}
 std::cout<<"Actual response gate selects experimental IK only firstpersonhip; nativeIK chain exact, altered numeric pair isolated. Prior camera/sway/ADS modules unchanged. Native parameter meaning and speed improvement require gameplay test.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-hip-response-') as d:
 p=Path(d);(p/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
