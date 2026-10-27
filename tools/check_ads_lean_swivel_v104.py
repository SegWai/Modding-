"""Check fixed-wrist swivel math, graph routing and Panacea-only loadout wiring."""
from pathlib import Path
import sys,re,json,math
import numpy as np
from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v104';a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v103'
spec=json.loads((r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v101/Left-Shoulder-Height-v101.json').read_text()) if (r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v101/Left-Shoulder-Height-v101.json').exists() else None
# A swivel uses the complete arm as a rigid body; wrist lies on its axis.
def euler(m):
 y=math.asin(np.clip(-m[2,0],-1,1));return np.array([math.atan2(m[2,1],m[2,2]),y,math.atan2(m[1,0],m[0,0])])
def rotation(v):
 x,y,z=v;cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
 return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
def solve(root,elbow,wrist,pole):
 upper=elbow-root;lower=wrist-elbow;reach=wrist-root;d=np.linalg.norm(reach);axis=reach/d
 along=(upper@upper-lower@lower+d*d)/(2*d);radius=math.sqrt(max(0,upper@upper-along*along));centre=root+axis*along
 target=pole-axis*(pole@axis);target/=np.linalg.norm(target);source=(elbow-centre);source/=np.linalg.norm(source)
 cross=np.cross(source,target);sine=np.linalg.norm(cross);cosine=np.clip(source@target,-1,1);turn=cross/sine
 x,y,z=turn;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
 m=np.eye(3)*cosine+(1-cosine)*np.outer(turn,turn)+sine*K
 return m,centre+target*radius
root=np.array([-.28544,1.33802,.08846]);elbow=np.array([-.14460,1.42578,.32629]);wrist=np.array([.05790,1.32951,.48551]);pole=np.array([.422618,-.906308,0.])
rng=np.random.default_rng(104)
for _ in range(200):
 shift=rng.normal(size=3)*10
 m,goal=solve(root+shift,elbow+shift,wrist+shift,pole)
 assert np.linalg.norm(root+shift+m@(wrist-root)-(wrist+shift))<1e-10
 assert np.linalg.norm(root+shift+m@(elbow-root)-goal)<1e-10
 assert goal[1]<elbow[1]+shift[1]
 assert np.linalg.norm(rotation(euler(m))-m)<1e-10
 assert np.linalg.norm(rotation(euler(m.T))@m-np.eye(3))<1e-10
 assert abs(np.linalg.norm(goal-(root+shift))-np.linalg.norm(elbow-root))<1e-10
 assert abs(np.linalg.norm(wrist+shift-goal)-np.linalg.norm(wrist-elbow))<1e-10
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
changed=[]
for name,node in old.items():
 if name.startswith('{'):continue
 name2=name.replace('ML103','ML104');expected=node.replace('ML103','ML104')
 if new[name2]!=expected:changed.append(name2)
assert set(changed)=={'ML104_Pole_Right_X','ML104_RestorePrivateHands'},changed
assert 'ML104_LeftWristHold' not in new['ML104_RestorePrivateHands']
assert 'ML104_RightWristHold' in new['ML104_RestorePrivateHands']
assert 'Child "ML104_LeftHandCounter_Z"' in new['ML104_Pole_Right_X']
agr=(b/'WorkspaceSource/player_main.agr').read_text()
for axis in 'XYZ':
 assert f'AnimSrcGCTVarFloat ML104LeftHand{axis}' in agr
 assert f'Expression "ML104LeftHand{axis}"' in new['ML104_LeftHandCounter_'+axis]
 assert 'Bone "LeftHand"' in new['ML104_LeftHandCounter_'+axis]
assert not re.search(r'\b(?:Default|Min|Max) ',agr)
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
assert 'poleIndex < 10' in player and 'm_ML104PoleVars[10]' in player
assert 'MLArmPoleMath104.Swivel(leftRoot' in player
assert 'MLArmPoleMath104.Solve(rightRoot' in player
assert 'm_ML104PoleVars[poleAxis + 7]' in player
assert 'reach / distance' not in (b/'LogicSource/Scripts/4_World/MLArmPoleMath104.c').read_text()
mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();playerloadout=mission[:mission.index(' void MLADSLeanRefreshAmmo')]
assert 'MLADSLeanPanacea104.Equip(player)' in playerloadout
for name in ['AK74','MP5K','SVD','FNX45']:assert '"'+name+'"' not in playerloadout
assert 'AliceBag_Green' in playerloadout
launcher=(b/'Launch-Test.ps1').read_text();assert '2389010221' in launcher and '$mods = @($panacea,$workspace,$logic)' in launcher
for p in (b/'LogicSource/Scripts/4_World').glob('*Camera*.c'):
 original=a/p.relative_to(b)
 if original.exists(): assert p.read_text()==original.read_text().replace('103','104')
panacea=json.loads((b/'Panacea-Loadout-v104.json').read_text())
helper=(b/'LogicSource/Scripts/4_World/MLADSLeanPanacea104.c').read_text()
assert len(panacea['weapon_magazine_pairs'])==4
for w,m in panacea['weapon_magazine_pairs']:assert f'"{w}", "{m}"' in helper
assert 'weapon.SpawnAmmo(magazineType)' in helper
print('PASS: 200 fixed-wrist/bone-length/inverse-orientation cases; only intended graph routing changes; 10 controls; no old player weapons; Panacea launch wiring. Native compilation/render/Panacea equipment not executed.')
