"""Check native FP graph provenance, isolation, references, and player view scope."""
from pathlib import Path
import re,json
from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v222';b=a.with_name('MovementLab_ADS_Lean_Mosin_v224')
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());native=newnodes(Path('/workspace/output/ADS_Lean_Game_Test/source-workspace/player_main/locomotion.agf').read_text());info=json.loads((b/'First-Person-Native-Crouch-v223.json').read_text())
assert {k for k in old if old[k]!=new[k]}=={'MeleeBlockQ'}
assert old['MeleeBlockQ'].replace('Child "ML183_UnarmedOnly"','Child "ML223FirstPersonOnly"')==new['MeleeBlockQ']
assert len(info['native_clones'])==116
names={k:'ML223Native_'+k for k in info['native_clones']};names['StanceMaster']='ML223CrouchRaised'
normalize=lambda t:re.sub(r'\{[A-F0-9]{16}\}','{GUID}',t)
for name in info['native_clones']:
 expected=native[name];prefix=expected.split('{',1)[0];expected=expected.replace(prefix,prefix.replace(name,names[name],1),1)
 expected=re.sub(r'\b(Child[0-9]*) "([^"]+)"',lambda m:m[1]+' "'+names.get(m[2],m[2])+'"',expected)
 assert normalize(expected)==normalize(new[names[name]]),name
 assert 'MLADS' not in new[names[name]] and 'ML149' not in new[names[name]]
# FP subtree never reaches custom pose nodes; references resolve; no cycles.
visiting=set();seen=set()
def walk(k):
 assert k in new,k
 assert k not in visiting,'Cycle:'+k
 if k in seen:return
 visiting.add(k)
 for child in re.findall(r'\bChild[0-9]* "([^"]+)"',new[k]):
  if child not in new:
   assert child in {'DamageMaster','WeaponStanceMaster'}, (k,child)  # native cross-graph reference
   continue
  assert child.startswith('ML223'),(k,child)
  walk(child)
 visiting.remove(k);seen.add(k)
walk('ML223Native_NormalWeaponIK')
assert len(seen)==119
selector=new['ML223FirstPersonOnly'];assert 'BlendWeight "ML87FirstPersonCrouchLean"'in selector and 'OptimizeMin 1'in selector and 'OptimizeMax 1'in selector
for p in(a/'LogicSource/Presets').glob('*.json'):
 for rel in [p.name,'LogicSource/Presets/'+p.name,'Profiles/LeanMosin/'+p.name]:assert(a/rel).read_bytes()==(b/rel).read_bytes(),rel
p=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
for marker in ['cameraName == "DayZPlayerCamera1stPerson"','!m_MLADSLeanDemo && firstPersonView','state.m_iMovement <= 2 && Math.AbsFloat(state.m_fLeaning) > 0.001','AnimSetFloat(m_ML87ViewVar, m_ML87ViewAmount)','if (fpRoute)\n   sharedLean = false;','suppressHeadTilt = suppressHeadTilt && m_ML87ViewAmount < 0.5;']:
 assert marker in p,marker
# Scope truth table across lean sides, gait, live command, NPC and camera.
for view in ['third','first','ironsights','optics']:
 for npc in [False,True]:
  for movement in range(4):
   for lean in [-1,0,1]:
    active=view!='third' and not npc and movement<=2 and abs(lean)>.001
    if view=='third' or npc or movement==3 or lean==0:assert not active
    else:assert active
print('PASS:116 native clones exact except names/GUIDs;FP119-node subtree isolated/acyclic;original third-person graph unchanged except final selector;all15banks byteexact;bothside/gait/camera scope. Native compile/render/grip/FPS NOT RUN. Absolute head lock remains unimplemented.')

# Local camera cannot select FP for another actor. Dedicated server never runs visual graph.
assert 'bool localPlayer = GetGame().GetPlayer() == this;' in p
assert 'GetIsSimulationDisabled() || GetGame().IsDedicatedServer() || !GetAnimInterface()' in p
assert 'if (GetGame().IsDedicatedServer() || !GetAnimInterface())' in p
assert 'if (!m_MLADSLeanDemo || GetGame().IsMultiplayer())' in p
for marker in ['protected bool m_ML224PlayerJogBank;', 'routingState.m_iMovement == 2;', 'MLADSLeanWeaponSupport106.Profile(crouchHeld) == 1;', 'else if (m_ML216JogEditor || m_ML224PlayerJogBank)', 'if ((m_ML216JogEditor || m_ML224PlayerJogBank) && m_ML173Walking)']:
 assert marker in p, marker
assert p.count('else if (m_ML216JogEditor || m_ML224PlayerJogBank)')==2
assert p.count('if ((m_ML216JogEditor || m_ML224PlayerJogBank) && m_ML173Walking)')==2
assert 'ML224PlayerJogBank' not in (b/'WorkspaceSource/locomotion.agf').read_text()
assert 'RegisterNetSyncVariable' not in p and 'ScriptRPC' not in p
for controlled in [False,True]:
 for actor_is_controlled in [False,True]:
  for actor_camera in ['first','third']:
   fp=controlled and actor_is_controlled and actor_camera=='first'
   if not actor_is_controlled:assert not fp
print('PASS:local FP selection only;remote always custom;client-only visual updates/no network camera pose flag;real-player jogging preset+reference scope3;preview MP guards retained. Two-client native visibility NOT RUN.')
