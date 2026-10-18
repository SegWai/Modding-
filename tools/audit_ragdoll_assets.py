#!/usr/bin/env python3
"""Inspect collector ZIP parts without executing/extracting their contents.

Reports evidence and missing inputs. Does not claim native rig compatibility.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, re, struct, zipfile

MAX_TOTAL = 256 * 1024 * 1024
MAX_ASSET = 18 * 1024 * 1024
MAX_METADATA = 10 * 1024 * 1024


def normalized(name):
    value = name.replace('\\', '/')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or not path.parts or ':' in path.parts[0]:
        raise ValueError('Unsafe archive path: ' + name)
    return path.as_posix()


def group(path):
    path = path.lower()
    if '/zombies/' in path or 'infected' in path or 'zomb' in path:
        return 'infected'
    if '/bodies/' in path or 'player_main' in path or '/human' in path or '/heads/' in path:
        return 'human'
    return 'shared'


def load_parts(paths):
    assets, expected = {}, {}
    total = 0
    for source in paths:
        with zipfile.ZipFile(source) as archive:
            entries = {}
            for info in archive.infolist():
                if info.is_dir() or info.filename.replace('\\', '/').endswith('/'):
                    continue
                name = normalized(info.filename)
                key = name.casefold()
                if key in entries:
                    raise ValueError('Duplicate archive path: ' + name)
                limit = MAX_METADATA if key in ('manifest.json', 'asset-inventory.json') else MAX_ASSET
                if info.file_size > limit:
                    raise ValueError('Oversized archive entry: ' + name)
                total += info.file_size
                if total > MAX_TOTAL:
                    raise ValueError('Input exceeds audit size budget')
                entries[key] = (name, info)
            if 'manifest.json' not in entries:
                raise ValueError('Missing collector manifest in ' + str(source))
            manifest = json.loads(archive.read(entries['manifest.json'][1]).decode('utf-8-sig'))
            if manifest.get('format') != 'MovementLab-Rig-Assets-1':
                raise ValueError('Unsupported manifest format')
            records = manifest.get('files', [])
            if not isinstance(records, list) or len(records) > 10000:
                raise ValueError('Invalid manifest file list')
            current = {}
            for record in records:
                path = normalized(record['path'])
                key = path.casefold()
                if key in current:
                    raise ValueError('Duplicate manifest asset: ' + path)
                current[key] = record
                if key in expected and expected[key]['sha256'] != record['sha256']:
                    raise ValueError('Conflicting manifests for ' + path)
                expected[key] = record
            for key, (name, info) in entries.items():
                if key in ('manifest.json', 'asset-inventory.json'):
                    continue
                if key not in current:
                    raise ValueError('Unlisted asset in archive: ' + name)
                data = archive.read(info)
                record = current[key]
                if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
                    raise ValueError('Asset hash/size mismatch: ' + name)
                if key in assets and assets[key][1] != data:
                    raise ValueError('Conflicting asset contents: ' + name)
                assets[key] = (name, data)
    missing = sorted(record['path'] for key, record in expected.items() if key not in assets)
    return assets, missing


def inspect(paths):
    assets, missing = load_parts(paths)
    report = {'files': [], 'missing_from_uploaded_parts': missing,
              'native_test': 'Not run; collected metadata does not prove rig/physics compatibility.'}
    text_ext = {'.agr', '.agf', '.ast', '.asi', '.cpp', '.cfg', '.xml', '.json', '.phys', '.physics', '.phx', '.skeleton', '.ragdoll'}
    for key, (name, data) in sorted(assets.items()):
        extension = PurePosixPath(key).suffix
        item = {'path': name, 'group': group(key), 'bytes': len(data)}
        if extension == '.p3d':
            magic = data[:4].decode('ascii', errors='replace')
            item['model_format'] = magic
            item['version'] = struct.unpack_from('<I', data, 4)[0] if len(data) >= 8 else None
            item['editable_source_header'] = magic == 'MLOD'
            item['rig_compatibility'] = 'Not established by model header'
        elif extension in text_ext:
            # Do not interpret opaque binary physics/config files as text evidence.
            encoding = 'utf-16' if data[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-8-sig'
            try:
                content = data.decode(encoding)
            except UnicodeError:
                item['opaque_binary'] = True
            else:
                if '\x00' in content:
                    item['opaque_binary'] = True
                else:
                    hits = []
                    for number, line in enumerate(content.splitlines(), 1):
                        if re.search(r'ragdoll|rag_doll|skeleton|physics|physical', line, re.I):
                            hits.append({'line': number, 'text': line[:1200]})
                    item['rig_mentions'] = hits[:150]
                    item['mentions_truncated'] = len(hits) > 150
                    bone_arrays = []
                    for match in re.finditer(r'skeletonBones\s*\[\s*\]\s*=\s*\{(.*?)\}\s*;', content, re.S | re.I):
                        names = re.findall(r'"([^"\n]*)"', match[1])
                        bone_arrays.append({'pairs': list(zip(names[::2], names[1::2])), 'unpaired_token': bool(len(names) % 2)})
                    if bone_arrays:
                        item['source_skeleton_arrays'] = bone_arrays
        elif extension == '.bin':
            item['opaque_binary'] = True
            item['magic_hex'] = data[:4].hex()
        report['files'].append(item)
    report['summary'] = {category: sum(item['group'] == category for item in report['files']) for category in ('human', 'infected', 'shared')}
    models = [item for item in report['files'] if 'model_format' in item]
    report['model_summary'] = {'total': len(models), 'binarized_ODOL': sum(item['model_format'] == 'ODOL' for item in models), 'source_MLOD': sum(item['model_format'] == 'MLOD' for item in models)}
    next_steps = []
    if missing:
        next_steps.append('Upload the remaining collector ZIP parts; this audit is incomplete.')
    if not report['summary']['infected']:
        next_steps.append('Infected assets are missing; inspect the collector asset-name inventory and extraction location.')
    if not report['summary']['human']:
        next_steps.append('Human comparison assets are missing; collect the native player_main workspace/body data.')
    if models and not report['model_summary']['source_MLOD']:
        next_steps.append('Collected models are not editable MLOD sources. Editable/custom rig work may require source assets; a header alone does not establish that conversion is possible.')
    if not any('source_skeleton_arrays' in item for item in report['files']):
        next_steps.append('No source skeletonBones arrays found. They may be embedded in binarized data; absence here does not prove the engine lacks a rig.')
    next_steps.append('Compare actual skeleton/bind and physics definitions in DayZ Tools, then test a compatible corpse rig in the native game. Do not infer ragdoll support from death-animation names.')
    report['next_steps'] = next_steps
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parts', type=Path, nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.parts)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'summary': report['summary'], 'models': report['model_summary'], 'missing_entries': len(report['missing_from_uploaded_parts'])}))


if __name__ == '__main__':
    main()
