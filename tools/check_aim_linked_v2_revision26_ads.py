from pathlib import Path
import re,subprocess,tempfile
root=Path(__file__).resolve().parents[1];p=root/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision26';s=(p/'StartGateSource/Scripts/4_World/MovementLabAltADS.c').read_text()
# Compare original native safety/optics body after its input declarations.
native=Path('/tmp/dayz-script-diff/scripts/4_world/entities/dayzplayerimplement.c').read_text();a=native.index('\tvoid HandleADS()');b=native.index('\n\tvoid HandleView()',a);n=native[a:b]
assert s[s.index('\t\tbool bADSToggle'):s.rindex('\n}')].strip()==n[n.index('\t\tbool bADSToggle'):].replace('bool isWeaponADS = hic.WeaponADS();','bool isWeaponADS = m_MovementLabAltADS;').strip()
# Execute actual toggle method with a minimal native interface.
a=s.index('    void MovementLabToggleAltADS()');b=s.index('\toverride void HandleADS()',a);method=s[a:b].replace('MovementLabStartGate.','MovementLabStartGate::').replace('GetGame().','GetGame()->').replace('GetInput().','GetInput()->').replace('GetUIManager().','GetUIManager()->').replace('GetItemInHands().','GetItemInHands()->')
cpp='''#include <cassert>
struct MovementLabStartGate{inline static bool Enabled=true;};struct Item{bool weapon=true;bool IsWeapon(){return weapon;}};struct UI{bool menu=false;bool GetMenu(){return menu;}};struct Input{bool focus=true;bool HasGameFocus(){return focus;}};struct Game{void* player=nullptr;bool multi=false;UI ui;Input input;bool IsMultiplayer(){return multi;}void* GetPlayer(){return player;}Input* GetInput(){return &input;}UI* GetUIManager(){return &ui;}}game;Game* GetGame(){return &game;}
struct Player{bool m_MovementLabAltADS=false,raised=true,alive=true,unconscious=false;Item item;bool IsRaised(){return raised;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}Item* GetItemInHands(){return &item;}
'''+method+'''};
int main(){Player p;game.player=&p;p.MovementLabToggleAltADS();assert(p.m_MovementLabAltADS);p.MovementLabToggleAltADS();assert(!p.m_MovementLabAltADS);p.raised=false;p.MovementLabToggleAltADS();assert(!p.m_MovementLabAltADS);p.raised=true;game.ui.menu=true;p.MovementLabToggleAltADS();assert(!p.m_MovementLabAltADS);game.ui.menu=false;game.multi=true;p.MovementLabToggleAltADS();assert(!p.m_MovementLabAltADS);}
'''
with tempfile.TemporaryDirectory() as d:
 q=Path(d);(q/'test.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17',str(q/'test.cpp'),'-o',str(q/'test')],check=True);subprocess.run([str(q/'test')],check=True)
mission=(p/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text();assert 'KeyCode.KC_LMENU' in mission and 'm_MovementLabAltTime <= 200' in mission
print('Actual ADS toggle tested on/off and lowered/menu/multiplayer guards. Native safety/optic body unchanged except input selection; Shift no longer requests ADS. Native camera/fire/Alt event runtime pending.')
