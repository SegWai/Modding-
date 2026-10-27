"""Offline both-side target/persistence-routing and final native muzzle wiring checks."""
from pathlib import Path
import json,re,math,sys
import numpy as np
from scipy.spatial.transform import Rotation
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];KIT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v147';BASE=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v146'
spec=json.loads((KIT/'Both-Sides-Editor-v147.json').read_text());right=json.loads((KIT/'Live-Editor-v144.json').read_text());rng=np.random.default_rng(147)
def coefficients(points,values):
 orientation=Rotation.from_euler('xyz',values[3:6],degrees=True).as_matrix();off=np.array([values[0],values[1]+5,values[2]])*.01;rt=points['RightHand']+off;targets={'Right':rt,'Left':rt+orientation@(points['LeftHand']-points['RightHand'])};out=[];error=0.
 def turn(a,b):
  a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);cross=np.cross(a,b);sn=np.linalg.norm(cross);cs=np.clip(a@b,-1,1)
  return np.eye(3) if sn<1e-6 else Rotation.from_rotvec(cross/sn*math.atan2(sn,cs)).as_matrix()
 for side in ['Left','Right']:
  root,e,w=[points[side+p] for p in ['Arm','ForeArm','Hand']];target=targets[side];upper=np.linalg.norm(e-root);lower=np.linalg.norm(w-e);distance=np.linalg.norm(target-root)
  if distance<=abs(upper-lower)+.002 or distance>=upper+lower-.002:return None
  axis=(target-root)/distance;along=(upper*upper-lower*lower+distance*distance)/(2*distance);radius=math.sqrt(max(0,upper*upper-along*along));pole=e-root;pole-=axis*(pole@axis)
  if pole@pole<1e-6:return None
  pole/=np.linalg.norm(pole);goal=root+axis*along+pole*radius;arm=turn(e-root,goal-root);fore=turn(arm@(w-e),target-goal);hand=orientation@(fore@arm).T
  actual=root+arm@(e-root)+fore@arm@(w-e);error=max(error,np.max(abs(actual-target)),np.max(abs(hand@fore@arm-orientation)));out.extend(np.concatenate([-Rotation.from_matrix(m).as_euler('xyz') for m in [arm,fore,hand]]))
 return np.array(out),error
reports={}
for name,source,default in [('left',spec['left_seed'],[0,-5,0,0,0,0]),('right',right['reference'],[5,-10,0,0,0,0])]:
 points={n:np.array(v) for n,v in source.items()};base=coefficients(points,default);assert base is not None
 expected=np.zeros(18) if name=='left' else np.array(right['default_coefficients']);assert np.max(abs(base[0]-expected))<1e-9
 accepted=0;rejected=0;err=0.
 for _ in range(500):
  values=[rng.uniform(-20,20),rng.uniform(-25,15),rng.uniform(-20,25),*rng.uniform(-20,20,3)];solved=coefficients(points,values)
  if solved is None:rejected+=1;continue
  accepted+=1;err=max(err,solved[1])
 assert accepted>100 and rejected>0 and err<1e-9
 reports[name]={'accepted':accepted,'rejected':rejected,'FK_error':err,'default_error':float(np.max(abs(base[0]-expected)))}
g=(KIT/'WorkspaceSource/locomotion.agf').read_text();nodes=newnodes(g);agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
for control in spec['controls']:assert agr.count('AnimSrcGCTVarFloat '+control+' {')==1
for side in ['Left','Right']:
 muzzle=nodes['ML147_'+side+'MuzzleIK'];support=nodes['ML147_LeftSupportGrip' if side=='Left' else 'ML140_RightSupportGrip']
 for node in [muzzle,support]:
  assert 'WeaponDirLr "ML147'+side+'MuzzleYaw"' in node
  assert 'WeaponDirUd "ML147'+side+'MuzzlePitch"' in node
  assert 'weaponrotator = RightHand' in node
  assert 'WeightAim "true"' in node and 'WeightPrimaryChain "false"' in node
 assert 'outputweaponoffsettobuffer = true' in muzzle
 assert 'outputweaponoffsettobuffer = true' not in support
 assert 'WeaponDirLr "0.0"' not in support
old=newnodes((BASE/'WorkspaceSource/locomotion.agf').read_text())
for n,node in old.items():
 if not n.startswith('{') and n not in ['MeleeBlockQ','ML140_RightSupportGrip']:assert nodes[n]==node,n
state=(KIT/'LogicSource/Scripts/4_World/MLPoseEditor144.c').read_text();world=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();menu=(KIT/'LogicSource/Scripts/5_Mission/MLPoseEditorMenu144.c').read_text();layout=(KIT/'LogicSource/GUI/MLPoseEditor144.layout').read_text()
for field in ['LeftValues','RightValues','LeftCoefficients','RightCoefficients']:assert field in state
assert 'MLPoseEditor_Left.json' in state and 'MLPoseEditor_Right.json' in state
assert 'Apply(Defaults(EditLeft))' in state and 'SideValues(leanSide == 0)' in world
assert 'ML144State.RightCoefficients[coefficient]' in world and 'ML144State.LeftCoefficients[coefficient]' in world
assert 'ML144State.EditLeft' in world and 'm_MLADSLeanDemoSign = -1;' in world
for i in range(17):
 for prefix in ['Value','Readout','Minus','Plus']:assert len(re.findall(r'\b'+prefix+str(i)+r' \{',layout))==1
assert 'SelectSide(name == "LeftSide")' in menu
for p in (KIT/'LogicSource').rglob('*.c'):
 s=p.read_text();assert s.count('{')==s.count('}'),p
print(json.dumps({'math':reports,'routing':'independent side values/coefficient buffers, selected-side JSON/save/reset, held NPC sign follows selection','muzzle':'yaw/pitch written to final hand-pivot native publication AND following support solve for both sides; no later zero-direction overwrite','native_compile_UI_muzzle_direction_grip':'NOT RUN'},indent=2))
