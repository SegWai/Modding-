"""Revise v13 stationary legs and add shared final head compensation.
Reuses the known-loaded GCT and working NPC controller unchanged.
"""
from pathlib import Path
import sys,math,json,re,copy
sys.dont_write_bytecode=True
from dayz_graph_formats import newnodes
import captured_pose_bridge as pose
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v14'
BASE=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v13'
EARLY=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v3'
LOWER=['Pelvis','LeftUpLeg','LeftLeg','LeftFoot','RightUpLeg','RightLeg','RightFoot']
def main():
 g=(BASE/'WorkspaceSource/locomotion.agf').read_text();nodes=newnodes(g)
 old=json.loads((EARLY/'Pose-Spec.json').read_text())['corrections'];revised=[]
 for side in ['left','right']:
  for bone in LOWER:
   d=old[side].get(bone,{})
   for op,field,sign in [('Rotate','rotation_xyz',-1),('Translate','translation_xyz',1)]:
    for axis,v in zip('XYZ',d.get(field,[0,0,0])):
     name=f'ML5_StandIdle_{side}_{bone}_{op}_{axis}'
     if name in nodes:
      before=nodes[name];after=re.sub(r'\bAmount [-+0-9.eE]+',f'Amount {sign*v:.10g}',before)
      if before!=after:g=g.replace(before,after,1);revised.append(name)
     else:assert abs(v)<(1e-4 if op=='Rotate' else 1e-5),name
 # Apply only to Head, after the normal ADS/weapon IK stack. No gun or arm edits.
 assert g.count('Child "NormalWeaponIK"')==1
 g=g.replace('Child "NormalWeaponIK"','Child "ML14_HeadCounterRoll"',1)
 extra='''
    AnimSrcNodeProcTransform ML14_HeadForwardNod {
     Child "NormalWeaponIK"
     Expression "abs(MLADSLeanAmount)*MLADSLeanGate"
     Bones {
      AnimSrcNodeProcTrBoneItem "{F9EE95F8C6F6C401}" {
       Bone "Head"
       Axis X
       Space Model
       Op Rotate
       Amount -0.0872664626
      }
     }
    }
    AnimSrcNodeProcTransform ML14_HeadCounterRoll {
     Child "ML14_HeadForwardNod"
     Expression "MLADSLeanAmount*MLADSLeanGate"
     Bones {
      AnimSrcNodeProcTrBoneItem "{F9EE95F8C6F6C402}" {
       Bone "Head"
       Axis Z
       Space Model
       Op Rotate
       Amount -0.2094395102
      }
     }
    }
'''
 anchor=newnodes(g)['NormalWeaponIK'];g=g.replace(anchor,anchor+extra,1)
 (KIT/'WorkspaceSource/locomotion.agf').write_text(g)
 snap=json.loads((BASE/'Pose-Snapshot.json').read_text());early=json.loads((EARLY/'Pose-Snapshot.json').read_text())
 assert max(abs(snap['reference'][b][i][j]-early['reference'][b][i][j]) for b in snap['reference'] for i in range(4) for j in range(4))<1e-5
 out={'reference':snap['reference'],'parents':snap['parents'],'note':'Stationary baseline with restored v3 legs/hips and current torso/arms. Final empirical head compensation is an additional post-ADS graph pass.'}
 for side in ['left','right']:
  full=pose.solve(snap['reference'],snap[side],snap['parents'])
  lower=pose.solve(early['reference'],early[side],early['parents'])
  for b in LOWER:full[b]=lower[b]
  out[side]=pose.reconstruct(snap['reference'],snap['parents'],full)
 (KIT/'Static-Pose-Snapshot.json').write_text(json.dumps(out,indent=2)+'\n')
 spec={'stationary_lower_source':'MovementLab_ADS_Lean_Mosin_v3','stationary_lower_bones':LOWER,'stationary_lower_corrections':{s:{b:old[s][b] for b in LOWER} for s in ['left','right']},'modified_static_nodes':revised,'head':{'placement':'after NormalWeaponIK, before SickHotColdQ','bone':'Head','pitch_forward_degrees':5,'extra_counter_roll_degrees':12,'scope':'Shared for player and NPC in custom ADS lean: standing idle/walk and crouch idle/walk. Zero at neutral or native comparison.','interpretation':'Empirical correction for head tilt visible in supplied screenshots; native appearance requires test.'},'preserved':['v13 NPC controller and GCT','walking leg motion and IK','crouched legs','central lateral exposure','weapon IK, hands and shared weapon roll']}
 (KIT/'Pose-Revision-v14.json').write_text(json.dumps(spec,indent=2)+'\n')
 p=KIT/'Pose-Spec.json';d=json.loads((BASE/'Pose-Spec.json').read_text());d['graph_overrides']='Pose-Revision-v14.json: static legs/hips restored to v3 and shared final head correction';p.write_text(json.dumps(d,indent=2)+'\n')
 print('Restored static nodes:',len(revised),'head nodes: 2')
if __name__=='__main__':main()
