"""Build a DayZ full-body import test with Blender 4.3.2.

Run with Blender in background mode; dependencies are explicit local paths.
This creates original keyframes on a reference rig, not a gameplay movement mod.
"""

import argparse
import importlib
import json
import math
from pathlib import Path
import re
import sys

import bpy
from mathutils import Quaternion, Vector


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rig', required=True, type=Path)
    parser.add_argument('--addon-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    return parser.parse_args(sys.argv[sys.argv.index('--') + 1:])


def rig_axis_quaternion(bone, axis, angle):
    """Turn around an armature-space axis, expressed in this bone's local axes."""
    local_axis = bone.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
    return Quaternion(local_axis.normalized(), angle)


def validate(txa, rig):
    animations = list(txa.animations.values())
    assert len(animations) == 1
    animation = animations[0]
    assert animation.fps == 30 and animation.numFrames == 121
    nodes = {}

    def visit(name, node):
        assert name not in nodes, f'Duplicate node: {name}'
        nodes[name] = node
        for key in node.keyframes:
            assert 0 <= key.frameStart <= key.frameEnd < animation.numFrames
            if key.HasTranslation():
                assert all(math.isfinite(v) for v in key.translation.toTuple())
            if key.HasRotation():
                q = key.rotation.toTuple()
                assert all(math.isfinite(v) for v in q)
                assert abs(sum(v * v for v in q) - 1) < 0.001
        for child_name, child in node.children.items():
            visit(child_name, child)

    for name, node in animation.rootBones.items():
        visit(name, node)
    assert set(nodes) == set(rig.pose.bones.keys()) | {'Scene_Root'}
    assert len(nodes['RightArm'].keyframes) > 30
    first, last = nodes['RightArm'].keyframes[0], nodes['RightArm'].keyframes[-1]
    assert first.HasRotation() and last.HasRotation()
    dot = sum(a * b for a, b in zip(first.rotation.toTuple(), last.rotation.toTuple()))
    assert abs(abs(dot) - 1) < 0.001
    return {'fps': 30, 'frames': 121, 'nodes': len(nodes), 'loop_endpoints_match': True}


def main():
    args = arguments()
    args.output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.rig.resolve()), use_scripts=False)
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # The reference blend contains camera rigs and control shapes. Retain only
    # the character's armature and its skinned body for a small editable file.
    rig = bpy.data.objects['_DayZ_Character']
    body = bpy.data.objects['zMale_body']
    for obj in list(bpy.data.objects):
        if obj not in (rig, body):
            bpy.data.objects.remove(obj, do_unlink=True)
    for bone in rig.pose.bones:
        bone.rotation_mode = 'QUATERNION'
        bone.location = (0, 0, 0)
        bone.rotation_quaternion = (1, 0, 0, 0)
        bone.scale = (1, 1, 1)
        bone.custom_shape = None
        for constraint in list(bone.constraints):
            bone.constraints.remove(constraint)
    for obj in (rig, body):
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False

    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    rig.animation_data_clear()
    rig.animation_data_create()
    action = bpy.data.actions.new('MovementLab_ArmLift_Test')
    rig.animation_data.action = action
    action.use_fake_user = True
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 0
    scene.frame_end = 120

    # A deliberately obvious, four-second loop: arms rest at the sides,
    # right arm rises and returns. Legs and root remain stationary so the
    # test does not depend on locomotion, footstep events, or root motion.
    for frame in range(121):
        phase = frame / 120
        lift = (1 - math.cos(2 * math.pi * phase)) / 2
        angles = {
            'LeftArm': math.radians(36),
            'RightArm': math.radians(-36 + 75 * lift),
        }
        for name, angle in angles.items():
            bone = rig.pose.bones[name]
            bone.rotation_quaternion = rig_axis_quaternion(bone, (0, 1, 0), angle)
            bone.keyframe_insert('rotation_quaternion', frame=frame)
    for curve in action.fcurves:
        for key in curve.keyframe_points:
            key.interpolation = 'LINEAR'
    scene.frame_set(0)

    # The current addon exporter reads evaluated poses and does not use the
    # newer Action API required by its importer. No addon installation needed.
    sys.path.insert(0, str(args.addon_root.resolve()))
    exporter = importlib.import_module('DayzAnimationTools.Export.ExportTxa')
    types = importlib.import_module('DayzAnimationTools.Types.Txa')
    settings = types.TxaExportSettings()
    settings.bSaveAll = False
    filepath = args.output / 'MovementLab_ArmLift_Test.txa'
    operator = type('ExportRequest', (), {'filepath': str(filepath)})()
    error = exporter.save(operator, bpy.context, settings)
    if error:
        raise RuntimeError(error)
    # Explicit single-frame ranges also round-trip through addon versions that
    # leave frameEnd at zero when the optional second number is omitted.
    text = filepath.read_text()
    text = re.sub(r'\$frame (\d+) \{', r'$frame \1 \1 {', text)
    filepath.write_text(text)
    report = validate(types.Txa.CreateFromFile(str(filepath)), rig)

    # Measure the evaluated pose too, rather than only checking text output.
    positions = {}
    for frame in (0, 60, 120):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        positions[frame] = {name: list(rig.pose.bones[name].head)
                            for name in ('RightHand', 'LeftFoot', 'RightFoot')}
    assert positions[60]['RightHand'][2] - positions[0]['RightHand'][2] > 0.2
    for name in ('LeftFoot', 'RightFoot'):
        assert (Vector(positions[60][name]) - Vector(positions[0][name])).length < 1e-6
    assert (Vector(positions[120]['RightHand']) - Vector(positions[0]['RightHand'])).length < 1e-5
    report['pose_checks'] = 'right hand rises; feet fixed; start/end match'
    report['blender_version'] = bpy.app.version_string
    report['workbench_compilation'] = 'pending user test on Windows'
    report['in_game_test'] = 'not performed'
    (args.output / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')

    scene.frame_set(0)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output / 'MovementLab_ArmLift_Test.blend'))
    print('DIAGNOSTIC_CLIP_RESULT', json.dumps(report))


if __name__ == '__main__':
    main()
