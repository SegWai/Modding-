"""Package the generated walk study with its separate editor preview."""

import argparse
import json
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generated', required=True, type=Path)
    parser.add_argument('--revision', choices=('v01', 'v02', 'v03', 'v04', 'v05', 'v06', 'v07'), default='v01')
    args = parser.parse_args()
    clip_name = 'MovementLab_Unarmed_Walk_' + args.revision
    report = json.loads((args.generated / 'validation.json').read_text())
    cycle, fps = report['cycle_frames'], report['fps']
    sampled = list(range(0, cycle, 2))
    boundaries = [round(frame/fps*100)*10 for frame in sampled + [cycle]]
    delays = [b-a for a, b in zip(boundaries, boundaries[1:])]
    # GIF timing uses centiseconds; distribute rounding over the whole loop.
    frames = [Image.open(args.generated / 'frames' / f'walk_{n:03d}.png').convert('RGB')
              for n in sampled]
    frames[0].save(args.generated / 'preview_walk.gif', save_all=True,
                   append_images=frames[1:], duration=delays, loop=0)
    sheet = Image.new('RGB', (384*4, 408), '#20242a')
    draw = ImageDraw.Draw(sheet)
    for column, frame in enumerate((0, 8, 18, 26)):
        sheet.paste(frames[frame//2], (column*384, 24))
        draw.text((column*384+12, 6), f'Frame {frame}', fill='white')
    sheet.save(args.generated / 'preview_contact_sheet.png')
    with Image.open(args.generated / 'preview_walk.gif') as preview:
        assert preview.n_frames == len(sampled)
        duration = 0
        for frame in range(preview.n_frames):
            preview.seek(frame)
            duration += preview.info['duration']
        assert duration == boundaries[-1]
    files = {}
    source = ROOT / ('walk-test' if args.revision == 'v01' else 'walk-test-' + args.revision)
    for path in sorted(source.rglob('*')):
        if path.is_file():
            files[path.relative_to(source).as_posix()] = path.read_bytes()
    for extension in ('.blend', '.txa'):
        files['TestAnimations/' + clip_name + extension] = (args.generated / (clip_name+extension)).read_bytes()
    for name in ('validation.json', 'preview_walk.gif', 'preview_contact_sheet.png'):
        files[name] = (args.generated / name).read_bytes()
    if args.revision != 'v01':
        side = [Image.open(args.generated / 'frames_side' / f'walk_{n:03d}.png').convert('RGB')
                for n in sampled]
        side[0].save(args.generated / 'preview_walk_side.gif', save_all=True,
                     append_images=side[1:], duration=delays, loop=0)
        files['preview_walk_side.gif'] = (args.generated / 'preview_walk_side.gif').read_bytes()
    if args.revision in ('v04', 'v05', 'v06', 'v07'):
        rear = [Image.open(args.generated / 'frames_rear' / f'walk_{n:03d}.png').convert('RGB')
                for n in sampled]
        rear[0].save(args.generated / 'preview_walk_rear.gif', save_all=True,
                     append_images=rear[1:], duration=delays, loop=0)
        files['preview_walk_rear.gif'] = (args.generated / 'preview_walk_rear.gif').read_bytes()
    for name in ('build_walk_clip.py', 'build_diagnostic_clip.py', 'render_walk_preview.py', 'package_walk_test.py'):
        files['Source/' + name] = (ROOT / 'tools' / name).read_bytes()
    if args.revision != 'v01':
        builder = 'build_walk_clip_' + args.revision + '.py'
        files['Source/' + builder] = (ROOT / 'tools' / builder).read_bytes()
    with zipfile.ZipFile(ROOT / 'artifacts/MovementLab_ArmLift_Test.zip') as original:
        for name in ('ASSET_NOTICES.txt', 'EXPORTER_LICENSE.txt'):
            files[name] = original.read(name)
    files['ASSET_NOTICES.txt'] = files['ASSET_NOTICES.txt'].replace(
        b'Original diagnostic arm-lift keyframes and authoring script:',
        b'Original walking-study keyframes and authoring script:').replace(
        b'adding new procedural arm-lift keyframes',
        b'adding new procedural walking keyframes and preview lighting')
    destination = ROOT / 'artifacts' / ('MovementLab_Unarmed_Walk_' + args.revision + '.zip')
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name, data in sorted(files.items()):
            if name.endswith('.txt'):
                data = data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 9, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, data, compresslevel=9)
    with zipfile.ZipFile(destination) as bundle:
        assert bundle.testzip() is None
        assert len(bundle.namelist()) == len(set(bundle.namelist()))
        assert not any(Path(name).is_absolute() or '..' in Path(name).parts for name in bundle.namelist())
    print(f'Packaged {len(files)} files: {destination.name} ({destination.stat().st_size} bytes)')
    print('Walking ANM compilation and native pace matching remain Windows checks.')


if __name__ == '__main__':
    main()
