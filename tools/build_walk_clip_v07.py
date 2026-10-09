"""Author a walk interpretation from the user's front and rear video references.

Key-pose curves are manually authored interpretations, not recovered 3D motion.
No native Rockstar assets or motion data are extracted. Native DayZ speed and
slots must be checked separately before using this as a gameplay replacement.
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

NAME = 'MovementLab_Unarmed_Walk_v07'
FPS = 30
CYCLE = 34  # Approximate repeat in the supplied front-view clip; camera affects the estimate.
DURATION = CYCLE / FPS
SPEED = 0.90  # Authoring reference only; not a change to DayZ movement speed.
STANCE = 0.61

# Authored normalized key poses guided by the visible hip/shoulder/wrist
# relationship in the reference. Rear-view projection does not determine
# exact 3D joint angles; these values remain artistic interpretations.
BODY_PHASES = (0, .07, .18, .30, .42, .50, .57, .68, .80, .92)
BODY_POSES = {
    'shift': (0, .010, .027, .020, .005, 0, -.010, -.027, -.020, -.005),
    'height': (-.020, -.016, -.005, -.005, -.017, -.020, -.016, -.005, -.005, -.017),
    'hip_yaw': (-3.8, -4.3, -1.8, 1.5, 3.6, 3.8, 4.3, 1.8, -1.5, -3.6),
    'hip_roll': (-.1, -.6, -1.4, -1.0, -.3, .1, .6, 1.4, 1.0, .3),
    'chest_yaw': (1.4, 2.0, 2.3, .6, -1.1, -1.4, -2.0, -2.3, -.6, 1.1),
    'lean': (2.1, 2.4, 2.2, 1.7, 1.9, 2.1, 2.4, 2.2, 1.7, 1.9),
}
ARM_PHASES = (0, .10, .22, .36, .50, .60, .72, .86)
ARM_POSES = {
    'swing': (16, 19, 9, -6, -15, -18, -8, 7),
    'elbow': (12, 16, 22, 20, 15, 21, 19, 14),
    'drop': (29, 30, 29, 28, 27, 28, 29, 30),
    'wrist': (2, 4, 1, -1, 0, 3, 1, -1),
}


def periodic_curve(phase, phases, values):
    """Cyclic cubic Hermite curve with matching value and tangent at wrap."""
    phase %= 1
    count = len(phases)
    index = next((i for i in range(count-1) if phases[i] <= phase < phases[i+1]), count-1)

    def knot(i):
        cycle, k = divmod(i, count)
        return phases[k]+cycle, values[k]

    x0, y0 = knot(index)
    x1, y1 = knot(index+1)
    xp, yp = knot(index-1)
    xn, yn = knot(index+2)
    m0, m1 = (y1-yp)/(x1-xp), (yn-y0)/(xn-x0)
    t = (phase-x0)/(x1-x0)
    return ((2*t**3-3*t*t+1)*y0 + (t**3-2*t*t+t)*(x1-x0)*m0
            + (-2*t**3+3*t*t)*y1 + (t**3-t*t)*(x1-x0)*m1)


def body_value(name, phase):
    return periodic_curve(phase, BODY_PHASES, BODY_POSES[name])


def arm_value(name, phase):
    return periodic_curve(phase, ARM_PHASES, ARM_POSES[name])


def relaxed_fingers(rig):
    """A soft, cupped hand pose instead of straight, spread fingers."""
    names = []
    for side, sign in (('Left', 1), ('Right', -1)):
        for digit, angles in (('Index', (16, 24, 12)), ('Middle', (20, 28, 14)),
                              ('Ring', (24, 30, 14)), ('Pinky', (28, 32, 15)),
                              ('Thumb', (8, 8, 5))):
            for joint, angle in enumerate(angles, 1):
                name = side+'Hand'+digit+str(joint)
                bone = rig.pose.bones[name]
                bone.rotation_quaternion = rig_axis_quaternion(bone, (0, 1, 0), sign*math.radians(angle))
                names.append(name)
    return names


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
    return y, 0.065 * lift


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
            pitch = -math.radians(22)*(1-smoothstep(t/0.18))
            return pitch, heel, 0.0, 'heel'
        if t < 0.58:
            return 0.0, heel, 0.0, 'flat'
        pitch = math.radians(30)*smoothstep((t-0.58)/0.42)
        return pitch, ball, -pitch, 'ball'
    t = (phase-STANCE)/(1-STANCE)
    pitch = math.radians(30) - math.radians(52)*smoothstep(t)
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
    assert abs(a - b) < distance < a + b - 0.00001, f'Unreachable {side} ankle at frame {bpy.context.scene.frame_current}: {distance} vs {a+b}; hip {tuple(hip)}, target {tuple(target)}'
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
    animated = ['Pelvis', 'Spine', 'Spine1', 'Spine2', 'Spine3', 'Neck', 'Neck1', 'Head', 'LeftArm', 'RightArm',
                'LeftForeArm', 'RightForeArm', 'LeftShoulder', 'RightShoulder',
                'LeftHand', 'RightHand']
    animated += [side + suffix for side in ('Left', 'Right') for suffix in ('UpLeg', 'Leg', 'Foot', 'ToeBase')]
    animated += relaxed_fingers(rig)
    for frame in range(CYCLE + 1):
        scene.frame_set(frame)
        for bone in rig.pose.bones:
            bone.matrix_basis = Matrix.Identity(4)
        phase = frame / CYCLE
        angle = 2 * math.pi * phase
        relaxed_fingers(rig)
        hip_yaw, hip_roll = body_value('hip_yaw', phase), body_value('hip_roll', phase)
        chest_yaw = body_value('chest_yaw', phase)
        pelvis = rig.pose.bones['Pelvis']
        pelvis.location = pelvis.bone.matrix_local.to_3x3().inverted() @ Vector((
            body_value('shift', phase), 0.002*math.sin(2*angle), body_value('height', phase)))
        pelvis.rotation_quaternion = rig_axis_quaternion(pelvis, (0, 0, 1), math.radians(hip_yaw)) @ rig_axis_quaternion(pelvis, (0, 1, 0), math.radians(hip_roll))
        bpy.context.view_layer.update()
        support_side, support_phase, support_sign = ('Left', phase%1, 1) if phase%1 < .5 else ('Right', (phase+.5)%1, -1)
        def support_height(p, side, sign, bend):
            y, lift = foot_path(p)
            pitch, pivot, _, _ = foot_roll(p)
            rot = Quaternion(Vector((1,0,0)), pitch)
            ankle = rig.data.bones[side+'Foot'].head_local
            target = Vector((sign*.100, ankle.y+y, ankle.z+lift)) + pivot-rot@pivot
            hip = rig.pose.bones[side+'UpLeg'].head.copy()
            upper = (rig.data.bones[side+'Leg'].head_local-rig.data.bones[side+'UpLeg'].head_local).length
            lower = (ankle-rig.data.bones[side+'Leg'].head_local).length
            length2 = upper*upper+lower*lower+2*upper*lower*math.cos(math.radians(bend))
            vertical = math.sqrt(length2-(target.x-hip.x)**2-(target.y-hip.y)**2)
            return target.z+vertical-hip.z
        # Stay nearly straight through heel placement/double support. Begin
        # yielding when the opposite foot leaves the ground (phase .11).
        knee = 3 if support_phase <= STANCE-.5 else 3+13*smoothstep((support_phase-(STANCE-.5))/.19)
        z = support_height(support_phase, support_side, support_sign, knee)
        # Blend into the next landing height before support swaps, with no pop.
        if support_phase > .40:
            landing = support_height(0, support_side, support_sign, 3)
            z = z*(1-smoothstep((support_phase-.40)/.10))+landing*smoothstep((support_phase-.40)/.10)
        # Respect both legs' anatomical reach, including the incoming heel.
        z = min(z, support_height(phase%1, 'Left', 1, 3),
                support_height((phase+.5)%1, 'Right', -1, 3))
        # Set world vertical motion through the pelvis rest-space axes.
        pelvis.location += pelvis.bone.matrix_local.to_3x3().inverted() @ Vector((0,0,z))
        bpy.context.view_layer.update()
        # Articulate the waist, ribs and upper chest separately. Delayed
        # bend/twist avoids treating the torso as a single rigid segment.
        for name, weight, lag in (('Spine', .18, 0), ('Spine1', .27, .025),
                                  ('Spine2', .32, .045), ('Spine3', .23, .065)):
            p = phase - lag
            twist = 1.0 * (body_value('chest_yaw', p) - body_value('hip_yaw', p))
            side_bend = 2.5 * math.sin(2*math.pi*(p-.045)) - body_value('hip_roll', p)
            flex = body_value('lean', p) + .65*math.sin(4*math.pi*(p-.035))
            bone = rig.pose.bones[name]
            bone.rotation_quaternion = (
                rig_axis_quaternion(bone, (0, 0, 1), math.radians(weight*twist)) @
                rig_axis_quaternion(bone, (0, 1, 0), math.radians(weight*side_bend)) @
                rig_axis_quaternion(bone, (1, 0, 0), math.radians(weight*flex)))
        # The neck absorbs only part of the chest turn: the head now follows
        # the torso gently instead of being held in an absolute world pose.
        for name, weight in (('Neck', .35), ('Neck1', .40), ('Head', .25)):
            bone = rig.pose.bones[name]
            p = phase-.09
            twist = 1.0*(body_value('chest_yaw', p)-body_value('hip_yaw', p))
            bone.rotation_quaternion = (
                rig_axis_quaternion(bone, (0, 0, 1), math.radians(-weight*.45*twist)) @
                rig_axis_quaternion(bone, (0, 1, 0), math.radians(-weight*1.2*math.sin(2*math.pi*(p-.08)))) @
                rig_axis_quaternion(bone, (1, 0, 0), math.radians(weight*.7*math.sin(4*math.pi*p))))
        bpy.context.view_layer.update()
        for side, offset, sign in (('Left', 0, 1), ('Right', 0.5, -1)):
            p = (phase + offset) % 1
            shoulder = rig.pose.bones[side+'Shoulder']
            shoulder.rotation_quaternion = (
                rig_axis_quaternion(shoulder, (0, 0, 1), -sign*math.radians(1.2+1.3*math.sin(2*math.pi*(p-.10)))) @
                rig_axis_quaternion(shoulder, (0, 1, 0), sign*math.radians(.8*math.sin(2*math.pi*(p-.06)))))
            arm = rig.pose.bones[side+'Arm']
            # A forward leg pairs with the opposite forward arm. +X rotation
            # moves a hanging hand BACK in this rig; v01 had this sign reversed.
            arm.rotation_quaternion = rig_axis_quaternion(arm, (1, 0, 0), math.radians(arm_value('swing', p))) @ rig_axis_quaternion(arm, (0, 1, 0), sign*math.radians(arm_value('drop', p)))
            bpy.context.view_layer.update()
            forearm = rig.pose.bones[side+'ForeArm']
            # Use the posed axes so elbow flex stays in the walking plane
            # after lowering the arms from the reference rig's spread pose.
            elbow_axis = forearm.matrix.to_3x3().inverted() @ Vector((1, 0, 0))
            forearm.rotation_quaternion = Quaternion(elbow_axis.normalized(), -math.radians(arm_value('elbow', p)))
            bpy.context.view_layer.update()
            hand = rig.pose.bones[side+'Hand']
            hand.rotation_quaternion = rig_axis_quaternion(hand, (0, 1, 0), sign*math.radians(arm_value('wrist', p)))
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
            reference = Vector((sign*0.100, rest_ankle.y + y, rest_ankle.z + lift))
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
    torso_angles = []
    for pose in matrices[:-1]:
        waist = pose['Pelvis'].to_quaternion() @ rig.data.bones['Pelvis'].matrix_local.to_quaternion().inverted()
        chest = pose['Spine3'].to_quaternion() @ rig.data.bones['Spine3'].matrix_local.to_quaternion().inverted()
        torso_angles.append(tuple(math.degrees(x) for x in (waist.inverted() @ chest).to_euler('XYZ')))
    torso_ranges = {axis: [min(a[i] for a in torso_angles), max(a[i] for a in torso_angles)]
                    for i, axis in enumerate(('flex', 'side_bend', 'twist'))}
    assert torso_ranges['twist'][1]-torso_ranges['twist'][0] > 10
    assert torso_ranges['side_bend'][1]-torso_ranges['side_bend'][0] > 6
    assert all(len(action.fcurves.find('pose.bones["'+name+'"].rotation_quaternion', index=0).keyframe_points) == CYCLE+1
               for name in ('Spine', 'Spine1', 'Spine2', 'Spine3', 'Neck', 'Neck1', 'Head'))
    drift = 0
    for side in ('Left', 'Right'):
        for frame in range(1, CYCLE):
            prev, now = samples[frame-1][side], samples[frame][side]
            if prev['stance'] and now['stance'] and now['phase'] > prev['phase']:
                step = Vector(now['contact_reference']) - Vector(prev['contact_reference']) - Vector((0, SPEED/FPS, 0))
                drift = max(drift, step.length)
        assert max(s[side]['ankle'][2] for s in samples) - min(s[side]['ankle'][2] for s in samples) > 0.055
        hand_travel = max(s[side]['hand'][1] for s in samples) - min(s[side]['hand'][1] for s in samples)
        assert hand_travel > 0.28, f'{side} hand swing too small: {hand_travel}'
        assert samples[0][side]['hand'][1] * (-1 if side == 'Right' else 1) > 0
    assert drift < 0.0001
    pelvis_heights = [matrix['Pelvis'].translation.z for matrix in matrices]
    pelvis_dip = max(pelvis_heights) - min(pelvis_heights)
    assert all(samples[0 if side=='Left' else CYCLE//2][side]['knee_bend_degrees'] < 5 for side in ('Left','Right')), 'Landing knee did not straighten'
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
    early_knees = {side: [q[side]['knee_bend_degrees'] for q in samples if q[side]['phase'] <= STANCE-.5]
                   for side in ('Left','Right')}
    late_knees = {side: [q[side]['knee_bend_degrees'] for q in samples if q[side]['phase'] >= .97]
                  for side in ('Left','Right')}
    assert all(max(v)<5 for v in early_knees.values())
    assert all(max(v)<5 for v in late_knees.values())
    groups = {g.index:g.name for g in body.vertex_groups}
    hip_vertices = [v.index for v in body.data.vertices if .80<v.co.z<1.14 and
                    sum(g.weight for g in v.groups if groups[g.group] in
                        ('Pelvis','Spine','Spine1','LeftUpLeg','RightUpLeg','LeftUpLegRoll','RightUpLegRoll'))>.5]
    hand_vertices = {side:[v.index for v in body.data.vertices if
                          sum(g.weight for g in v.groups if groups[g.group].startswith(side+'Hand'))>.5]
                     for side in ('Left','Right')}
    assert hip_vertices and all(hand_vertices.values())
    hand_gaps = {side:[] for side in hand_vertices}
    minimum_ground_z = float('inf')
    for sample in range(2*CYCLE+1):
        scene.frame_set(sample//2, subframe=(sample % 2)/2)
        bpy.context.view_layer.update()
        evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        minimum_ground_z = min(minimum_ground_z, min(v.co.z for v in mesh.vertices))
        for side, sign in (('Left',1),('Right',-1)):
            gap = min(sign*mesh.vertices[i].co.x for i in hand_vertices[side])-max(sign*mesh.vertices[i].co.x for i in hip_vertices)
            hand_gaps[side].append(gap)
        evaluated.to_mesh_clear()
    # Rest mesh soles sit about 0.6 mm below zero. Keep added penetration
    # below 2 mm, including intermediate frames between the baked keys.
    assert minimum_ground_z > -0.002, 'Foot roll penetrates the reference ground'
    assert all(min(v)>=.10 and max(v)<=.16 for v in hand_gaps.values()), str(hand_gaps)
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
              'virtual_foot_clearance_m': 0.065, 'forward_axis': '-Y in Blender armature space',
              'torso_relative_to_pelvis_angle_ranges_degrees': torso_ranges,
              'torso_revision': 'Four articulated spine joints with delayed twist, side bend and flex; partially following neck and head',
              'nodes': nodes, 'endpoint_matrix_max_error': endpoint_error,
              'baked_action_matrix_max_error': replay_error,
              'minimum_deformed_mesh_ground_z_m': minimum_ground_z,
              'ground_check_samples': 2*CYCLE+1,
              'max_stance_drift_per_frame_with_nominal_travel_m': drift,
              'hand_fore_aft_travel_m': {side: max(s[side]['hand'][1] for s in samples) - min(s[side]['hand'][1] for s in samples) for side in ('Left', 'Right')},
              'foot_pitch_range_degrees': [-22, 30],
              'ankle_track_width_m': .200,
              'hand_to_hip_lateral_mesh_gap_m': {side:[min(v),max(v)] for side,v in hand_gaps.items()},
              'hand_gap_method': 'Innermost hand/finger vertices minus outermost hip-band vertices in armature X; evaluated at integer and half frames, unclothed reference mesh',
              'early_support_knee_max_degrees': {side:max(v) for side,v in early_knees.items()},
              'late_swing_knee_max_degrees': {side:max(v) for side,v in late_knees.items()},
              'landing_knee_bend_degrees': {side: samples[0 if side=='Left' else CYCLE//2][side]['knee_bend_degrees'] for side in ('Left','Right')},
              'user_revision': 'Higher toes, nearly straight landing knee, delayed support flex, narrower leg track and more arm clearance',
              'pelvis_vertical_travel_m': pelvis_dip,
              'flat_stance_knee_bend_range_degrees': {side: [min(values), max(values)] for side, values in flat_stance_knees.items()},
              'ankle_support_center_y_m': {side: rig.data.bones[side+'Foot'].head_local.y for side in ('Left', 'Right')},
              'arm_phase': 'opposed arms, restrained swing and elbow overlap guided by front/rear visual comparison',
              'reference': 'https://www.youtube.com/shorts/FJnBXvfNc_E (earlier rear-view reference; also supplied three-second John Marston front-view crop)',
              'reference_method': 'manual key-pose interpretation; manual front/rear visual comparison; temporal lower-body correlation estimates a 1.13-second repeat in the front-view crop; no recovered 3D joint data',
              'reference_limits': 'Front crop 240x512, clothing occlusion, rear cropped feet and tracking cameras; references are not synchronized views of the same walk. Depth and absolute speed are estimated.',
              'root_motion': 'in-place; EntityPosition stationary',
              'workbench_compilation': 'pending Windows test', 'in_game_test': 'not performed',
              'limitations': 'Visual revision, not final production motion; no native pace, footstep events, transitions, or blend compatibility validated.'}
    (args.output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    scene.frame_set(0)
    scene['MovementLab_notes'] = 'Walk v07: front/rear video interpretation; front-view weight transfer, restrained chest twist, wider arms with hip clearance, narrower leg track and straighter landing knees, gently following head. Loop frames 0–33; frame 34 duplicates frame 0. Nominal 0.90 m/s is an authoring choice, not measured video speed.'
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output/(NAME+'.blend')))
    print('WALK_CLIP_RESULT', json.dumps(report))


if __name__ == '__main__':
    main()
