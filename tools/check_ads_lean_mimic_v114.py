"""Read-only checks of replay integration, lifecycle, keys and pose math.
Native DayZ compilation and playback are deliberately not claimed.
"""
from pathlib import Path
import sys,json,re,math
import numpy as np
from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v113';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v114'
world=b/'LogicSource/Scripts/4_World';player=(world/'MLADSLeanPlayer.c').read_text();controller=(world/'MLMimic114.c').read_text();keys=(b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
for p in list((b/'LogicSource').rglob('*.c'))+list((b/'Missions').rglob('*.c')):
 text=p.read_text();assert 'NotificationSystem.' not in text,p
 # Lexical brace balance with comments/quoted strings removed.
 text=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/','',text)
 depth=0
 for c in text:
  if c=='{':depth+=1
  if c=='}':depth-=1
  assert depth>=0,p
 assert depth==0,p
assert set(re.findall(r'KeyCode\.(KC_F\d+)',keys))=={'KC_F8'}
assert 'm_ML114LeftCtrl || m_ML114RightCtrl' in keys
assert 'ML49' not in keys
assert 'm_ML114LReset = true' in keys and '!m_ML114LReset &&' in keys
hold=keys[keys.index('if (!m_ML114LReset &&'):]
assert hold.index('m_ML114LConsumed = true')<hold.index('m_ML114LReset = true')
assert 'bool tap = m_ML114LDown && !m_ML114LConsumed' in keys
assert 'KeyCode.KC_PERIOD && (m_ML114LeftShift || m_ML114RightShift)' in keys
assert 'GetGame().GetUIManager().GetMenu()' in keys
# No loop/controller writes the selected player input or takes player selection.
assert 'SelectPlayer' not in controller
assert 'source.Set' not in controller and 'source.Override' not in controller
assert controller.count('Actor.SetPosition(Home)')==3
assert 'Frames.Count() >= 6000' in controller
assert 'm_SampleElapsed >= 0.05' in controller
assert 'Frames.Count() < 2' in controller
assert 'm_PlayTime = Math.ModFloat(m_PlayTime, duration)' in controller
assert 'Actor.ML114SetMimicFrame(frame, position, heading)' in controller
# Playback cannot enter the original patrol input logic.
i=player.index('protected void MLADSLeanUpdateDemoInput');j=player.index(' override void CommandHandler',i)
method=player[i:j];assert method.index('ML114UpdateMimicInput();')<method.index('vector offset = GetPosition()')
assert re.search(r'if \(m_ML114Mimic\)\s*\{\s*ML114UpdateMimicInput\(\);\s*return;',method)
assert 'GetGame().GetPlayer() == this' in player[player.index('protected void ML114UpdateMimicInput'):i]
# Absolute pose graph values are written only after native actor processing.
start=player.index('super.CommandHandler(');end=player.index(' // Read-only camera weight')
for match in re.finditer(r'AnimSetFloat\(m_MLADSLeanDemoAim\w*, m_ML114Frame',player):assert start<match.start()<end
assert '(!m_ML114Mimic || raised)' in player
assert 'move.ForceStance(m_ML114Frame.Stance)' in player
assert 'GetCommand_Move().ForceStance(-1)' in player
assert 'SurvivorF_Eva' in mission
assert 'm_MLADSLeanTargetPosition + npcRight * 10' in mission
assert 'corpse == m_ML114Woman' in mission
assert 'CallLater(ML114SpawnWoman, 1000, false)' in mission
assert '.Remove(ML114SpawnWoman)' in mission
assert 'm_ML114Woman.ML114DisableMimic()' in mission
assert 'm_MLADSLeanNPC.MLADSLeanStartDemo()' in mission
# Check coordinate transforms for round trips and the own-right placement over
# a full turn, including mirrored NPC/player facing directions.
for yaw in np.linspace(-180,180,73):
 t=math.radians(yaw);c,s=math.cos(t),math.sin(t)
 matrix=np.array([[c,0,s],[0,1,0],[-s,0,c]])
 for v in [np.array([1.,2.,3.]),np.array([-.05,0,.2])]:assert np.max(abs(matrix.T@(matrix@v)-v))<1e-12
 forward=matrix@np.array([0.,0.,1.]);right=np.array([forward[2],0,-forward[0]])
 assert abs(np.linalg.norm(right*10)-10)<1e-12 and abs(right@forward)<1e-12
 assert np.max(abs(right-matrix@np.array([1.,0.,0.])))<1e-12
# Only the intended 18 arm-node coefficients differ from previous graph.
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
changed=[name for name,node in old.items() if not name.startswith('{') and new[name]!=node]
assert len(changed)==18 and all(name.startswith('ML32_ReferenceHold_') for name in changed),changed
pose=json.loads((b/'Left-Weapon-Shift-v114.json').read_text());reference=json.loads((b/'Left-Shoulder-Height-v101.json').read_text())
for hand in ['LeftHand','RightHand']:
 current=np.array(pose['desired'][hand]);original=np.array(reference['desired'][hand]);assert np.max(abs(current[:3,3]-original[:3,3]-[0,0,.05]))<1e-8
 assert np.max(abs(current[:3,:3]-original[:3,:3]))<1e-8
assert 'float leftOutward = -0.34202014' in player and 'float outward = 0.70710678' in player
assert (a/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes()==(world/'MLADSLeanCamera.c').read_bytes()
launch=(b/'Launch-Test.ps1').read_text();assert '$mods = @($cf,$aj,$workspace,$logic)' in launch
# Confirm each newly used native API against the available official SDK.
sdk=Path('/tmp/dayz-lean-sdk/scripts/3_game/human.c').read_text()
for api in ['SetDirectionFilterModifier','SetRunSprintFilterModifier','ForceStance','GetCurrentMovementSpeed','GetCurrentMovementAngle','GetBaseAimingAngleUD','OverrideRaise']:
 assert api in sdk,api
assert 'Math.ModFloat' in controller
print('PASS: silent keys/hold-reset gating, NPC-only playback route, cleanup/respawn, 73 coordinate orientations, 18 scoped hold changes, +5cm forward wrists, camera/CF/AJ retained; native compilation and replay untested.')
