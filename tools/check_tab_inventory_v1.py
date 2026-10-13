"""Execute skin logic with native GUI mocks; Enforce/rendering require DayZDiag."""
from pathlib import Path
import re, subprocess, tempfile, struct
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'inventory-ui-test/MovementLabTABInventoryTest_v1'
BASE=ROOT/'hud-icons-test/MovementLabHUDIcons_v2'
for folder in ('StartGateSource','WorkspacePatches','Missions'):
    for p in (BASE/folder).rglob('*'):
        if p.is_file():assert p.read_bytes()==(SOURCE/folder/p.relative_to(BASE/folder)).read_bytes(),p
source=(SOURCE/'InventoryUISource/Scripts/5_Mission/MovementLabInventorySkin.c').read_text()
assert not any(word in source for word in ('SetUV','CreatePlayer','CreateObject','ObjectDelete','PredictiveTake','SetQuantity(','ServerSetAmmo','SetVelocity','OverrideMovement','AddItemToCargo','SetCargoSize'))
sdk=Path('/tmp/dayz-script-diff/scripts')
names={
 'CargoContainer':('5_mission/gui/inventorynew/containeditems/cargocontainer.c', [('SetEntity','EntityAI item, int cargo_index = 0, bool immedUpdate = true'),('UpdateHeaderText',''),('UpdateInterval','')]),
 'ClosableHeader':('5_mission/gui/inventorynew/containeditems/headers/closableheader.c',[('SetName','string name')]),
 'Icon':('5_mission/gui/inventorynew/containeditems/icon.c',[('UpdateInterval','')])}
for cls,(path,methods) in names.items():
    text=(sdk/path).read_text()
    for method,args in methods:
        pattern=r'void\s+'+method+r'\s*\(\s*'+re.escape(args).replace(r'\ ',r'\s*')+r'\s*\)'
        assert re.search(pattern,text), (cls,method)
header=(sdk/'5_mission/gui/inventorynew/containeditems/headers/closableheader.c').read_text()
for method in ('OnDragHeader','OnDropHeader','MouseEnter','MouseLeave'):assert method+'(' in header or method+' (' in header
for resource in ('cell.paa','header.paa'):
    b=(SOURCE/'InventoryUISource/GUI/Textures'/resource).read_bytes();assert struct.unpack_from('<H',b)[0]==0xff05
# C++ mirrors native base construction for modded constructors; actual geometry
# and skin code follows. It cannot substitute for Enforce's compiler/type system.
pieces=re.split(r'(?=modded class )',source)
translated=[]
mapping={'CargoContainerRow':'BaseCargoContainerRow','Icon':'BaseIcon','ClosableHeader':'BaseClosableHeader','CargoContainer':'BaseCargoContainer'}
for piece in pieces:
    match=re.search(r'modded class (\w+)',piece)
    if match:
        cls=match[1];base=mapping[cls]
        piece=piece.replace('modded class '+cls, 'struct '+cls+':'+base)
        piece=piece.replace('super.',base+'::')
        if cls=='CargoContainer':
            piece=piece.replace('{\n    protected bool', '{\n    using BaseCargoContainer::BaseCargoContainer;\n    static CargoContainer* Cast(LayoutHolder* p){return dynamic_cast<CargoContainer*>(p);}\n    protected bool',1)
        if cls=='ClosableHeader':
            piece=piece.replace('{\n    void ClosableHeader', '{\n    static ClosableHeader* Cast(Header* p){return dynamic_cast<ClosableHeader*>(p);}\n    void ClosableHeader',1)
    else:piece=piece.replace('class MovementLabInventorySkin','struct MovementLabInventorySkin')
    piece=piece.replace('protected ','').replace('override ','').replace('m_RootWidget','root')
    # Enforce resolves class names regardless of file order. Use the native base
    # cast when the new CargoContainer declaration occurs later in C++.
    piece=piece.replace('CargoContainer.Cast(parent)','BaseCargoContainer::Cast(parent)')
    for typ in ('Widget','ImageWidget','TextWidget','ItemPreviewWidget','EntityAI','PlayerBase','Header','Container','LayoutHolder','ClosableHeader','HandsPreview'):
        piece=re.sub(r'\b'+typ+r' (\w+)',typ+r'* \1',piece)
        piece=re.sub(r'\b'+typ+r'\.',typ+'::',piece)
    piece=piece.replace('WidgetFlags flags','int flags').replace('WidgetFlags.','WidgetFlags::').replace('Math.','Math::').replace('MovementLabInventorySkin.','MovementLabInventorySkin::').replace('WidgetEventHandler.','WidgetEventHandler::').replace('QuantityConversions.','QuantityConversions::')
    for name in ('GetGame()','GetWorkspace()','GetInstance()','GetParent()','GetRootWidget()','GetMainWidget()','parent','item','player','owner','cargoOwner','header','oldPreview','headerPreview','GetHeader()','root','image','label','m_QuantityItem','m_MovementLabItemName','m_MovementLabNamedItem','m_Obj','m_PanelWidget','m_HeaderText','m_MovementLabGearColumn','m_MovementLabGearName','m_MovementLabGearCapacity','m_MovementLabGearPreview','m_Entity','m_MovementLabBoundGear'):
        piece=piece.replace(name+'.',name+'->')
    piece=piece.replace('translated.Length()','translated.size()').replace('translated.Substring(','translated.substr(')
    piece=piece.replace('"Icon" + themeColumn','"Icon" + std::to_string(themeColumn)').replace('"" + occupied + " / " + maximum','std::to_string(occupied)+" / "+std::to_string(maximum)')
    piece=re.sub(r'\bnull\b','nullptr',piece)
    piece=re.sub(r'^\s*Print\([^\n]*\);','',piece,flags=re.M)
    piece=re.sub(r'\bbool (m_MovementLab\w+);',r'bool \1=false;',piece)
    piece=re.sub(r'\bfloat (m_MovementLab\w+);',r'float \1=0;',piece)
    piece=re.sub(r'\b(Widget|ImageWidget|TextWidget|ItemPreviewWidget|EntityAI)\* (m_MovementLab\w+);',r'\1* \2=nullptr;',piece)
    if match:
        cls=match[1]
        if cls=='CargoContainerRow':piece=piece.replace('void CargoContainerRow(LayoutHolder* parent)', 'CargoContainerRow(LayoutHolder* parent):BaseCargoContainerRow(parent)')
        if cls=='Icon':piece=piece.replace('void Icon(LayoutHolder* parent, bool hands_icon = false)', 'Icon(LayoutHolder* parent, bool hands_icon = false):BaseIcon(parent,hands_icon)')
        if cls=='ClosableHeader':piece=piece.replace('void ClosableHeader(LayoutHolder* parent, string function_name)', 'ClosableHeader(LayoutHolder* parent, string function_name):BaseClosableHeader(parent,function_name)')
    # End the class before #endif (the last section wraps the full client module).
    at=piece.rfind('}')
    piece=piece[:at+1]+';'+piece[at+1:]
    translated.append(piece)
mock=(ROOT/'tools/fixtures/movementlab_inventory_skin_mock.cpp').read_text()
mock=mock.replace('struct BaseCargoContainer:Container{','struct BaseCargoContainer:Container{static BaseCargoContainer* Cast(LayoutHolder* p){return dynamic_cast<BaseCargoContainer*>(p);}')
tests=r'''
int main(){
 PlayerBase player;game.player=&player;EntityAI vest;vest.owner=&player;player.vest=&vest;
 Widget pane;pane.flags=WidgetFlags::EXACTPOS|WidgetFlags::EXACTSIZE;pane.x=10;pane.y=20;pane.w=500;pane.h=300;Container owner;owner.root=&pane;ClosableHeader header(&owner,"close");owner.header=&header;
 CargoContainer cargo(&owner);cargo.SetEntity(&vest);assert(cargo.m_MovementLabSidebar && cargo.nativeSets==1);assert(std::abs(cargo.measuredX-120)<.01f && std::abs(cargo.cellSize-39)<.01f);assert(cargo.m_MovementLabGearPreview->item==&vest);assert(cargo.m_MovementLabGearCapacity->text=="6 / 40");assert(header.m_HeaderText->text=="Chest Rig");
 float gx,gy;cargo.root->GetScreenPos(gx,gy);int hitColumn=int((gx+3*cargo.cellSize+1-cargo.measuredX)/cargo.cellSize);assert(hitColumn==3);float px,py;cargo.m_MovementLabGearColumn->GetScreenPos(px,py);assert(std::abs(px-pane.x)<.01f);
 auto callbacks=WidgetEventHandler::GetInstance()->binds.size();assert(callbacks==6);int itemAssignments=cargo.m_MovementLabGearPreview->assignments;for(int i=0;i<100;i++)cargo.UpdateInterval();assert(cargo.nativeUpdates==100 && cargo.m_MovementLabGearPreview->assignments==itemAssignments && WidgetEventHandler::GetInstance()->binds.size()==callbacks);
 vest.count=13;cargo.UpdateInterval();assert(cargo.m_MovementLabGearCapacity->text=="13 / 40");vest.max=50;cargo.UpdateInterval();assert(cargo.m_MovementLabGearCapacity->text=="13 / 50");vest.view=1;cargo.UpdateInterval();assert(cargo.m_MovementLabGearPreview->view==1 && cargo.m_MovementLabGearPreview->assignments==itemAssignments+1);
 CargoContainerRow row(&cargo);for(int i=0;i<10;i++){auto c=row.GetMainWidget()->FindAnyWidget("Icon"+std::to_string(i));auto bg=ImageWidget::Cast(c->FindAnyWidget("MovementLabCell"));assert(bg && (bg->flags&WidgetFlags::IGNOREPOINTER));}
 Icon item(&cargo);item.m_Obj=&vest;item.UpdateInterval();assert(item.nativeUpdates==1 && item.m_MovementLabItemName->visible && !item.m_MovementLabItemName->text.empty());assert(vest.count==13&&vest.max==50);vest.magazine=true;item.UpdateInterval();assert(item.m_QuantityItem->text=="13 / 50");vest.magazine=false;item.m_IsDragged=true;item.UpdateInterval();assert(!item.m_MovementLabItemName->visible);
 CargoContainer exact(&owner);exact.root->flags|=WidgetFlags::HEXACTPOS|WidgetFlags::HEXACTSIZE;exact.root->w=500;exact.SetEntity(&vest);assert(exact.m_MovementLabSidebar && exact.root->flags&WidgetFlags::HEXACTSIZE && std::abs(exact.cellSize-39)<.01f);
 Widget small;small.flags=WidgetFlags::EXACTSIZE;small.w=200;small.h=200;Container smallOwner;smallOwner.root=&small;CargoContainer narrow(&smallOwner);narrow.SetEntity(&vest);assert(!narrow.m_MovementLabSidebar && !narrow.m_MovementLabGearPreview && narrow.nativeSets==1);
 Widget locked;locked.flags=WidgetFlags::EXACTSIZE;locked.w=500;locked.h=300;locked.forceChildOrigin=true;Container lockedOwner;lockedOwner.root=&locked;CargoContainer fallback(&lockedOwner);fallback.SetEntity(&vest);assert(!fallback.m_MovementLabSidebar && fallback.root->w==1 && fallback.root->x==0);
 EntityAI nearby;CargoContainer vicinity(&owner);vicinity.SetEntity(&nearby);assert(!vicinity.m_MovementLabSidebar && vicinity.cellSize==50);
 assert(MovementLabInventorySkin::FitName("A long weapon name that should fit",30)=="A ...");
 std::cout<<"Actual TAB skin: grid inset BEFORE native measurements, matching drop-column geometry, real item/quantity references, cached preview updates, native header callbacks, no pointer-blocking decor, cell labels, narrow/spacer/vicinity fallbacks passed. Native UI rendering/dragging not executed.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='movementlab-tab-ui-') as d:
    p=Path(d);(p/'test.cpp').write_text(mock+'\n'+'\n'.join(translated)+tests)
    subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True)
print('Native method names/signatures checked; previous movement/HUD/mission files byte-identical.')
