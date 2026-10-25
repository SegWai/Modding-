"""Generate symmetric Mosin ADS lean across stationary/moving stand and crouch."""
from pathlib import Path
import sys,json,re,hashlib,argparse,math,copy
sys.dont_write_bytecode=True
from dayz_graph_formats import end,newnodes
import captured_pose_bridge as pose
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--output',type=Path,default=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v5');args=p.parse_args()
OUT=args.output;SOURCE=args.workspace;SNAP=json.loads((OUT/'Pose-Snapshot.json').read_text())
POSES={};ERRORS={}
for side in ['left','right']:
 d=pose.solve(SNAP['reference'],SNAP[side],SNAP['parents']);r=pose.reconstruct(SNAP['reference'],SNAP['parents'],d)
 ERRORS[side]=max(abs(r[n][i][j]-SNAP[side][n][i][j]) for n in r for i in range(4) for j in range(4));assert ERRORS[side]<1e-5
 POSES[side]={n:v for n,v in d.items() if max(map(abs,v['rotation_xyz']))>1e-4 or max(map(abs,v['translation_xyz']))>1e-5}
 assert not any(n.startswith(('Face_','Eye')) or re.search('Hand(?:Index|Middle|Ring|Pinky|Thumb)',n) for n in POSES[side])
def guid(s):return hashlib.sha256(('MLADSLeanV5/'+s).encode()).hexdigest()[:16].upper()
def transform(name,child,weight,bone,axis,op,value):
 return f'''    AnimSrcNodeProcTransform {name} {{
     Child "{child}"
     Expression "{weight}"
     Bones {{
      AnimSrcNodeProcTrBoneItem "{{{guid(name)}}}" {{
       Bone "{bone}"
       Axis {axis}
       Space Model
       Op {op}
       Amount {value:.10g}
      }}
     }}
    }}'''
def upper(n):return n.startswith(('Spine','Neck','Head','LeftShoulder','RightShoulder','LeftArm','RightArm','LeftForeArm','RightForeArm')) or n in ['LeftHand','RightHand']
original=(SOURCE/'locomotion.agf').read_text();g=original;original_nodes=newnodes(g);added=[];coverage={}
modes=[('StandIdle','LeanIdleErcRas','full'),('StandWalk','LeanMoveErcRas','gait'),('CrouchIdle','LeanIdleCroRas','upper'),('CrouchWalk','LeanMoveCroRas','upper')]
changed=set()
for mode,prefix,mask in modes:
 child=prefix+'Right';chains=[]
 for side,suffix in [('left','Left'),('right','Right')]:
  name=prefix+suffix;block=newnodes(g)[name];expr=re.search(r'Expression "([^"]+)"',block)[1]
  g=g.replace(block,block.replace('Expression "'+expr+'"','Expression "('+expr+')*(1.0-MLADSLeanGate)"'),1);changed.add(name)
  collision=[]
  for m in re.finditer(r'AnimSrcNodeProcTrBoneItem\s+"[^\"]+"\s*\{',block):
   item=block[m.start():end(block,m.start())]
   if 'Bone "Collision"' in item:collision.append(re.sub(r'"\{[^}]+\}"',lambda _: '"{'+guid(mode+side+'collision')+'}"',item,count=1))
  if collision:
   name=f'ML5_{mode}_{side}_Collision';chains.append(f'    AnimSrcNodeProcTransform {name} {{\n     Child "{child}"\n     Expression "({expr})*MLADSLeanGate"\n     Bones {{\n'+'\n'.join(collision)+'\n     }\n    }');child=name
 mode_bones=set()
 for side in ['left','right']:
  weight=('clamp(-MLADSLeanAmount, 0.0, 1.0)' if side=='left' else 'clamp(MLADSLeanAmount, 0.0, 1.0)')+'*MLADSLeanGate'
  values=copy.deepcopy(POSES[side])
  if mask!='full':values={n:v for n,v in values.items() if upper(n) or (mask=='gait' and n=='Pelvis')}
  if mask=='upper':
   # Transfer the standing lateral hip offset to the lower torso, keeping
   # crouched pelvis/legs in the native pose. Do not transfer the hip drop.
   values['Spine']['translation_xyz'][0]+=POSES[side]['Pelvis']['translation_xyz'][0]
  for bone in pose.ordered(SNAP['parents']):
   if bone not in values:continue
   for op,field,sign in [('Rotate','rotation_xyz',-1),('Translate','translation_xyz',1)]:
    for i,axis in enumerate('XYZ'):
     value=sign*values[bone][field][i]
     if abs(value)<(1e-4 if op=='Rotate' else 1e-5):continue
     name=f'ML5_{mode}_{side}_{bone}_{op}_{axis}';chains.append(transform(name,child,weight,bone,axis,op,value));child=name;mode_bones.add(bone)
 assert g.count('Child "'+prefix+'Right"')==1
 g=g.replace('Child "'+prefix+'Right"','Child "'+child+'"',1)
 anchor=newnodes(g)[prefix+'Right'];g=g.replace(anchor,anchor+'\n'+'\n'.join(chains),1);added+=chains
 coverage[mode]={'native_chain':prefix,'output_node':child,'mask':mask,'bones':sorted(mode_bones),'default_tilt':'both native expressions multiplied by (1-MLADSLeanGate)','weight':'same MLADSLeanAmount and gate as all other modes'}
foot='''    AnimSrcNodeBlend MLADSLeanFootIKBlend {
     BlendWeight "clamp(abs(MLADSLeanAmount), 0.0, 1.0)*MLADSLeanGate*(1.0-clamp(Stance, 0.0, 1.0))*(1.0-clamp(MovementSpeed, 0.0, 1.0))"
     Child0 "IdleRasIK"
     Child1 "IdleRasSTM"
     OptimizeMin 1
     OptimizeMax 1
    }'''
assert g.count('Child "IdleRasIK"')==1;g=g.replace('Child "IdleRasIK"','Child "MLADSLeanFootIKBlend"',1);anchor=newnodes(g)['IdleRasIK'];g=g.replace(anchor,anchor+'\n'+foot,1);added.append(foot)
weapon=newnodes(g)['NormalWeaponIK'];assert 'WeaponRoll ""' in weapon
g=g.replace(weapon,weapon.replace('WeaponRoll ""','WeaponRoll "8.0*MLADSLeanAmount*MLADSLeanGate"'),1)
agr=(SOURCE/'player_main.agr').read_text();decl=''
for name,default,minimum,maximum in [('MLADSLeanGate',0,0,1),('MLADSLeanCanary',.731,0,1),('MLADSLeanAmount',0,-1,1)]:decl+=f'   AnimSrcGCTVarFloat {name} {{\n    DefaultValue {default}\n    MinValue {minimum}\n    MaxValue {maximum}\n   }}\n'
agr=agr.replace('  Variables {','  Variables {\n'+decl,1);agr=re.sub(r'(ControlTemplate AnimSrcGCT )"\{[0-9A-Fa-f]+\}"',lambda m:m[1]+'"{'+guid('control-template')+'}"',agr,count=1)
end(g,0);end(agr,0);nodes=newnodes(g)
allowed=changed|{'LeanForwardRotNodeErc','ErcMoveRasInjG','IdleRasSTM','Cro','CroMoveRasInjG','StanceMaster','IdleRas','NormalWeaponIK'}
for name,body in original_nodes.items():
 if name not in allowed:assert nodes[name]==body,name
seen=set()
def visit(name,active):
 if name in active:raise AssertionError('Cycle '+name)
 if name not in nodes or name in seen:return
 active.add(name)
 for child in re.findall(r'\bChild\d* "([^"]+)"',nodes[name]):visit(child,active)
 active.remove(name);seen.add(name)
for name in nodes:visit(name,set())
for path,text in [('locomotion.agf',g),('player_main.agr',agr)]: (OUT/'WorkspaceSource'/path).write_text(text)
(OUT/'Pose-Spec.json').write_text(json.dumps({'authoring':SNAP['authoring'],'coordinate_contract':SNAP['coordinate_contract'],'corrections':POSES,'math_reconstruction_error':ERRORS,'scope':'Symmetric central body offsets; same upper-body correction across ADS stand/walk/crouch; walking retains native gait/foot solver, crouch retains legs. Shared NormalWeaponIK roll expression targets signed 8-degree cant; native result requires validation.'},indent=2)+'\n')
(OUT/'Mode-Coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
print('Corrected bones', {s:len(v) for s,v in POSES.items()},'nodes',len(added),'modes',list(coverage))
