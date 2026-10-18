#!/usr/bin/env python3
"""Read the observed XOB6 node layout. No mesh loading, editing or execution.

The format interpretation is inferred from the supplied assets, not an official
XOB specification. All tree, range, chunk and quaternion checks must pass.
"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from audit_ragdoll_assets import load_parts
from compare_ragdoll_skeletons import ragdoll


def read_xob(data):
    if len(data) < 80 or data[:4] != b'FORM' or data[8:12] != b'XOB6':
        raise ValueError('Expected XOB6 FORM')
    if struct.unpack_from('>I', data, 4)[0] + 8 != len(data):
        raise ValueError('FORM length mismatch')
    chunks = {}
    pos = 12
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError('Truncated chunk')
        tag = data[pos:pos + 4].decode('ascii')
        size = struct.unpack_from('>I', data, pos + 4)[0]
        end = pos + 8 + size
        if end > len(data) or tag in chunks:
            raise ValueError('Invalid/duplicate chunk')
        chunks[tag] = (pos + 8, end)
        pos = end
    if chunks.get('HEAD', (None,))[0] != 20:
        raise ValueError('Unexpected HEAD layout')
    materials, count = struct.unpack_from('<HH', data, 64)
    size = struct.unpack_from('<I', data, 76)[0]
    end = 80 + size
    start = end + 2 * materials
    if not 1 <= count <= 2048 or not 1 <= materials <= 256 or end > chunks['HEAD'][1] or start + count * 36 > chunks['HEAD'][1]:
        raise ValueError('Node table outside HEAD')
    if size < 1 or data[end - 1] != 0:
        raise ValueError('Unterminated string table')
    strings = data[80:end].split(b'\0')[:-1]
    rows = []
    for index in range(count):
        row = struct.unpack_from('<I7fHH', data, start + index * 36)
        name_index, values, sibling, child = row[0], row[1:8], row[8], row[9]
        if name_index >= len(strings) or not all(math.isfinite(x) for x in values):
            raise ValueError('Invalid node name/transform')
        if abs(sum(x*x for x in values[3:]) - 1) > .001:
            raise ValueError('Nonunit node quaternion')
        if any(x != 65535 and x >= count for x in (sibling, child)):
            raise ValueError('Node link out of range')
        rows.append({'name': strings[name_index].decode('ascii'), 'translation': list(values[:3]),
                     'quaternion_xyzw': list(values[3:]), 'sibling': sibling, 'child': child})
    if len({r['name'].lower() for r in rows}) != count or rows[0]['sibling'] != 65535:
        raise ValueError('Duplicate names or multiple roots')
    parents = {0: None}
    pending = [(rows[0]['child'], 0)]
    while pending:
        node, parent = pending.pop()
        if node == 65535:
            continue
        if node in parents:
            raise ValueError('Cyclic/shared node')
        parents[node] = parent
        pending.append((rows[node]['sibling'], parent))
        pending.append((rows[node]['child'], node))
    if len(parents) != count:
        raise ValueError('Unreachable nodes')
    for i, row in enumerate(rows):
        row['parent'] = None if parents[i] is None else rows[parents[i]]['name']
        del row['sibling'], row['child']
    return {'node_count': count, 'chunks': chunks, 'node_table_offset': start, 'nodes': rows}


def qmul(a, b):
    x, y, z, w = a
    X, Y, Z, W = b
    return (w*X+x*W+y*Z-z*Y, w*Y-x*Z+y*W+z*X,
            w*Z+x*Y-y*X+z*W, w*W-x*X-y*Y-z*Z)


def world_nodes(rig):
    nodes = {n['name'].lower(): n for n in rig['nodes']}
    result = {}
    # Parent-first evaluation without recursive tree assumptions.
    pending = list(nodes)
    while pending:
        deferred = []
        for key in pending:
            n = nodes[key]
            parent = n['parent'].lower() if n['parent'] else None
            if parent is not None and parent not in result:
                deferred.append(key)
                continue
            q = n['quaternion_xyzw']
            norm = math.sqrt(sum(v*v for v in q))
            q = tuple(v/norm for v in q)
            t = n['translation']
            if parent is not None:
                pt, pq = result[parent]
                rotated = qmul(qmul(pq, (*t, 0)), (-pq[0], -pq[1], -pq[2], pq[3]))
                t = tuple(a+b for a, b in zip(pt, rotated[:3]))
                q = qmul(pq, q)
            result[key] = (t, q)
        if len(deferred) == len(pending):
            raise ValueError('Unresolvable parent tree')
        pending = deferred
    return result


def compare(parts):
    assets, missing = load_parts(parts)
    if missing:
        raise ValueError('Incomplete collector upload')
    rigs = {name.lower(): {'sha256': hashlib.sha256(data).hexdigest(), **read_xob(data)}
            for name, data in assets.values() if name.lower().endswith('.xob')}
    human_key = 'dz/anims/workspaces/player/models/player_m_editorpreview.xob'
    infected_key = 'dz/characters/zombies/z_hermit_m.xob'
    human, infected = rigs[human_key], rigs[infected_key]
    hw, zw = world_nodes(human), world_nodes(infected)
    hn = {n['name'].lower(): n for n in human['nodes']}
    zn = {n['name'].lower(): n for n in infected['nodes']}
    physical = ragdoll(assets['dz/characters/bodies/human.ragdoll'][1].decode())
    results = []
    for b in physical:
        key = b['name']
        if key not in hw or key not in zw:
            raise ValueError('Missing physical bone: ' + key)
        ht, hq = hw[key]
        zt, zq = zw[key]
        dot = min(1, abs(sum(a*b for a, b in zip(hq, zq))))
        results.append({'bone': key, 'human_parent': hn[key]['parent'], 'infected_parent': zn[key]['parent'],
                        'human_position': ht, 'infected_position': zt,
                        'position_delta': math.dist(ht, zt),
                        'rotation_delta_degrees': math.degrees(2*math.acos(dot))})
    return {'verified_asset_count': len(assets), 'rigs': rigs, 'physical_bone_comparison': results,
            'interpretation': 'Observed XOB6 node TR + XYZW quaternion, parent composition; inferred format, not official specification.',
            'native_activation_tested': False, 'mesh_weights_decoded': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parts', type=Path, nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(compare(args.parts), indent=2) + '\n')
