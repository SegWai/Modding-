from pathlib import Path
import re,subprocess
p=Path('/workspace/Modding-/ctrl-mode-test/MovementLabAim_Linked_v2_Revision14')
s=(p/'StartGateSource/Scripts/4_World/MovementLabTestStamina.c').read_text().split('modded class PlayerBase')[0]
s=s.replace('modded class StaminaHandler','struct TestStamina : NativeStamina').replace('override protected ','').replace('override ','').replace('super.','NativeStamina::').replace('MovementLabStartGate.','MovementLabStartGate::').replace('CfgGameplayHandler.','CfgGameplayHandler::').replace('GetGame().','GetGame()->')+';'
cpp='''#include <cassert>
struct MovementLabStartGate{inline static bool Enabled=true;};
struct CfgGameplayHandler{static float GetStaminaMax(){return100;} }; 
'''.replace('return100','return 100')+'''
struct Game{bool multi=false;bool IsMultiplayer(){return multi;}} game; Game* GetGame(){return &game;}
enum EStaminaModifiers{TEST};
struct NativeStamina{float m_Stamina=20,m_StaminaCap=20,m_StaminaCapSynced=20,m_StaminaDepletion=10,m_StaminaDelta=-10;void RecalculateStaminaCap(){m_StaminaCap=20;} void ProcessStaminaChanges(float dt,bool){m_Stamina+=m_StaminaDelta*dt-m_StaminaDepletion;}void DepleteStaminaEx(EStaminaModifiers,float=-1,float=1){m_StaminaDepletion+=10;}};
'''+s+'''
int main(){TestStamina s;s.RecalculateStaminaCap();assert(s.m_StaminaCap==100);for(int i=0;i<600;i++){s.DepleteStaminaEx(TEST);s.ProcessStaminaChanges(.1,true);assert(s.m_Stamina==100 && s.m_StaminaDepletion==0);}game.multi=true;s.RecalculateStaminaCap();assert(s.m_StaminaCap==20);s.DepleteStaminaEx(TEST);assert(s.m_StaminaDepletion==10);}
'''
Path('/tmp/stamina14.cpp').write_text(cpp);subprocess.run(['g++','-std=c++17','/tmp/stamina14.cpp','-o','/tmp/stamina14'],check=True);subprocess.run(['/tmp/stamina14'],check=True)
mission=(p/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text();assert '4610 0 10180' in mission
for name in ['TacticalShirt_Black','CargoPants_Black','TacticalGloves_Black','BallisticHelmet_Black','BalaclavaMask_Black','PlateCarrierVest_Black','PlateCarrierPouches_Black','PlateCarrierHolster_Black']:assert name in mission
assert 'itemsCargoSize[] = {7,6}' in (p/'StartGateSource/config.cpp').read_text()
print('Translated stamina logic: offline full cap/no depletion over600 updates, multiplayer native fallback; black loadout, smaller pack and NWAF spawn checked. Native spawn/compile pending.')
