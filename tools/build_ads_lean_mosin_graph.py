from pathlib import Path
import sys,json,re,hashlib,uuid,struct,zipfile,math
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import captured_pose_bridge as pose
from dayz_graph_formats import end,newnodes
import argparse
parser=argparse.ArgumentParser(description='Generate Mosin ADS lean graph patches from the supplied fresh workspace and approved pose snapshot.')
parser.add_argument('--workspace',type=Path,required=True,help='Fresh player_main folder; read only')
parser.add_argument('--snapshot',type=Path,default=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v3/Pose-Snapshot.json')
parser.add_argument('--output',type=Path,default=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v3')
parser.add_argument('--keep-native-foot-ik',action='store_true',help='Reproduce the v2 foot-pinning behavior for diagnosis')
args=parser.parse_args()
SOURCE=args.workspace;OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
SNAP=json.loads(args.snapshot.read_text())
POSES={};ERRORS={}
for side in ['left','right']:
 d=pose.solve(SNAP['reference'],SNAP[side],SNAP['parents']);check=pose.reconstruct(SNAP['reference'],SNAP['parents'],d)
 error=max(abs(check[n][i][j]-SNAP[side][n][i][j]) for n in check for i in range(4) for j in range(4));assert error<1e-5;ERRORS[side]=error
 POSES[side]={n:v for n,v in d.items() if max(map(abs,v['rotation_xyz']))>1e-4 or max(map(abs,v['translation_xyz']))>1e-5}
 # Tiny facial/finger numeric drift is excluded; the Mosin's native finger and IK poses remain.
 assert not any(n.startswith(('Face_','Eye')) or re.search('Hand(?:Index|Middle|Ring|Pinky|Thumb)',n) for n in POSES[side])
def guid(text):return hashlib.sha256(('MLADSLeanMosinV1/'+text).encode()).hexdigest()[:16].upper()
def item(bone,axis,op,amount,key):
 return f'      AnimSrcProcTrBoneItem "{{{guid(key)}}}" {{\n       Bone "{bone}"\n       Axis {axis}\n       Space Model\n       Op {op}\n       Amount {amount:.10g}\n      }}'.replace('AnimSrcProcTrBoneItem','AnimSrcNodeProcTrBoneItem')
def node(name,child,expression,items):
 return f'    AnimSrcNodeProcTransform {name} {{\n     Child "{child}"\n     Expression "{expression}"\n     Bones {{\n'+ '\n'.join(items)+'\n     }\n    }'
original=(SOURCE/'locomotion.agf').read_text();g=original;nodes=newnodes(g)
# Retain the native collision displacement through the full A/B gate range.
collision=[]
for side,oldname in [('left','LeanIdleErcRasLeft'),('right','LeanIdleErcRasRight')]:
 block=nodes[oldname];expr=re.search(r'Expression "([^"]+)"',block)[1]
 ci=[]
 for m in re.finditer(r'AnimSrcNodeProcTrBoneItem\s+"[^\"]+"\s*\{',block):
  b=block[m.start():end(block,m.start())]
  if re.search(r'Bone "Collision"',b):
   b=re.sub(r'"\{[^}]+\}"',f'"{{{guid(side+"collision")}}}"',b,count=1);ci.append(b)
 g=g.replace(block,block.replace(f'Expression "{expr}"',f'Expression "({expr})*(1.0-MLADSLeanGate)"'),1)
 if ci:collision.append((side,expr,ci))
child='LeanIdleErcRasRight';new=[]
for side,expr,items in collision:
 name='MLADSLeanCollision_'+side;new.append(node(name,child,f'({expr})*MLADSLeanGate',items));child=name
for side in ['left','right']:
 weight='clamp(-Lean, 0.0, 1.0)*MLADSLeanGate' if side=='left' else 'clamp(Lean, 0.0, 1.0)*MLADSLeanGate'
 # Parent-first propagation; per bone rotate X/Y/Z then translate X/Y/Z.
 for bone in pose.ordered(SNAP['parents']):
  if bone not in POSES[side]:continue
  d=POSES[side][bone];items=[]
  for op,field,sign in [('Rotate','rotation_xyz',-1),('Translate','translation_xyz',1)]:
   for index,axis in enumerate('XYZ'):
    value=sign*d[field][index]
    if abs(value)<(1e-4 if op=='Rotate' else 1e-5):continue
    # Separate nodes explicitly define native operation order, not just item order.
    name=f'MLADSLean_{side}_{bone}_{op}_{axis}'
    new.append(node(name,child,weight,[item(bone,axis,op,value,name)]));child=name
# The only consumer of the standing raised idle chain is redirected; other states stay native.
assert g.count('Child "LeanIdleErcRasRight"')==1
g=g.replace('Child "LeanIdleErcRasRight"',f'Child "{child}"',1)
anchor=newnodes(g)['LeanIdleErcRasRight'];g=g.replace(anchor,anchor+'\n'+'\n'.join(new),1)
# The native IdleRasIK solver runs after the custom pose and would pin the
# feet back to their pre-lean targets. Bypass only that foot solver at custom
# standing lean, blending back to it at center/F7/other stances.
if not args.keep_native_foot_ik:
 footblend='''    AnimSrcNodeBlend MLADSLeanFootIKBlend {
     BlendWeight "clamp(abs(Lean), 0.0, 1.0)*MLADSLeanGate*(1.0-clamp(Stance, 0.0, 1.0))"
     Child0 "IdleRasIK"
     Child1 "IdleRasSTM"
     OptimizeMin 1
     OptimizeMax 1
    }'''
 assert g.count('Child "IdleRasIK"')==1
 g=g.replace('Child "IdleRasIK"','Child "MLADSLeanFootIKBlend"',1)
 foot_anchor=newnodes(g)['IdleRasIK']
 g=g.replace(foot_anchor,foot_anchor+'\n'+footblend,1)
 new.append(footblend)
agr=(SOURCE/'player_main.agr').read_text();control='   AnimSrcGCTVarFloat MLADSLeanGate {\n    DefaultValue 0\n    MinValue 0\n    MaxValue 1\n   }\n   AnimSrcGCTVarFloat MLADSLeanCanary {\n    DefaultValue 0.731\n    MinValue 0\n    MaxValue 1\n   }\n'
assert agr.count('  Variables {')==1;agr=agr.replace('  Variables {','  Variables {\n'+control,1)
# A private template identity prevents reuse of a native cached control template.
agr=re.sub(r'(ControlTemplate AnimSrcGCT )\"\{[A-Fa-f0-9]+\}\"',lambda m:m[1]+'\"{'+guid('ControlTemplate-v2')+'}\"',agr,count=1)
# Balance parser and child-graph cycle checks, including untouched native nodes.
end(g,0);end(agr,0);N=newnodes(g);assert len(N)==len(newnodes(original))+sum(len(newnodes(block)) for block in new)
def walk(n,active,seen):
 if n in active:raise AssertionError('Graph cycle '+n)
 if n in seen or n not in N:return
 active.add(n)
 for name in re.findall(r'\bChild\d* "([^"]+)"',N[n]):walk(name,active,seen)
 active.remove(n);seen.add(n)
seen=set()
for n in N:walk(n,set(),seen)
for n,b in newnodes(original).items():
 if n not in ['LeanIdleErcRasLeft','LeanIdleErcRasRight','LeanForwardRotNodeErc']+([] if args.keep_native_foot_ik else ['StanceMaster','IdleRas']):assert N[n]==b,n
# Baseline at gate 0: original expressions and all custom expressions = 0.
for side in ['left','right']:
 for bone,d in POSES[side].items():assert all(math.isfinite(x) for v in d.values() for x in v)
patch=OUT/'WorkspaceSource';patch.mkdir(exist_ok=True)
(patch/'locomotion.agf').write_text(g);(patch/'player_main.agr').write_text(agr)
(patch/'config.cpp').write_text('class CfgPatches { class MLADSLeanWorkspace { units[] = {}; weapons[] = {}; requiredVersion = 0.1; requiredAddons[] = {"DZ_Anims_Cfg"}; }; };\n')
manifest={p.relative_to(SOURCE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.rglob('*') if p.is_file()}
(OUT/'Workspace-Provenance.json').write_text(json.dumps({'source':'user player_main.rar','files':manifest,'note':'Current source files supplied by user; runtime build/branch not yet independently verified.'},indent=2)+'\n')
(OUT/'Pose-Spec.json').write_text(json.dumps({'authoring':'approved Blender v6','coordinate_contract':SNAP['coordinate_contract'],'corrections':POSES,'math_reconstruction_error':ERRORS,'scope':'Additive pose study on native Mosin ADS, not a baked absolute pose. Native IK/finger poses retained. Native graph transform order/sign/pivots and first-person alignment need local validation.'},indent=2)+'\n')
print('Changed bones:',{k:len(v) for k,v in POSES.items()},'new graph nodes',len(new),'math',ERRORS)
