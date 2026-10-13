"""Run in Blender: --background reference.blend --python this.py -- OUTPUT TOOLBOX.

Creates a static diagnostic arms mesh; no animation/gameplay compatibility claim.
The reference file remains untouched. Export uses upstream ArmAToolbox.
"""
import bpy, bmesh, sys, json, math
from pathlib import Path
from mathutils import Vector, Matrix

out = Path(sys.argv[sys.argv.index('--') + 1]); out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, sys.argv[sys.argv.index('--') + 2])
import ArmaToolbox
from ArmaToolbox import MDLExporter
ArmaToolbox.register()
rig = bpy.data.objects['_DayZ_Character']
body = bpy.data.objects['zMale_body']
rig.animation_data_clear()
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
    for c in list(pb.constraints): pb.constraints.remove(c)
bpy.context.view_layer.update()

arm_groups = {g.index for g in body.vertex_groups if
    g.name.startswith(('LeftArm', 'LeftForeArm', 'LeftHand',
                       'RightArm', 'RightForeArm', 'RightHand'))}
keep = {v.index for v in body.data.vertices if
        sum(g.weight for g in v.groups if g.group in arm_groups) >= .5}
original_vertices = len(body.data.vertices)
bm = bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in keep], context='VERTS')
bm.to_mesh(body.data); bm.free(); body.data.update()

def pose_arm(side, target, pole):
    upper = rig.data.bones[side+'Arm']
    lower = rig.data.bones[side+'ForeArm']
    hand = rig.data.bones[side+'Hand']
    start = upper.head_local.copy()
    upper_vec = lower.head_local-start; lower_vec = hand.head_local-lower.head_local
    a, b = upper_vec.length, lower_vec.length
    direction = target-start; d = direction.length
    assert abs(a-b) < d < a+b, (side, a, b, d)
    axis = direction.normalized()
    along = (a*a-b*b+d*d)/(2*d)
    perpendicular = pole-start-axis*(pole-start).dot(axis)
    elbow = start+axis*along+perpendicular.normalized()*math.sqrt(a*a-along*along)
    def set_segment(name, origin, source_vec, destination_vec):
        bone = rig.data.bones[name]
        rotation = source_vec.rotation_difference(destination_vec).to_matrix().to_4x4()
        rig.pose.bones[name].matrix = Matrix.Translation(origin) @ rotation @ Matrix.Translation(-bone.head_local) @ bone.matrix_local
        bpy.context.view_layer.update()
    set_segment(side+'Arm', start, upper_vec, elbow-start)
    set_segment(side+'ForeArm', elbow, lower_vec, target-elbow)
    return {'shoulder':list(start), 'elbow':list(elbow), 'wrist':list(target)}

poses = {
    'right':pose_arm('Right', Vector((-.14,-.34,1.25)), Vector((-.5,-.05,.9))),
    'left':pose_arm('Left', Vector((.03,-.49,1.27)), Vector((.5,-.15,.95)))
}
# Keep an editable rigged source, independent of the diagnostic static P3D.
body.name = 'MovementLab_Arms_Rigged'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'MovementLab_Arms_Rigged.blend'))
depsgraph = bpy.context.evaluated_depsgraph_get()
mesh = bpy.data.meshes.new_from_object(body.evaluated_get(depsgraph), depsgraph=depsgraph)
static = bpy.data.objects.new('arms_only', mesh)
bpy.context.collection.objects.link(static)
static.matrix_world = body.matrix_world.copy()
# Center the asset around its own bounds for ItemPreview's bounding-box camera.
coords = [static.matrix_world @ v.co for v in mesh.vertices]
center = Vector(tuple((min(v[i] for v in coords)+max(v[i] for v in coords))/2 for i in range(3)))
for v in mesh.vertices: v.co = static.matrix_world @ v.co-center
static.matrix_world = Matrix.Identity(4)
mat = bpy.data.materials.new('DiagnosticArmsGrey')
mat.diffuse_color = (.22,.25,.28,1)
mat.armaMatProps.texType = 'Color'; mat.armaMatProps.colorValue = (.22,.25,.28)
mat.armaMatProps.colorType = 'CO'
mesh.materials.clear(); mesh.materials.append(mat)
for p in mesh.polygons: p.material_index=0; p.use_smooth=True
static.armaObjProps.isArmaObject=True; static.armaObjProps.lod='-1.0'; static.armaObjProps.lodDistance=1
bpy.ops.object.select_all(action='DESELECT'); static.select_set(True); bpy.context.view_layer.objects.active=static
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
with (out/'arms_only.p3d').open('wb') as f:
    assert MDLExporter.exportMDL(None, f, True, False, False, False, True)
body.hide_render=True; rig.hide_render=True
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=16
scene.render.resolution_x=960; scene.render.resolution_y=540; scene.render.resolution_percentage=100
scene.world.color=(.08,.08,.08)
camera_data=bpy.data.cameras.new('ArmsDiagnosticCamera'); camera=bpy.data.objects.new('ArmsDiagnosticCamera',camera_data)
scene.collection.objects.link(camera); scene.camera=camera
camera.location=(0,.8,.42); camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.lens=36
for location in [(2,1,3),(-2,0,2)]:
    lightdata=bpy.data.lights.new('DiagnosticLight','AREA'); lightdata.energy=400; lightdata.size=3
    light=bpy.data.objects.new('DiagnosticLight',lightdata); scene.collection.objects.link(light)
    light.location=location; light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(out/'arms_only_preview.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'MovementLab_Arms_Static.blend'))
report={'source_vertices':original_vertices,'arms_vertices':len(mesh.vertices),'faces':len(mesh.polygons),
        'selection_rule':'arm/forearm/hand bone weights >= 0.5; torso/head/legs removed',
        'pose':poses,'static':True,'native_render_test':'pending','gun_grip_test':'pending'}
assert 0 < report['arms_vertices'] < original_vertices
(out/'model-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('ARMS_MODEL_VALIDATED',report['arms_vertices'],report['faces'])
