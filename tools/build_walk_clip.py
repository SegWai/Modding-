"""Author an original in-place DayZ walking study in Blender 4.3.2.

No vanilla motion is sampled. Native locomotion speed/slots must be checked
separately on Windows before this study is used as a gameplay replacement.
"""

import importlib
import json
import math
from pathlib import Path
import re
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_diagnostic_clip import arguments, rig_axis_quaternion

NAME = 'MovementLab_Unarmed_Walk_v01'
FPS = 30
CYCLE = 36
DURATION = CYCLE / FPS
SPEED = 0.80  # Authoring reference only; not a change to DayZ movement speed.
STANCE = 0.60


def foot_path(phase):
    distance = SPEED * DURATION * STANCE
    if phase < STANCE:
        return -distance / 2 + SPEED * DURATION * phase, 0.0
    t = (phase - STANCE) / (1 - STANCE)
    smooth = 10 * t**3 - 15 * t**4 + 6 * t**5
    # Match the stance velocity at both contacts, avoiding a position/velocity
    # jump. The swing foot lifts with zero vertical velocity at the contacts.
    y = distance / 2 - distance * smooth
    y += SPEED * DURATION * (1 - STANCE) * (t - smooth)
    return y, 0.075 * math.sin(math.pi * t)**2


def aim_joint(bone, origin, rest_segment, posed_segment):
    rotation = rest_segment.normalized().rotation_difference(posed_segment.normalized())
    bone.matrix = Matrix.Translation(origin) @ rotation.to_matrix().to_4x4() @ bone.bone.matrix_local.to_3x3().to_4x4()
    bpy.context.view_layer.update()


def solve_leg(rig, side, target):
    thigh, shin, foot = [rig.pose.bones[side + suffix] for suffix in ('UpLeg', 'Leg', 'Foot')]
    upper = shin.bone.head_local - thigh.bone.head_local
    lower = foot.bone.head_local - shin.bone.head_local
    hip = thigh.head.copy()
    delta = target - hip
    distance = delta.length
    a, b = upper.length, lower.length
    assert abs(a - b) < distance < a + b - 0.001, f'Unreachable {side} ankle at frame {bpy.context.scene.frame_current}: {distance} vs {a+b}; hip {tuple(hip)}, target {tuple(target)}'
    axis = delta.normalized()
    forward = Vector((0, -1, 0))
    bend = (forward - axis * forward.dot(axis)).normalized()
    along = (a*a - b*b + distance*distance) / (2*distance)
    height = math.sqrt(max(0, a*a - along*along))
    knee = hip + axis * along + bend * height
    aim_joint(thigh, hip, upper, knee - hip)
    aim_joint(shin, knee, lower, target - knee)
    # Hold the foot's rest orientation. Contact feet remain flat; swing feet
    # clear the ground. Toe roll is reserved for a later contact refinement.
    foot.matrix = Matrix.Translation(target) @ foot.bone.matrix_local.to_3x3().to_4x4()
    bpy.context.view_layer.update()
    assert (foot.head - target).length < 0.0001


def validate_export(animation, rig):
    assert animation.fps == FPS and animation.numFrames == CYCLE + 1
    nodes = {}

    def visit(name, node):
        assert name not in nodes
        nodes[name] = node
        for key in node.keyframes:
            assert 0 <= key.frameStart <= key.frameEnd <= CYCLE
            if key.HasTranslation():
                assert all(math.isfinite(v) for v in key.translation.toTuple())
            if key.HasRotation():
                q = key.rotation.toTuple()
                assert all(math.isfinite(v) for v in q)
                assert abs(sum(v*v for v in q) - 1) < 0.001
        for child_name, child in node.children.items():
            visit(child_name, child)

    for name, node in animation.rootBones.items():
        visit(name, node)
    assert set(nodes) == set(rig.pose.bones.keys()) | {'Scene_Root'}
    for side in ('Left', 'Right'):
        assert len(nodes[side + 'UpLeg'].keyframes) > CYCLE // 2
    return len(nodes)


def main():
    args = arguments()
    args.output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.rig.resolve()), use_scripts=False)
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    rig = bpy.data.objects['_DayZ_Character']
    body = bpy.data.objects['zMale_body']
    for obj in list(bpy.data.objects):
        if obj not in (rig, body):
            bpy.data.objects.remove(obj, do_unlink=True)
    for obj in (rig, body):
        obj.hide_set(False)
        obj.hide_viewport = obj.hide_render = False
    for bone in rig.pose.bones:
        bone.rotation_mode = 'QUATERNION'
        bone.custom_shape = None
        for constraint in list(bone.constraints):
            bone.constraints.remove(constraint)
    rig.animation_data_clear()
    rig.animation_data_create()
    action = bpy.data.actions.new(NAME)
    action.use_fake_user = True
    rig.animation_data.action = action
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 0, CYCLE - 1
    samples, matrices = [], []
    animated = ['Pelvis', 'Spine', 'Spine2', 'LeftArm', 'RightArm',
                'LeftForeArm', 'RightForeArm']
    animated += [side + suffix for side in ('Left', 'Right') for suffix in ('UpLeg', 'Leg', 'Foot')]
    for frame in range(CYCLE + 1):
        scene.frame_set(frame)
        for bone in rig.pose.bones:
            bone.matrix_basis = Matrix.Identity(4)
        phase = frame / CYCLE
        angle = 2 * math.pi * phase
        pelvis = rig.pose.bones['Pelvis']
        pelvis.location = pelvis.bone.matrix_local.to_3x3().inverted() @ Vector((
            0.018 * math.sin(angle), 0, -0.065 + 0.009 * math.cos(2*angle)))
        pelvis.rotation_quaternion = rig_axis_quaternion(pelvis, (0, 0, 1), math.radians(2)*math.sin(angle)) @ rig_axis_quaternion(pelvis, (0, 1, 0), math.radians(1.2)*math.sin(angle))
        spine = rig.pose.bones['Spine']
        spine.rotation_quaternion = rig_axis_quaternion(spine, (1, 0, 0), math.radians(3))
        spine2 = rig.pose.bones['Spine2']
        spine2.rotation_quaternion = rig_axis_quaternion(spine2, (0, 0, 1), -math.radians(3.5)*math.sin(angle))
        for side, offset, sign in (('Left', 0, 1), ('Right', 0.5, -1)):
            p = (phase + offset) % 1
            arm = rig.pose.bones[side+'Arm']
            arm.rotation_quaternion = rig_axis_quaternion(arm, (1, 0, 0), -math.radians(13)*math.cos(2*math.pi*p)) @ rig_axis_quaternion(arm, (0, 1, 0), sign*math.radians(36))
            forearm = rig.pose.bones[side+'ForeArm']
            forearm.rotation_quaternion = rig_axis_quaternion(forearm, (1, 0, 0), math.radians(9 + 3*math.sin(2*math.pi*p)))
        bpy.context.view_layer.update()
        contact = {}
        for side, offset, sign in (('Left', 0, 1), ('Right', 0.5, -1)):
            p = (phase + offset) % 1
            y, lift = foot_path(p)
            target = Vector((sign*0.135, y, rig.data.bones[side+'Foot'].head_local.z + lift))
            solve_leg(rig, side, target)
            contact[side] = {'phase': p, 'stance': p < STANCE, 'ankle': list(rig.pose.bones[side+'Foot'].head)}
        for name in animated:
            bone = rig.pose.bones[name]
            assert max(abs(s - 1) for s in bone.scale) < 0.0001
            bone.keyframe_insert('location', frame=frame)
            bone.keyframe_insert('rotation_quaternion', frame=frame)
        samples.append(contact)
        matrices.append({b.name: b.matrix.copy() for b in rig.pose.bones})
    for curve in action.fcurves:
        for key in curve.keyframe_points:
            key.interpolation = 'LINEAR'
    endpoint_error = max(abs(matrices[0][name][i][j] - matrices[-1][name][i][j])
                         for name in matrices[0] for i in range(4) for j in range(4))
    assert endpoint_error < 0.0001
    drift = 0
    for side in ('Left', 'Right'):
        for frame in range(1, CYCLE):
            prev, now = samples[frame-1][side], samples[frame][side]
            if prev['stance'] and now['stance'] and now['phase'] > prev['phase']:
                step = Vector(now['ankle']) - Vector(prev['ankle']) - Vector((0, SPEED/FPS, 0))
                drift = max(drift, step.length)
        assert max(s[side]['ankle'][2] for s in samples) - min(s[side]['ankle'][2] for s in samples) > 0.07
    assert drift < 0.0001
    for frame in range(CYCLE+1):
        assert (matrices[frame]['EntityPosition'].translation - matrices[0]['EntityPosition'].translation).length < 0.00001
    replay_error = 0
    for frame in range(CYCLE+1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        for bone in rig.pose.bones:
            replay_error = max(replay_error, max(abs(bone.matrix[i][j] - matrices[frame][bone.name][i][j])
                                               for i in range(4) for j in range(4)))
    assert replay_error < 0.0001, 'Baked action differs from authored poses'
    sys.path.insert(0, str(args.addon_root.resolve()))
    exporter = importlib.import_module('DayzAnimationTools.Export.ExportTxa')
    types = importlib.import_module('DayzAnimationTools.Types.Txa')
    path = args.output / (NAME+'.txa')
    settings = types.TxaExportSettings()
    settings.bSaveAll = False
    error = exporter.save(type('ExportRequest', (), {'filepath': str(path)})(), bpy.context, settings)
    if error:
        raise RuntimeError(error)
    path.write_text(re.sub(r'\$frame (\d+) \{', r'$frame \1 \1 {', path.read_text()))
    nodes = validate_export(list(types.Txa.CreateFromFile(str(path)).animations.values())[0], rig)
    report = {'name': NAME, 'blender_version': bpy.app.version_string,
              'fps': FPS, 'cycle_frames': CYCLE, 'exported_frames_with_duplicate_endpoint': CYCLE+1,
              'duration_seconds': DURATION, 'nominal_speed_m_s': SPEED,
              'nominal_distance_per_cycle_m': SPEED*DURATION, 'stance_fraction': STANCE,
              'foot_clearance_m': 0.075, 'forward_axis': '-Y in Blender armature space',
              'nodes': nodes, 'endpoint_matrix_max_error': endpoint_error,
              'baked_action_matrix_max_error': replay_error,
              'max_stance_drift_per_frame_with_nominal_travel_m': drift,
              'root_motion': 'in-place; EntityPosition stationary',
              'workbench_compilation': 'pending Windows test', 'in_game_test': 'not performed',
              'limitations': 'Flat-foot first study; no native pace, footstep events, transitions, or blend compatibility validated.'}
    (args.output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    scene.frame_set(0)
    scene['MovementLab_notes'] = 'Original walk study. Loop Blender frames 0–35; frame 36 duplicates frame 0 for TXA continuity. Nominal 0.80 m/s only; native speed not yet matched.'
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output/(NAME+'.blend')))
    print('WALK_CLIP_RESULT', json.dumps(report))


if __name__ == '__main__':
    main()
