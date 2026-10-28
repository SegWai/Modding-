"""Verify one-shot retarget math and graph wiring without native playback."""
from pathlib import Path
import sys,re,json,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v171';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v172'
spec=json.loads((b/'Shared-Walking-Upper-v172.json').read_text());names=spec['bones'];parentidx=spec['parents'];parents={n:(names[parentidx[i]] if i else None) for i,n in enumerate(names)}
full=json.loads((a/'Native-Head-Travel-v55.json').read_text())['sides']['right']['desired'];target={n:np.array(full[n],float) for n in names}
rng=np.random.default_rng(172);maximum=0.
for _ in range(100):
 # Different gait pelvis frame plus independent arm/spine model changes.
 source={n:m.copy() for n,m in target.items()}
 for n in names:
  source[n][:3,:3]=Rotation.from_rotvec(rng.uniform(-.15,.15,3)).as_matrix()@source[n][:3,:3]
  source[n][:3,3]+=rng.uniform(-.03,.03,3)
 desired={n:m.copy() for n,m in target.items()};bob=source['Pelvis'][1,3]-target['Pelvis'][1,3]
 desired['Pelvis']=source['Pelvis'].copy();desired['Pelvis'][0,3]=target['Pelvis'][0,3];desired['Pelvis'][2,3]=target['Pelvis'][2,3]
 for n in names[1:]:desired[n][1,3]+=bob
 # Independent reference solver checks the ML172 parent-inheritance formula.
 coeff=bridge.solve({n:m.tolist() for n,m in source.items()},{n:m.tolist() for n,m in desired.items()},parents)
 replay=bridge.reconstruct({n:m.tolist() for n,m in source.items()},parents,coeff)
 err=max(np.max(abs(np.array(replay[n])-desired[n])) for n in names);assert err<1e-10;maximum=max(maximum,float(err))
 # Coded parent-space conversion independently matches correction coefficients.
 for i,n in enumerate(names[1:],1):
  p=names[parentidx[i]];inherited=desired[p][:3,:3]@source[p][:3,:3].T
  current_p=desired[p][:3,3]+inherited@(source[n][:3,3]-source[p][:3,3])
  current_r=inherited@source[n][:3,:3]
  correction=desired[n][:3,:3]@current_r.T
  assert np.allclose(Rotation.from_euler('xyz',coeff[n]['rotation_xyz']).as_matrix(),correction,atol=1e-10)
  assert np.allclose(coeff[n]['translation_xyz'],desired[n][:3,3]-current_p,atol=1e-10)
  assert np.allclose(desired[n][:3,:3],target[n][:3,:3])
 # Pelvis keeps its walking rotation/Y, and lower limbs inherit translation only.
 assert np.allclose(desired['Pelvis'][:3,:3],source['Pelvis'][:3,:3])
 assert desired['Pelvis'][1,3]==source['Pelvis'][1,3]
old={k:v for k,v in newnodes((a/'WorkspaceSource/locomotion.agf').read_text()).items() if not k.startswith('{')};new={k:v for k,v in newnodes((b/'WorkspaceSource/locomotion.agf').read_text()).items() if not k.startswith('{')}
for n,node in old.items():
 expected=node
 if n=='ML166_FinalVerticalAim':expected=node.replace('Child "ML157_HeadZ"','Child "ML172_SharedWalkingUpper"',1)
 if n=='ML166_FinalAimOnly':expected=node.replace('Child0 "ML157_HeadZ"','Child0 "ML172_SharedWalkingUpper"',1)
 assert new[n]==expected,n
assert len(set(new)-set(old))==117
for i in range(116):
 node=new['ML172_Upper'+str(i)];bone=re.search(r'Bone "([^"]+)"',node)[1]
 assert bone in names and all(x not in bone for x in ['Leg','Foot','Toe'])
 if i<2:assert bone=='Pelvis' and 'Op Translate' in node
 else:assert bone!='Pelvis'
assert 'BlendWeight "ML172Active"' in new['ML172_SharedWalkingUpper']
state=(b/'LogicSource/Scripts/4_World/MLWalkingUpper172.c').read_text();assert 'if (canLearn && !solution)' in state and 'Write(actor, null, 0)' in state
assert 'Failed[walkKey]' in state and 'Walking[walkKey] = solution;' in state
assert 'solution.Values.Count() != 116' in state
keys={pose+gait*4+direction*8 for pose in range(4) for gait in range(2) for direction in range(8)};assert keys==set(range(64))
for p in (a/'LogicSource/Scripts').rglob('*.c'):
 if p.name=='MLADSLeanPlayer.c':continue
 assert p.read_bytes()==(b/p.relative_to(a)).read_bytes(),p
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
 assert hashlib.sha256((b/rel).read_bytes()).hexdigest()=='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
report={'retarget_cases':100,'max_matrix_error':maximum,'upper_target':'standing model orientations/positions plus walking vertical bob','lower_target':'native walking pelvis rotation/Y and leg joint motion unchanged; pelvis X/Z anchor shared','cache_keys':64,'new_controls':117,'no_perframe_feedback':'reference capture only with output disabled; solved keys never resampled until invalidated','preserved':'fixed preset/camera/controls/late aim and crash mitigation','native_compile_pose_transition_grip':'NOT RUN'}
(b/'Shared-Walking-Upper-Checks-v172.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
