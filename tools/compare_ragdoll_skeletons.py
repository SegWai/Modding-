#!/usr/bin/env python3
"""Compare verified collector assets; never load models into an engine.

Reads only the identified ODOL56 skeleton string table, not meshes/rest matrices.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from audit_ragdoll_assets import load_parts


def skeleton(data):
    if data[:8] != b'ODOL' + struct.pack('<I', 56):
        raise ValueError('Only observed ODOL version 56 is supported')
    marker = b'DayzTemporarySkeleton\0'
    if data.count(marker) != 1:
        raise ValueError('Expected one known skeleton marker')
    start = data.index(marker)
    # These collected models place the skeleton in their model-info header.
    if not 32 <= start <= 4096:
        raise ValueError('Skeleton marker outside expected header')
    pos = start + len(marker)
    if pos + 5 > len(data) or data[pos] != 0:
        raise ValueError('Unsupported skeleton flag')
    count = struct.unpack_from('<I', data, pos + 1)[0]
    if not 1 <= count <= 1024:
        raise ValueError('Invalid bone count')
    pos += 5
    bones = []
    for _ in range(count):
        pair = []
        for _ in range(2):
            end = data.find(b'\0', pos, pos + 256)
            if end == -1:
                raise ValueError('Truncated/oversized bone string')
            value = data[pos:end].decode('ascii')
            if value and not re.fullmatch(r'[A-Za-z0-9_]+', value):
                raise ValueError('Invalid bone identifier')
            pair.append(value)
            pos = end + 1
        bones.append(pair)
    if pos >= len(data) or data[pos] != 0:
        raise ValueError('Missing skeleton table terminator')
    names = [name for name, _ in bones]
    if len(set(names)) != count or any(not name for name in names):
        raise ValueError('Duplicate/empty bone')
    parents = dict(bones)
    for name in names:
        seen = set()
        node = name
        while node:
            if node in seen or node not in parents:
                raise ValueError('Cyclic or missing parent')
            seen.add(node)
            node = parents[node]
    return {'marker_offset': start, 'table_end': pos + 1, 'bones': bones}


def ragdoll(text):
    # Brace-aware ancestry, excluding shape properties from each bone's mass.
    tokens = re.findall(r'"[^"\n]*"|[{}]|[^\s{}]+', text)
    stack, bones, pending = [], [], None
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == 'RagdollBone':
            if i + 2 >= len(tokens) or tokens[i + 2] != '{':
                raise ValueError('Invalid ragdoll bone declaration')
            pending = {'name': tokens[i + 1], 'parent': next((x['name'] for x in reversed(stack) if x), '')}
            bones.append(pending)
            i += 2
        elif token == '{':
            stack.append(pending)
            pending = None
            i += 1
        elif token == '}':
            if not stack:
                raise ValueError('Unbalanced ragdoll braces')
            stack.pop()
            i += 1
        elif token == 'Mass' and stack and stack[-1]:
            stack[-1]['mass'] = float(tokens[i + 1])
            i += 2
        else:
            i += 1
    if stack or not bones or any('mass' not in bone for bone in bones):
        raise ValueError('Incomplete ragdoll definition')
    return bones


def compare(paths):
    assets, missing = load_parts(paths)
    if missing:
        raise ValueError('Missing manifest assets')
    models = []
    for name, data in assets.values():
        if name.lower().endswith('.p3d'):
            models.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(), **skeleton(data)})
    models.sort(key=lambda x: x['path'])
    if not models:
        raise ValueError('No models supplied')
    definitions = [(n, d) for n, d in assets.values() if n.lower().endswith('/human.ragdoll')]
    if len(definitions) != 1:
        raise ValueError('Expected one human.ragdoll')
    physics = ragdoll(definitions[0][1].decode('utf-8-sig'))
    for model in models:
        hierarchy = dict(model['bones'])
        model['ragdoll_missing_bones'] = [b['name'] for b in physics if b['name'] not in hierarchy]
        mismatches = []
        for bone in physics:
            if bone['name'] not in hierarchy:
                continue
            node = hierarchy[bone['name']]
            while node and node != bone['parent']:
                node = hierarchy[node]
            if node != bone['parent']:
                mismatches.append(bone['name'])
        model['ragdoll_parent_not_ancestor'] = mismatches
    return {'models': models, 'identical_ordered_names_and_parents': all(m['bones'] == models[0]['bones'] for m in models),
            'ragdoll_bones': physics, 'ragdoll_mass_sum': round(sum(b['mass'] for b in physics), 4),
            'bind_matrices_compared': False, 'native_activation_tested': False,
            'limits': 'Skeleton names/parents alone do not prove bind pose, weights, physics loading or native controller compatibility.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parts', nargs='+', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(compare(args.parts), indent=2) + '\n')
