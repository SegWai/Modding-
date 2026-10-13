"""Exercise actual Enforce controller translated to C++; not a native renderer test."""
from pathlib import Path
import ast, re, subprocess, tempfile, json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'viewmodel-prototype/MovementLabArmsOnlyTest_v2'
prior=ROOT/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision49'
for p in (prior/'StartGateSource/Scripts').rglob('*.c'):
    assert p.read_bytes()==(SOURCE/'StartGateSource/Scripts'/p.relative_to(prior/'StartGateSource/Scripts')).read_bytes(),p
mission=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
native=(prior/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
# Mission braking/inputs are unchanged; only the existing extra F9/F10 observer
# keys and loadout differ. World controller regressions run separately.
assert mission[mission.index('    protected EntityAI MovementLabAddItem'):mission.index('    protected void MovementLabEquipNativeFallback')]==native[native.index('    protected EntityAI MovementLabAddItem'):native.index('    protected void MovementLabEquipTestPlayer')]
assert 'testAmmoTypes' not in mission and 'Ammo_556x45' not in mission
assert 'snafuSpareIndex < 5' in mission and 'ServerSetAmmoMax' in mission
model=json.loads((SOURCE/'ModelSource/model-validation.json').read_text())
assert model['arms_vertices']==4522 and model['faces']==7974
assert (SOURCE/'StartGateSource/Models/arms_only.p3d').read_bytes()==(SOURCE/'ModelSource/arms_only.p3d').read_bytes()
assert (SOURCE/'StartGateSource/Models/arms_only.p3d').read_bytes()[:12]==b'MLOD\x01\x01\0\0\x01\0\0\0'
s=(SOURCE/'StartGateSource/Scripts/5_Mission/MovementLabViewmodelUI.c').read_text()
assert not any(x in s for x in ('PlayerPreviewWidget','AnimSet','GetOrientation','SetTransform','SetOrientation','OverrideMovement','CreatePlayer','StartAction','GetCurrentCameraTransform'))
sdk=Path('/tmp/dayz-script-diff/scripts/3_game/gameplay.c').read_text()
for name in ('SetItem','GetItem','SetView','SetModelOrientation','SetModelPosition'):
    assert name+'(' in sdk
layout=(SOURCE/'StartGateSource/GUI/MovementLabViewmodel.layout').read_text()
assert layout.count('ItemPreviewWidgetClass')==2 and 'PlayerPreviewWidgetClass' not in layout
code=s[:s.index('modded class IngameHud')]
code=code.replace('class MovementLabViewmodelUI','struct MovementLabViewmodelUI').replace('protected ','')
code=code.replace('static ref MovementLabViewmodelUI s_Instance;', 'inline static MovementLabViewmodelUI* s_Instance=nullptr;')
code=code.replace('ref array<EntityAI> m_HiddenClothes = new array<EntityAI>();','EntityArray m_HiddenClothes;')
code=code.replace('void ~MovementLabViewmodelUI()', '~MovementLabViewmodelUI()')
for typ in ('Widget','ItemPreviewWidget','PlayerBase','EntityAI','HumanCommandWeapons','MovementLabViewmodelUI'):
    code=re.sub(r'\b'+typ+r' (\w+)',typ+r'* \1',code)
code=code.replace('foreach (EntityAI* clothing : m_HiddenClothes)', 'for (EntityAI* clothing : m_HiddenClothes.vals)')
code=re.sub(r'\bnull\b','nullptr',code).replace('        s_Instance = nullptr;', '        delete s_Instance; s_Instance = nullptr;')
for name in ('MovementLabStartGate','WidgetFlags','Camera','PlayerBase','ItemPreviewWidget','EntityAI'):
    code=code.replace(name+'.',name+'::')
for name in ('GetGame()','GetInput()','GetUIManager()','GetMission()','GetWorkspace()','m_Root','m_ArmsPreview','m_GunPreview','m_ArmsItem','instance','m_HiddenPlayer','player','clothing','held','GetItemAccessor()','GetItemInHands()','GetInputController()','GetWeaponManager()','realWeapons','s_Instance'):
    code=code.replace(name+'.',name+'->')
code=re.sub(r'Print\([^\n]+\);','Print("trace");',code)
code=re.sub(r'\bbool (m_\w+);',r'bool \1=false;',code)
code=re.sub(r'\bint (m_\w+);',r'int \1=0;',code)
code=re.sub(r'\b(Widget|ItemPreviewWidget|PlayerBase|EntityAI)\* (m_\w+);',r'\1* \2=nullptr;',code)
code=re.sub(r'\bstring\b','std::string',code).rstrip()+';\n'
# Reuse native API mocks, replacing only the player-preview renderer and owned fixture.
tree=ast.parse((ROOT/'tools/check_viewmodel_prototype_v1.py').read_text())
prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets))
prefix=prefix.replace('#include <cassert>','#include <cassert>\n#include <array>\nusing vector=std::array<float,3>;\nconstexpr int ECE_LOCAL=1,ECE_KEEPHEIGHT=2,ECE_NOLIFETIME=4,ECE_NOPERSISTENCY_WORLD=8;')
prefix=prefix.replace('struct EntityAI{','struct EntityAI{static EntityAI* Cast(EntityAI* p){return p;} vector GetPosition(){return {0,100,0};}int GetViewIndex(){return 0;}bool simulationDisabled=false;void DisableSimulation(bool v){simulationDisabled=v;}')
a=prefix.index('struct PlayerPreviewWidget:');b=prefix.index('struct Workspace',a)
prefix=prefix[:a]+'''struct ItemPreviewWidget:Widget{EntityAI* item=nullptr;bool reject=false;int assignments=0;std::string orientation,position;float x=0,y=0,w=0,h=0;static ItemPreviewWidget* Cast(Widget* p){return dynamic_cast<ItemPreviewWidget*>(p);}void SetItem(EntityAI* p){item=reject?nullptr:p;assignments++;}EntityAI* GetItem(){return item;}void SetView(int){}void SetModelOrientation(std::string v){orientation=v;}void SetModelPosition(std::string v){position=v;}void SetPos(float a,float b){x=a;y=b;}void SetSize(float a,float b){w=a;h=b;}};
struct Root:Widget{ItemPreviewWidget arms,gun;bool child=true;Widget* FindAnyWidget(const char* n){if(!child)return nullptr;return std::string(n)=="MovementLabArmsPreview"?&arms:&gun;}};
'''+prefix[b:]
prefix=prefix.replace('struct Game{','struct Game{EntityAI fixture;bool spawnFail=false;int spawns=0,deletes=0;EntityAI* CreateObjectEx(const char* type,vector pos,int flags){assert(std::string(type)=="MovementLabArmsPreviewItem" && pos[1]==-900 && flags==15);spawns++;return spawnFail?nullptr:&fixture;}void ObjectDelete(EntityAI* p){assert(p==&fixture);deletes++;fixture.deleted=true;}')
main=r'''
int main(){
 {PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;Camera::external=false;
  {MovementLabViewmodelUI vm;vm.m_Enabled=true;vm.Update();assert(p.invisible && p.accessor.hidden);assert(game.workspace.root.visible && game.workspace.root.arms.item==&game.fixture && game.workspace.root.gun.item==&p.gun);assert(game.fixture.simulationDisabled);for(int i=0;i<100;i++)vm.Update();assert(game.spawns==1 && game.workspace.creates==1 && p.animWrites==0);vm.Stop();assert(!p.invisible && !p.accessor.hidden && !game.workspace.root.visible && game.workspace.root.gun.item==nullptr);}
  assert(game.deletes==1 && !p.gun.deleted && !p.deleted);}
 for(int exit=0;exit<13;exit++){PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;Camera::external=false;MovementLabViewmodelUI vm;vm.m_Enabled=true;vm.Update();assert(p.invisible);
  if(exit==0)p.iron=true;if(exit==1)p.optics=true;if(exit==2)p.third=true;if(exit==3)p.raised=false;if(exit==4)p.input.free=true;if(exit==5)p.manager.running=true;if(exit==6)p.weapons.action=1;if(exit==7)game.ui.menu=true;if(exit==8)p.alive=false;if(exit==9)p.unconscious=true;if(exit==10)game.multi=true;if(exit==11)Camera::external=true;if(exit==12)MovementLabStartGate::Enabled=false;vm.Update();assert(!p.invisible && !p.accessor.hidden && !game.workspace.root.visible && p.animWrites==0);}
 for(int fault=0;fault<4;fault++){PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;Camera::external=false;MovementLabViewmodelUI vm;vm.m_Enabled=true;if(fault==0)game.workspace.fail=true;if(fault==1)game.workspace.root.child=false;if(fault==2)game.spawnFail=true;if(fault==3)game.workspace.root.gun.reject=true;vm.Update();assert(!p.invisible && !p.accessor.hidden && !game.workspace.root.visible);}
 {PlayerBase p;game={};game.player=&p;MovementLabStartGate::Enabled=true;Camera::external=false;MovementLabViewmodelUI::Toggle();MovementLabViewmodelUI::Tick();assert(p.invisible);MovementLabViewmodelUI::CycleFrame();assert(game.workspace.root.gun.orientation=="0 90 0");MovementLabViewmodelUI::CycleFrame();assert(game.workspace.root.arms.x==.05f && game.workspace.root.gun.x==.5f);MovementLabViewmodelUI::Toggle();assert(!p.invisible);MovementLabViewmodelUI::Shutdown();assert(game.deletes==1 && !game.workspace.root.linked);}
 {PlayerBase p;game={};game.player=&p;MovementLabViewmodelUI vm;vm.m_Enabled=true;game.spawnFail=true;vm.Update();assert(!p.invisible && game.spawns==1);game.spawnFail=false;vm.m_WidgetAttempted=false;vm.Update();assert(p.invisible && game.spawns==2);}
 std::cout<<"Arms-only controller: fixture ownership/deletion, cached widgets, unchanged player animation, exit recovery, renderer failure fallbacks, framing and toggle passed. Native renderer not executed.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-arms-v2-') as d:
    p=Path(d);(p/'test.cpp').write_text(prefix+code+main)
    subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True)
print('Model/package source integrity and stable movement-script identity passed; SNAFU/runtime pixels pending.')
