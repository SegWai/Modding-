"""Independent FK equivalence and graph routing checks for crash mitigation."""
from pathlib import Path
import sys,re,json,hashlib,collections
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent))
from dayz_graph_formats import newnodes
sys.setrecursionlimit(10000)
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v163';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v164'
report=json.loads((b/'Graph-Compaction-v164.json').read_text());native=json.loads((a/'Native-Head-Travel-v55.json').read_text());parents=native['parents'];names=list(parents);indices={n:i for i,n in enumerate(names)}
ancestors={}
for n in names:
 chain=set();p=parents[n]
 while p:chain.add(p);p=parents[p]
 ancestors[n]=chain
subs={n:np.array([indices[m] for m in names if m==n or n in ancestors[m]],dtype=int) for n in names}
reference=np.array([native['sides']['right']['desired'][n] for n in names]);ops=report['original_operations']
def parse(item):
 return (re.search(r'Bone "([^"]+)"',item)[1],re.search(r'Axis ([XYZ])',item)[1],re.search(r'Op (\w+)',item)[1],float(re.search(r'Amount ([-+\d.eE]+)',item)[1]))
def apply(p,op,weight):
 bone,axis,kind,value=op;ids=subs[bone];axisidx='XYZ'.index(axis)
 if kind=='Translate':p[ids,axisidx,3]+=value*weight
 else:
  angle=np.zeros(3);angle[axisidx]=-value*weight;rot=Rotation.from_rotvec(angle).as_matrix();pivot=p[indices[bone],:3,3].copy();p[ids,:3,3]=(p[ids,:3,3]-pivot)@rot.T+pivot;p[ids,:3,:3]=np.einsum('ij,njk->nik',rot,p[ids,:3,:3])
old={k:v for k,v in newnodes((a/'WorkspaceSource/locomotion.agf').read_text()).items() if not k.startswith('{')};new={k:v for k,v in newnodes((b/'WorkspaceSource/locomotion.agf').read_text()).items() if not k.startswith('{')}
maximum=0.;cases=0;consumed=set()
for runid,run in enumerate(report['runs']):
 original=[parse(ops[name]['item']) for name in run['operations']];compiled=[];consumed.update(run['operations'])
 for level,layer in enumerate(run['layers']):
  for i,name in enumerate(layer):
   for other in layer[i+1:]:
    x=ops[name]['bone'];y=ops[other]['bone'];assert x!=y and x not in ancestors[y] and y not in ancestors[x]
  node=new[f'ML164_Compact_{runid}_{level}'];items=[v for v in newnodes(node).values() if v.startswith('AnimSrcNodeProcTrBoneItem')];actual=[parse(item) for item in items];assert actual==[parse(ops[name]['item']) for name in layer]
  assert 'Expression "'+run['expression']+'"' in node
  compiled.extend(actual)
 assert collections.Counter(compiled)==collections.Counter(original)
 for weight in [0.,.01,.25,.5,.75,.99,1.]:
  p=reference.copy();q=reference.copy()
  for op in original:apply(p,op,weight)
  for op in compiled:apply(q,op,weight)
  err=float(np.max(abs(p-q)));maximum=max(maximum,err);assert err<1e-11,(runid,weight,err);cases+=1
for name,node in old.items():
 expected=node if name in consumed else re.sub(r'\b(Child\d*) "([^"]+)"',lambda m:m[1]+' "'+report['replacements'].get(m[2],m[2])+'"',node)
 assert new[name]==expected,name
# Independently detect cycles and count depth of the live root.
cache={};active=set()
def depth(n):
 if n in cache:return cache[n]
 assert n not in active,('cycle',n);active.add(n)
 children=[c for c in re.findall(r'\bChild\d* "([^"]+)"',new[n]) if c in new]
 cache[n]=1+max([depth(c) for c in children],default=0);active.remove(n);return cache[n]
assert depth('LocomotionQ')==report['root_depth_after']<report['root_depth_before']*.6
for p in (a/'LogicSource/Scripts').rglob('*.c'):assert p.read_bytes()==(b/p.relative_to(a)).read_bytes(),p
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
 assert hashlib.sha256((b/rel).read_bytes()).hexdigest()=='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
collector=(b/'Collect-Logs.ps1').read_text();assert "@('.mdmp','.dmp')" in collector and '$dump.Length -le 24MB' in collector
result={'independent_forward_kinematics_cases':cases,'max_matrix_difference':maximum,'original_operations_batched':report['original_operations_batched'],'root_depth_before':report['root_depth_before'],'root_depth_after':report['root_depth_after'],'all_scripts_camera_editor_and_preset_unchanged':True,'crash_dump_collection':'newest dump <=24MiB, retained on disk if larger','native_pose_and_crash_resolution':'NOT RUN; native multi-bone evaluation and exit-left-lean replay need gameplay test'}
(b/'Graph-Compaction-Checks-v164.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
