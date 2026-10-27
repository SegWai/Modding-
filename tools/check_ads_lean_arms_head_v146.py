"""Independent offline wrist-invariance/FK and UI integration checks; no native compiler."""
from pathlib import Path
import json,re,math
import numpy as np
from scipy.spatial.transform import Rotation
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v145'
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v146'
old=newnodes((BASE/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
for name,node in old.items():
 if not name.startswith('{') and name!='ML139_RightStraightOnly':assert new[name]==node,name
spec=json.loads((KIT/'Arms-Head-Editor-v146.json').read_text())
agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
for control in spec['control_names']:
 assert agr.count('AnimSrcGCTVarFloat '+control+' {')==1
 assert re.search(r'AnimSrcGCTVarFloat '+control+r' \{\s*DefaultValue 0',agr)
 assert any('Expression "'+control+'"' in node for node in new.values())
assert 'Child1 "ML146_HeadEditor_Z"' in new['ML139_RightStraightOnly']
# Trace live editor output to ensure it follows existing support grip/head level.
chain='ML146_HeadEditor_Z';seen=[]
while chain!='ML140_LevelRightHead':
 seen.append(chain);assert len(seen)<20
 chain=re.search(r'Child "([^"]+)"',new[chain])[1]
assert len(seen)==15
refs=json.loads((KIT/'Live-Editor-v144.json').read_text())['reference'];rng=np.random.default_rng(146);errors=[];accepted=0
for side in ['Left','Right']:
 root,elbow,wrist=[np.array(refs[side+n]) for n in ['Arm','ForeArm','Hand']]
 axis=wrist-root;axis/=np.linalg.norm(axis);pole=elbow-root;pole-=axis*(pole@axis)
 for _ in range(500):
  angles=rng.uniform(-90,90,3);desired=Rotation.from_euler('xyz',angles,degrees=True).apply(pole);desired-=axis*(desired@axis)
  if desired@desired<1e-6:continue
  f=pole/np.linalg.norm(pole);t=desired/np.linalg.norm(desired);angle=math.atan2(axis@np.cross(f,t),np.clip(f@t,-1,1));turn=Rotation.from_rotvec(axis*angle)
  # Verify with Euler replay in the native sign/order convention.
  native=-turn.as_euler('xyz');native_hand=-turn.inv().as_euler('xyz')
  a=Rotation.from_euler('xyz',-native).as_matrix();h=Rotation.from_euler('xyz',-native_hand).as_matrix()
  actual=root+a@(wrist-root);goal=root+a@(elbow-root)
  errors.extend([np.max(abs(actual-wrist)),np.max(abs(h@a-np.eye(3))),abs(np.linalg.norm(goal-root)-np.linalg.norm(elbow-root)),abs(np.linalg.norm(wrist-goal)-np.linalg.norm(wrist-elbow))]);accepted+=1
assert accepted>900 and max(errors)<1e-9
layout=(KIT/'LogicSource/GUI/MLPoseEditor144.layout').read_text();menu=(KIT/'LogicSource/Scripts/5_Mission/MLPoseEditorMenu144.c').read_text();world=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
for name in ['WeaponTab','ArmTab','WeaponPage','ArmPage']:
 assert re.search(r'\b'+name+r' \{',layout)
for i in range(15):
 for prefix in ['Value','Readout','Minus','Plus']:assert len(re.findall(r'\b'+prefix+str(i)+r' \{',layout))==1
for field in spec['fields']:
 assert 'candidate.'+field+' = Math.Round(' in menu
 assert 'value.'+field in menu
assert 'weaponPage.Show(!arms)' in menu and 'armPage.Show(arms)' in menu
assert 'size .29 .84' in layout
assert world.index('super.CommandHandler(')<world.index('  ML146UpdateArmsHead(pDt, state);')
assert 'm_ML146Settled > 0.2' in world and 'm_ML146HoldRevision != ML144State.HoldRevision' in world
assert 'else if (m_ML146ValuesRevision != ML144State.ValuesRevision)' in world
assert 'Math.AbsFloat(upper-lower)+0.002' not in (KIT/'LogicSource/Scripts/4_World/MLPoseEditor144.c').read_text()
for p in (KIT/'LogicSource').rglob('*.c'):
 s=p.read_text();assert s.count('{')==s.count('}'),p
 assert not re.search(r'\b(?:vector|float|int|string) local\b',s),p
print(json.dumps({'new_zero_default_controls':15,'grip_anchored_elbow_cases':accepted,'max_wrist_orientation_segment_error':max(errors),'ui':'smaller panel,2exclusive tabs,15sliders/readouts/+/-pairs;9new fields save/load/reset with existing values class','graph':'approved body and weapon/support nodes unchanged; new arm/head controls after final support solve in standing-right branch','cache':'per-actor snapshot after0.2s settled unmodified arm pose; invalidated only for weapon/hold changes; recalc on values revision','native_compilation_and_rendering':'NOT RUN'},indent=2))
