#include <cassert>
#include <algorithm>
#include <string>
#include <vector>
#include <iostream>
struct Math{static float Clamp(float v,float lo,float hi){return std::clamp(v,lo,hi);}static float Max(float a,float b){return std::max(a,b);}};
struct WidgetFlags{static constexpr int VISIBLE=1,HEXACTPOS=2,VEXACTPOS=4,HEXACTSIZE=8,VEXACTSIZE=16,IGNOREPOINTER=32,NOFOCUS=64;};
constexpr int FrameWidgetTypeID=1,TextWidgetTypeID=2;
int ARGB(int a,int r,int g,int b){return (unsigned(a)<<24)|(r<<16)|(g<<8)|b;}
struct Widget{std::string name;bool visible=true;float x=0,y=0,w=0,h=0;int color=0;Widget* parent=nullptr;std::vector<Widget*> children;virtual ~Widget(){}void SetName(std::string n){name=n;}Widget* FindAnyWidget(std::string n){if(name==n)return this;for(auto c:children){if(auto found=c->FindAnyWidget(n))return found;}return nullptr;}bool IsVisibleHierarchy(){return visible&&(!parent||parent->IsVisibleHierarchy());}void Show(bool b){visible=b;}void SetColor(int c){color=c;}void GetScreenPos(float& a,float& b){a=x;b=y;}void GetScreenSize(float& a,float& b){a=w;b=h;}void SetScreenPos(float a,float b){x=a;y=b;}};
struct TextWidget:Widget{std::string text;static TextWidget* Cast(Widget* w){return dynamic_cast<TextWidget*>(w);}void SetText(std::string s){text=s;}void SetTextExactSize(int){}void SetOutline(int){}void SetBold(bool){}};
struct Workspace{bool failText=false;Widget* CreateWidget(int type,int x,int y,int w,int h,int,int color,int,Widget* parent){if(failText&&type==TextWidgetTypeID)return nullptr;Widget* v=type==TextWidgetTypeID?new TextWidget:new Widget;v->x=x;v->y=y;v->w=w;v->h=h;v->color=color;v->parent=parent;parent->children.push_back(v);return v;}};
struct PlayerBase{bool alive=true,unconscious=false,automatic=false;int selected=1;std::string mode="WALK";static PlayerBase* Cast(PlayerBase* p){return p;}bool IsAlive(){return alive;}bool IsUnconscious(){return unconscious;}void MovementLabGetHUDSpeed(int& l,std::string& m,bool& a){l=selected;m=mode;a=automatic;}};
struct Game{PlayerBase* player=nullptr;Workspace workspace;PlayerBase* GetPlayer(){return player;}Workspace* GetWorkspace(){return &workspace;}}game;Game* GetGame(){return &game;}
struct MovementLabStartGate{inline static bool Enabled=true;};
struct BaseHUD{Widget* m_HudPanelWidget=nullptr;Widget* m_Presence=nullptr;void Init(Widget* w){m_HudPanelWidget=w;m_Presence=w->FindAnyWidget("PresencePanel");}void Update(float){}};
