"""Offline FK and panel wiring checks. Does not compile Enforce or render DayZ UI."""
from pathlib import Path
import json,re,math,sys
import numpy as np
from scipy.spatial.transform import Rotation
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]
KIT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v144'
spec=json.loads((KIT/'Live-Editor-v144.json').read_text())
refs={n:np.array(v) for n,v in spec['reference'].items()}
def turn(a,b):
 a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);cross=np.cross(a,b);sine=np.linalg.norm(cross);cosine=np.clip(a@b,-1,1)
 if sine<1e-6:return np.eye(3)
 axis=cross/sine;x,y,z=axis;q=1-cosine
 return np.array([[cosine+x*x*q,x*y*q-z*sine,x*z*q+y*sine],[y*x*q+z*sine,cosine+y*y*q,y*z*q-x*sine],[z*x*q-y*sine,z*y*q+x*sine,cosine+z*z*q]])
def solve(values):
 x,y,z,pitch,yaw,roll=values
 orientation=Rotation.from_euler('xyz',[pitch,yaw,roll],degrees=True).as_matrix()
 shift=np.array([x,y+5,z])*.01
 rt=refs['RightHand']+shift
 targets={'Right':rt,'Left':rt+orientation@(refs['LeftHand']-refs['RightHand'])}
 angles=[];maxerr=0.
 for side in ['Left','Right']:
  root,e,w=[refs[side+n] for n in ['Arm','ForeArm','Hand']];target=targets[side];upper=np.linalg.norm(e-root);lower=np.linalg.norm(w-e);distance=np.linalg.norm(target-root)
  if distance<=abs(upper-lower)+.002 or distance>=upper+lower-.002:return None
  axis=(target-root)/distance;along=(upper*upper-lower*lower+distance*distance)/(2*distance);radius=math.sqrt(max(0,upper*upper-along*along));pole=e-root;pole-=axis*(pole@axis)
  if pole@pole<1e-6:return None
  pole/=np.linalg.norm(pole);goal=root+axis*along+pole*radius
  arm=turn(e-root,goal-root);fore=turn(arm@(w-e),target-goal);hand=orientation@(fore@arm).T
  native=[-Rotation.from_matrix(t).as_euler('xyz') for t in [arm,fore,hand]];angles.extend(np.ravel(native))
  # Replay native model-axis rotations, not just the inverse solve positions.
  a,b,c=[Rotation.from_euler('xyz',-v).as_matrix() for v in native]
  actual_elbow=root+a@(e-root);actual_wrist=actual_elbow+b@a@(w-e)
  maxerr=max(maxerr,np.max(abs(actual_wrist-target)),np.max(abs(c@b@a-orientation)),abs(np.linalg.norm(actual_elbow-root)-upper),abs(np.linalg.norm(actual_wrist-actual_elbow)-lower))
 return np.array(angles),maxerr
baseline=solve([5,-10,0,0,0,0]);assert baseline is not None
assert np.max(abs(baseline[0]-np.array(spec['default_coefficients'])))<1e-9
rng=np.random.default_rng(144);accepted=0;rejected=0;maxerr=0
for _ in range(1000):
 vals=[rng.uniform(-20,20),rng.uniform(-25,15),rng.uniform(-20,25),*rng.uniform(-20,20,3)]
 result=solve(vals)
 if result is None:rejected+=1;continue
 accepted+=1;maxerr=max(maxerr,result[1])
assert accepted>100 and rejected>0 and maxerr<1e-9
assert solve([1000,1000,1000,0,0,0]) is None
old=newnodes((ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v143/WorkspaceSource/locomotion.agf').read_text());new=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text());changed=[]
for name,node in old.items():
 if name.startswith('{'):continue
 if new[name]!=node:changed.append(name)
assert len(changed)==18 and all(n.startswith('ML143_RightX10_') for n in changed)
agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
for name in spec['control_names']:
 assert agr.count('AnimSrcGCTVarFloat '+name+' {')==1
 assert ('Expression "'+name+'"') in (KIT/'WorkspaceSource/locomotion.agf').read_text()
layout=(KIT/'LogicSource/GUI/MLPoseEditor144.layout').read_text()
for i in range(6):
 for name in ['Value','Readout','Minus','Plus']:assert len(re.findall(r'\b'+name+str(i)+r' \{',layout))==1
for name in ['Save','Load','Reset','Close','Hold','Status']:assert len(re.findall(r'\b'+name+r' \{',layout))==1
world=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();keys=(KIT/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();menu=(KIT/'LogicSource/Scripts/5_Mission/MLPoseEditorMenu144.c').read_text()
assert world.index('super.CommandHandler(')<world.index('  ML144UpdateEditor();')
assert 'if (ML144State.Open && ML144State.HoldRight)' in world
assert 'EnterScriptedMenu(86144, null)' in keys and 'return new ML144Menu;' in keys
assert 'super.OnShow();' in menu and 'super.OnHide();' in menu
assert 'AddActiveInputExcludes' in menu and 'RemoveActiveInputExcludes' in menu
for p in (KIT/'LogicSource').rglob('*.c'):
 s=p.read_text();assert s.count('{')==s.count('}'),p
 assert not re.search(r'\b(?:vector|float|int|string) local\b',s),p
report={'baseline_v143_coefficients_max_error':float(np.max(abs(baseline[0]-spec['default_coefficients']))),'random_targets_accepted':accepted,'random_targets_rejected':rejected,'max_fk_wrist_orientation_length_error':maxerr,'graph_changes':'18 fixed arm amounts replaced by dynamic inputs; previous body/head/support solver nodes unchanged','ui':'6 sliders, readouts and +/- pairs; save/load/reset/hold/close wired; F6 custom menu; paired input focus lifecycle','native_compilation_and_ui':'not run; requires Windows DayZDiag'}
print(json.dumps(report,indent=2))
