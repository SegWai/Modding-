#!/usr/bin/env python3
"""Offline full-pose correction math and native graph-fragment generation.

Uses column-vector 4x4 rigid transforms. Native row-basis matrices need explicit
conversion at the boundary. Does NOT establish native graph rotation semantics,
perform a runtime handoff, or implement a finished DayZ ragdoll.
"""
import argparse
import json
import math
import uuid
from pathlib import Path


def multiply(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def identity():
    return [[float(i==j) for j in range(4)] for i in range(4)]


def validate(m):
    if len(m)!=4 or any(len(r)!=4 for r in m) or not all(math.isfinite(v) for r in m for v in r):
        raise ValueError('Expected finite 4x4 transform')
    if max(abs(m[3][j]-(1 if j==3 else 0)) for j in range(4))>1e-6:
        raise ValueError('Non-affine transform')
    if max(abs(sum(m[k][i]*m[k][j] for k in range(3))-(1 if i==j else 0)) for i in range(3) for j in range(3))>.002:
        raise ValueError('Non-rigid transform')
    det=sum(m[0][i]*(m[1][(i+1)%3]*m[2][(i+2)%3]-m[1][(i+2)%3]*m[2][(i+1)%3]) for i in range(3))
    if abs(det-1)>.002:
        raise ValueError('Reflection or invalid rotation')


def inverse(m):
    validate(m)
    out=identity()
    for i in range(3):
        for j in range(3):out[i][j]=m[j][i]
        out[i][3]=-sum(m[j][i]*m[j][3] for j in range(3))
    return out


def rotation(x,y,z):
    cx,sx,cy,sy,cz,sz=math.cos(x),math.sin(x),math.cos(y),math.sin(y),math.cos(z),math.sin(z)
    return [[cz*cy,cz*sy*sx-sz*cx,cz*sy*cx+sz*sx,0],
            [sz*cy,sz*sy*sx+cz*cx,sz*sy*cx-cz*sx,0],[-sy,cy*sx,cy*cx,0],[0,0,0,1]]


def angles(m):
    # Applied X, then Y, then Z in fixed model axes (Rz*Ry*Rx).
    y=math.asin(max(-1,min(1,-m[2][0])))
    if abs(math.cos(y))>1e-7:
        return [math.atan2(m[2][1],m[2][2]),y,math.atan2(m[1][0],m[0][0])]
    return [math.atan2(-m[1][2],m[1][1]),y,0]


def ordered(parents):
    done=[]
    remaining=set(parents)
    while remaining:
        batch=sorted(n for n in remaining if parents[n] is None or parents[n] in done)
        if not batch:raise ValueError('Cyclic/missing parent')
        done+=batch
        remaining.difference_update(batch)
    return done


def solve(reference,desired,parents):
    if not reference or len(reference)>512:
        raise ValueError('Expected 1..512 captured bones')
    if set(reference)!=set(desired) or set(reference)!=set(parents):
        raise ValueError('Pose/hierarchy bone sets differ')
    for m in list(reference.values())+list(desired.values()):validate(m)
    result={}
    for bone in ordered(parents):
        parent=parents[bone]
        current=reference[bone] if parent is None else multiply(multiply(desired[parent],inverse(reference[parent])),reference[bone])
        # Rotation about the bone's own pivot: translation handled separately.
        current_rotation=[row[:] for row in current]
        target_rotation=[row[:] for row in desired[bone]]
        for i in range(3):current_rotation[i][3]=target_rotation[i][3]=0
        delta=multiply(target_rotation,inverse(current_rotation))
        result[bone]={'rotation_xyz':angles(delta),'translation_xyz':[desired[bone][i][3]-current[i][3] for i in range(3)]}
    return result


def reconstruct(reference,parents,corrections):
    result={}
    for bone in ordered(parents):
        parent=parents[bone]
        current=reference[bone] if parent is None else multiply(multiply(result[parent],inverse(reference[parent])),reference[bone])
        d=corrections[bone]
        out=multiply(rotation(*d['rotation_xyz']),current)
        for i in range(3):out[i][3]=current[i][3]+d['translation_xyz'][i]
        result[bone]=out
    return result


def fragment(parents,base_node='APoseSrc'):
    """Graph nodes/controls only; caller must integrate an instance-scoped gate.

    Native enum spelling is based on supplied AGF examples. Fixed-axis order,
    pivot/child propagation, evaluation and final physics seeding need native
    verification. These strings are not a validated complete workspace.
    """
    if not base_node.replace('_','').isalnum():raise ValueError('Invalid base-node identifier')
    controls=[]
    nodes=[]
    child=base_node
    mapping={}
    for index,bone in enumerate(ordered(parents)):
        if not bone.replace('_','').isalnum():raise ValueError('Invalid bone identifier')
        mapping[bone]={}
        for op,component in [('Rotate','rotation_xyz'),('Translate','translation_xyz')]:
            mapping[bone][component]=[]
            for axis in 'XYZ':
                name=f'MLCapturedPose_{index}_{op}_{axis}'
                mapping[bone][component].append(name)
                limit=math.pi if op=='Rotate' else 10
                controls.append(f'AnimSrcGCTVarFloat {name} {{ DefaultValue 0 MinValue {-limit} MaxValue {limit} }}')
                item_id = str(uuid.uuid5(uuid.NAMESPACE_URL, 'movementlab/capturedPose/' + name)).upper()
                nodes.append(f'AnimSrcNodeProcTransform {name}_Node {{\n Child "{child}"\n Expression "{name}"\n Bones {{ AnimSrcNodeProcTrBoneItem "{{{item_id}}}" {{ Bone "{bone}" Axis {axis} Space Model Op {op} Amount 1 }} }}\n}}')
                child=name+'_Node'
    return {'controls':'\n'.join(controls),'nodes':'\n'.join(nodes),'output_node':child,'binding_names':mapping,
            'native_status':'UNVERIFIED graph fragment; no activation/physics handoff included'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('snapshot',type=Path,help='JSON: reference, desired, parents')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    data=json.loads(a.snapshot.read_text())
    corrections=solve(data['reference'],data['desired'],data['parents'])
    check=reconstruct(data['reference'],data['parents'],corrections)
    error=max(abs(check[n][i][j]-data['desired'][n][i][j]) for n in check for i in range(4) for j in range(4))
    a.output.write_text(json.dumps({'corrections':corrections,'reconstruction_max_error':error,'graph':fragment(data['parents'])},indent=2)+'\n')
