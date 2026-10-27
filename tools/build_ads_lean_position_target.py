"""Build a left-walking hold target from the captured native v117 reference.
Offsets are model metres: +X anatomical right, +Y up, +Z forward.
This verifies FK math and packaging, not native DayZ execution.
"""
from pathlib import Path
import argparse,json,math,re,shutil,subprocess,sys,uuid
import numpy as np
from scipy.spatial.transform import Rotation
import captured_pose_bridge as bridge
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1]

def build(seed_version, version, x=None, y=None, z=None):
 seed=ROOT/f'ads-lean-test/MovementLab_ADS_Lean_Mosin_v{seed_version}'
 dest=ROOT/f'ads-lean-test/MovementLab_ADS_Lean_Mosin_v{version}'
 if dest.exists():raise ValueError(f'Output already exists: {dest}')
 specs=list(seed.glob('Native-Shoulder-Contact-v*.json'))
 old_spec=max(specs,key=lambda p:int(re.search(r'-v(\d+)\.json$',p.name)[1]))
 data=json.loads(old_spec.read_text());parents=data['parents']
 reference={n:np.array(m,dtype=float) for n,m in data['reference'].items()}
 result={n:m.copy() for n,m in reference.items()}
 previous=np.array(data['common_hand_shift_m']);offset=np.array([previous[0] if x is None else x,previous[1] if y is None else y,previous[2] if z is None else z])
 def descendants(name):
  found=[]
  for child in parents:
   ancestor=child
   while ancestor:
    if ancestor==name:found.append(child);break
    ancestor=parents[ancestor]
  return found
 def move(name,matrix):
  delta=matrix@np.linalg.inv(result[name])
  for child in descendants(name):result[child]=delta@result[child]
 def swing(origin,target):
  origin=origin/np.linalg.norm(origin);target=target/np.linalg.norm(target)
  axis=np.cross(origin,target);sine=np.linalg.norm(axis);cosine=np.clip(origin@target,-1,1)
  if sine<1e-10:
   if cosine<0:raise ValueError('Ambiguous antiparallel arm turn')
   return np.eye(3)
  return Rotation.from_rotvec(axis/sine*math.atan2(sine,cosine)).as_matrix()
 bones=[]
 for side in ['Left','Right']:
  arm,fore,hand=[side+n for n in ['Arm','ForeArm','Hand']];bones.extend([arm,fore,hand])
  root,elbow,wrist=[result[n][:3,3].copy() for n in [arm,fore,hand]];goal=wrist+offset
  upper=np.linalg.norm(elbow-root);lower=np.linalg.norm(wrist-elbow);reach=np.linalg.norm(goal-root)
  if not abs(upper-lower)+1e-8<reach<upper+lower-1e-8:raise ValueError(f'{side} hand target unreachable: {reach:.4f}m; maximum {upper+lower:.4f}m')
  direction=(goal-root)/reach;along=(upper*upper-lower*lower+reach*reach)/(2*reach)
  radius=math.sqrt(max(0,upper*upper-along*along));pole=elbow-root;pole-=direction*(pole@direction);pole/=np.linalg.norm(pole)
  elbow_goal=root+direction*along+pole*radius
  matrix=result[arm].copy();matrix[:3,:3]=swing(elbow-root,elbow_goal-root)@matrix[:3,:3];move(arm,matrix)
  matrix=result[fore].copy();matrix[:3,:3]=swing(result[hand][:3,3]-result[fore][:3,3],goal-result[fore][:3,3])@matrix[:3,:3];move(fore,matrix)
  matrix=result[hand].copy();matrix[:3,:3]=reference[hand][:3,:3];move(hand,matrix)
 corrections=bridge.solve({n:m.tolist() for n,m in reference.items()},{n:m.tolist() for n,m in result.items()},parents)
 used={n:corrections[n] if n in bones else {'rotation_xyz':[0,0,0],'translation_xyz':[0,0,0]} for n in parents}
 assert max(abs(v) for d in used.values() for v in d['translation_xyz'])<1e-8
 replay=bridge.reconstruct({n:m.tolist() for n,m in reference.items()},parents,used)
 assert max(np.max(abs(np.array(replay[n])-result[n])) for n in result)<1e-8
 for side in ['Left','Right']:
  hand=side+'Hand';assert np.max(abs(result[hand][:3,3]-reference[hand][:3,3]-offset))<1e-8
  assert np.max(abs(result[hand][:3,:3]-reference[hand][:3,:3]))<1e-8
  for part in ['Shoulder','Arm']:assert np.max(abs(result[side+part][:3,3]-reference[side+part][:3,3]))<1e-8
 # Mutate only after the complete target has passed the geometry checks.
 shutil.copytree(seed,dest)
 graph_path=dest/'WorkspaceSource/locomotion.agf';graph=graph_path.read_text();nodes=newnodes(graph);changed=[]
 for bone in bones:
  for axis,angle in zip('XYZ',corrections[bone]['rotation_xyz']):
   name='ML118_Contact_'+bone+'_'+axis;node=nodes[name]
   graph=graph.replace(node,re.sub(r'Amount [-\d.eE]+','Amount '+format(-angle,'.14g'),node,count=1));changed.append(name)
 graph_path.write_text(graph)
 current=newnodes(graph)
 for name,node in nodes.items():
  if not name.startswith('{') and name not in changed:assert current[name]==node,name
 agr=dest/'WorkspaceSource/player_main.agr';text=agr.read_text();private=re.search(r'MLADSLeanLocomotion_v\d+\.agf',text)[0];replacement=f'MLADSLeanLocomotion_v{version}.agf';text=text.replace(private,replacement)
 text=re.sub(r'\{[A-F0-9]+\}(?=DZ/anims/workspaces/player/player_main/'+re.escape(replacement)+r')',lambda m:'{'+uuid.uuid4().hex[:16].upper()+'}',text);agr.write_text(text)
 builder=dest/'build_pbos.py';text=builder.read_text().replace(private,replacement);text=re.sub(r'V\d+ NOT RUN',f'V{version} NOT RUN',text);text=text.replace("'revision':'",f"'revision':'v{version} manual left hold target {offset.tolist()}; ",1);builder.write_text(text)
 for name in ['Launch-Test.ps1','Launch-Mosin-Lean-Test.cmd','Collect-Logs.ps1']:
  path=dest/name;path.write_text(path.read_text().replace(f'v{seed_version}',f'v{version}').replace(f'V{seed_version}',f'V{version}'))
 data.update({'goal':f'Manual left hold target from v117: {offset.tolist()}m','common_hand_shift_m':offset.tolist(),'desired':{n:m.tolist() for n,m in result.items()},'corrections':{n:corrections[n] for n in bones},'native_validation':'unverified'})
 (dest/f'Native-Shoulder-Contact-v{version}.json').write_text(json.dumps(data,indent=2)+'\n')
 readme=dest/'README.txt';readme.write_text(f'V{version}: LEFT walking target from v117 X={offset[0]*100:.6f}cm, Y={offset[1]*100:.6f}cm, Z={offset[2]*100:.6f}cm. Right hold, final support-grip ordering, all scripts/recorder/controls/camera retained from v{seed_version}. Native visible position and grip require verification.\n\n'+readme.read_text())
 for path in (seed/'LogicSource').rglob('*'):
  if path.is_file():assert path.read_bytes()==(dest/path.relative_to(seed)).read_bytes(),path
 subprocess.run([sys.executable,str(builder)],check=True,stdout=subprocess.DEVNULL)
 subprocess.run([sys.executable,str(ROOT/'tools/package_ads_lean_runtime.py'),str(dest),str(ROOT/f'artifacts/{dest.name}.zip')],check=True)
 print(f'PASS: target={offset.tolist()}m, delta={(offset-previous).tolist()}m; native-reference reconstruction <1e-8, 18 scoped coefficients only; native rendering untested.')
 return dest
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,required=True);parser.add_argument('--version',type=int,required=True)
 for axis in ['x','y','z']:parser.add_argument('--'+axis,type=float)
 args=parser.parse_args();build(args.seed,args.version,args.x,args.y,args.z)
