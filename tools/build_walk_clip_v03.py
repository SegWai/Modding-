"""Revise the walk's support alignment and reduce knee-driven body dipping.

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

NAME = 'MovementLab_Unarmed_Walk_v03'
FPS = 30
CYCLE = 36
DURATION = CYCLE / FPS
SPEED = 0.90  # Authoring reference only; not a change to DayZ movement speed.
STANCE = 0.62


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return 10*t**3 - 15*t**4 + 6*t**5


def foot_path(phase):
    distance = SPEED * DURATION * STANCE
    if phase < STANCE:
        return -distance / 2 + SPEED * DURATION * phase, 0.0
    t = (phase - STANCE) / (1 - STANCE)
    smooth = smoothstep(t)
    # Match the stance velocity at both contacts, avoiding a position/velocity
    # jump. The swing foot lifts with zero vertical velocity at the contacts.
    y = distance / 2 - distance * smooth
    y += SPEED * DURATION * (1 - STANCE) * (t - smooth)
    # Pick the foot up soon after toe-off, then lower it more gradually.
    # This avoids a nearly locked rear knee during the start of swing.
    lift = smoothstep(t/0.35) if t < 0.35 else 1-smoothstep((t-0.35)/0.65)
    return y, 0.070 * lift


def foot_roll(phase):
    """Foot angle, contact pivot, and toe flex for a heel-to-toe step.

    Pivot coordinates are relative to the ankle in the rig's rest axes.
    Positive pitch lowers the toes; negative pitch raises them.
    """
    heel = Vector((0, 0.055, -0.104))
    ball = Vector((0, -0.149, -0.104))
    if phase < STANCE:
        t = phase / STANCE
        if t < 0.18:
            pitch = -math.radians(14)*(1-smoothstep(t/0.18))
            return pitch, heel, 0.0, 'heel'
        if t < 0.58:
            return 0.0, heel, 0.0, 'flat'
        pitch = math.radians(30)*smoothstep((t-0.58)/0.42)
        return pitch, ball, -pitch, 'ball'
    t = (phase-STANCE)/(1-STANCE)
    pitch = math.radians(30) - math.radians(44)*smoothstep(t)
    pivot = ball.lerp(heel, smoothstep(t))
    # Toe flex relaxes after leaving the ground; toes rise for heel strike.
    toe_flex = -math.radians(30)*(1-smoothstep(t/0.35))
    return pitch, pivot, toe_flex, 'swing'


def aim_joint(bone, origin, rest_segment, posed_segment):
    rotation = rest_segment.normalized().rotation_difference(posed_segment.normalized())
    bone.matrix = Matrix.Translation(origin) @ rotation.to_matrix().to_4x4() @ bone.bone.matrix_local.to_3x3().to_4x4()
    bpy.context.view_layer.update()


def solve_leg(rig, side, target, foot_rotation):
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
    foot.matrix = Matrix.Translation(target) @ foot_rotation.to_matrix().to_4x4() @ foot.bone.matrix_local.to_3x3().to_4x4()
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
    animated = ['Pelvis', 'Spine', 'Spine2', 'Head', 'LeftArm', 'RightArm',
                'LeftForeArm', 'RightForeArm']
    animated += [side + suffix for side in ('Left', 'Right') for suffix in ('UpLeg', 'Leg', 'Foot', 'ToeBase')]
    for frame in range(CYCLE + 1):
        scene.frame_set(frame)
        for bone in rig.pose.bones:
            bone.matrix_basis = Matrix.Identity(4)
        phase = frame / CYCLE
        angle = 2 * math.pi * phase
        pelvis = rig.pose.bones['Pelvis']
        pelvis.location = pelvis.bone.matrix_local.to_3x3().inverted() @ Vector((
            0.018 * math.sin(angle), 0.004*math.sin(2*angle), -0.014 - 0.009 * math.cos(2*angle)))
        pelvis.rotation_quaternion = rig_axis_quaternion(pelvis, (0, 0, 1), -math.radians(4)*math.cos(angle)) @ rig_axis_quaternion(pelvis, (0, 1, 0), -math.radians(1.5)*math.sin(angle))
        spine = rig.pose.bones['Spine']
        spine.rotation_quaternion = rig_axis_quaternion(spine, (1, 0, 0), math.radians(2))
        spine2 = rig.pose.bones['Spine2']
        spine2.rotation_quaternion = rig_axis_quaternion(spine2, (0, 0, 1), math.radians(7)*math.cos(angle))
        head = rig.pose.bones['Head']
        head.rotation_quaternion = rig_axis_quaternion(head, (0, 0, 1), -math.radians(3)*math.cos(angle)) @ rig_axis_quaternion(head, (1, 0, 0), -math.radians(0.6)*math.cos(2*angle))
        for side, offset, sign in (('Left', 0, 1), ('Right', 0.5, -1)):
            p = (phase + offset) % 1
            arm = rig.pose.bones[side+'Arm']
            # A forward leg pairs with the opposite forward arm. +X rotation
            # moves a hanging hand BACK in this rig; v01 had this sign reversed.
            swing = math.cos(2*math.pi*(p-0.035))
            arm.rotation_quaternion = rig_axis_quaternion(arm, (1, 0, 0), math.radians(24)*swing) @ rig_axis_quaternion(arm, (0, 1, 0), sign*math.radians(43))
            bpy.context.view_layer.update()
            forearm = rig.pose.bones[side+'ForeArm']
            # Use the posed axes so elbow flex stays in the walking plane
            # after lowering the arms from the reference rig's spread pose.
            elbow_axis = forearm.matrix.to_3x3().inverted() @ Vector((1, 0, 0))
            forearm.rotation_quaternion = Quaternion(elbow_axis.normalized(), -math.radians(8 + 10*(1-swing)/2))
        bpy.context.view_layer.update()
        contact = {}
        for side, offset, sign in (('Left', 0, 1), ('Right', 0.5, -1)):
            p = (phase + offset) % 1
            y, lift = foot_path(p)
            pitch, pivot, toe_flex, mode = foot_roll(p)
            rotation = Quaternion(Vector((1, 0, 0)), pitch)
            # The reference ankle sits behind the pelvis, with the forefoot
            # extending forward beneath it. Preserve that support alignment:
            # centering the ANKLE on the pelvis forced excessive knee flexion.
            rest_ankle = rig.data.bones[side+'Foot'].head_local
            reference = Vector((sign*0.125, rest_ankle.y + y, rest_ankle.z + lift))
            target = reference + pivot - rotation @ pivot
            solve_leg(rig, side, target, rotation)
            toe = rig.pose.bones[side+'ToeBase']
            toe.rotation_quaternion = rig_axis_quaternion(toe, (1, 0, 0), toe_flex)
            bpy.context.view_layer.update()
            # Recover the contact marker from the evaluated foot, not the
            # target alone. Within each contact phase its ground point is fixed
            # after compensating nominal root travel. Ankle motion is allowed.
            foot = rig.pose.bones[side+'Foot']
            local_pivot = foot.bone.matrix_local.to_3x3().inverted() @ pivot
            marker = foot.matrix @ local_pivot
            upper = rig.pose.bones[side+'Leg'].head - rig.pose.bones[side+'UpLeg'].head
            lower = foot.head - rig.pose.bones[side+'Leg'].head
            knee_bend = math.degrees(math.acos(max(-1, min(1, upper.normalized().dot(lower.normalized())))))
            contact[side] = {'phase': p, 'stance': p < STANCE, 'mode': mode,
                             'contact_reference': list(marker-pivot),
                             'ankle': list(foot.head), 'hand': list(rig.pose.bones[side+'Hand'].head),
                             'pitch_degrees': math.degrees(pitch), 'knee_bend_degrees': knee_bend}
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
                step = Vector(now['contact_reference']) - Vector(prev['contact_reference']) - Vector((0, SPEED/FPS, 0))
                drift = max(drift, step.length)
        assert max(s[side]['ankle'][2] for s in samples) - min(s[side]['ankle'][2] for s in samples) > 0.06
        hand_travel = max(s[side]['hand'][1] for s in samples) - min(s[side]['hand'][1] for s in samples)
        assert hand_travel > 0.40, f'{side} hand swing too small: {hand_travel}'
        assert samples[0][side]['hand'][1] * (-1 if side == 'Right' else 1) > 0
    assert drift < 0.0001
    pelvis_heights = [matrix['Pelvis'].translation.z for matrix in matrices]
    pelvis_dip = max(pelvis_heights) - min(pelvis_heights)
    assert pelvis_dip < 0.020, f'Body dip too large: {pelvis_dip}'
    flat_stance_knees = {side: [s[side]['knee_bend_degrees'] for s in samples
                               if s[side]['mode'] == 'flat'] for side in ('Left', 'Right')}
    assert max(max(values) for values in flat_stance_knees.values()) < 30
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
    minimum_ground_z = float('inf')
    for sample in range(2*CYCLE+1):
        scene.frame_set(sample//2, subframe=(sample % 2)/2)
        bpy.context.view_layer.update()
        evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        minimum_ground_z = min(minimum_ground_z, min(v.co.z for v in mesh.vertices))
        evaluated.to_mesh_clear()
    # Rest mesh soles sit about 0.6 mm below zero. Keep added penetration
    # below 2 mm, including intermediate frames between the baked keys.
    assert minimum_ground_z > -0.002, 'Foot roll penetrates the reference ground'
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
              'virtual_foot_clearance_m': 0.070, 'forward_axis': '-Y in Blender armature space',
              'nodes': nodes, 'endpoint_matrix_max_error': endpoint_error,
              'baked_action_matrix_max_error': replay_error,
              'minimum_deformed_mesh_ground_z_m': minimum_ground_z,
              'ground_check_samples': 2*CYCLE+1,
              'max_stance_drift_per_frame_with_nominal_travel_m': drift,
              'hand_fore_aft_travel_m': {side: max(s[side]['hand'][1] for s in samples) - min(s[side]['hand'][1] for s in samples) for side in ('Left', 'Right')},
              'foot_pitch_range_degrees': [-14, 30],
              'pelvis_vertical_travel_m': pelvis_dip,
              'flat_stance_knee_bend_range_degrees': {side: [min(values), max(values)] for side, values in flat_stance_knees.items()},
              'ankle_support_center_y_m': {side: rig.data.bones[side+'Foot'].head_local.y for side in ('Left', 'Right')},
              'arm_phase': 'opposite arm forward at leg heel strike; slight arm lag',
              'root_motion': 'in-place; EntityPosition stationary',
              'workbench_compilation': 'pending Windows test', 'in_game_test': 'not performed',
              'limitations': 'Visual revision, not final production motion; no native pace, footstep events, transitions, or blend compatibility validated.'}
    (args.output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    scene.frame_set(0)
    scene['MovementLab_notes'] = 'Walk v03: reduced body dip and straighter supporting knee; arm swing and foot roll retained. Loop 0–35; frame 36 duplicates frame 0. Nominal 0.90 m/s only; native speed not yet matched.'
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output/(NAME+'.blend')))
    print('WALK_CLIP_RESULT', json.dumps(report))


if __name__ == '__main__':
    main()
