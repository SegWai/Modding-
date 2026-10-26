"""Import native captured joint positions; retarget source rig's different bone axes.
Run with Blender 4.3.2 --background --python this_file.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
import numpy as np
OUT=Path(__file__).resolve().parent
SOURCE=Path('/workspace/output/DayZ_ADS_Lean_v6/DayZ_ADS_Side_Lean_v6_Blender_4_3.blend')
CAPS=json.loads((OUT/'Native-Captures.json').read_text())
C=Matrix(((-1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
S=C.inverted()
def tm(rows):
 m=Matrix.Identity(4)
 for col in range(4):
  for row in range(3):m[row][col]=rows[str(col)][row]
 return m
def rigidfit(a,b,fallback):
 if len(a)<2:return fallback
 A=np.array([list(v.normalized()) for v in a]);B=np.array([list(v.normalized()) for v in b]);u,s,vt=np.linalg.svd(B.T@A)
 if s[1]<.01:return fallback
 fix=np.eye(3);fix[2,2]=np.linalg.det(u@vt)
 return Matrix((u@fix@vt).tolist())
reports={}
for side,cid in [('Left','60375_true'),('Right','67091_true')]:
 capture=CAPS[cid];assert capture['complete'] and len(capture['bones'])==114
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;rig=bpy.data.objects['Armature'];mesh=bpy.data.objects['Male_body']
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 # Keep original mesh, bone rest matrices and skin weights; replace pose only.
 for obj in list(bpy.data.objects):
  if obj not in (rig,mesh):bpy.data.objects.remove(obj,do_unlink=True)
 for obj in (rig,mesh):obj.animation_data_clear()
 for b in rig.pose.bones:
  for constraint in list(b.constraints):b.constraints.remove(constraint)
  b.matrix_basis=Matrix.Identity(4);b.rotation_mode='QUATERNION'
 bpy.context.view_layer.update()
 rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
 targets={n:(S@tm(rows)).translation*100 for n,rows in capture['bones'].items()}
 # Use actual measured landmarks to fit each source bone's orientation. Native
 # transforms use different local axes from this rig; a direct matrix assignment
 # would point the elbows/gun upward. Single-child bones inherit parent twist.
 desired={}
 for bone in rig.data.bones:
  n=bone.name;parent=bone.parent
  inherited=Matrix.Identity(3) if not parent else desired[parent.name].to_3x3()@rest[parent.name].to_3x3().inverted()
  direct=[ch.name for ch in bone.children if ch.name in targets and (targets[ch.name]-targets[n]).length>.01]
  if n=='Head':direct=[k for k in ('EyeLeft','EyeRight','Face_Hub','Face_Jawbone','Face_Forehead') if k in targets]
  if direct:
   av=[rest[k].translation-rest[n].translation for k in direct];bv=[targets[k]-targets[n] for k in direct]
   idx=max(range(len(av)),key=lambda i:av[i].length)
   before=inherited@av[idx];swing=before.rotation_difference(bv[idx]).to_matrix()
   rot=rigidfit(av,bv,swing@inherited)
  else:
   rot=inherited
   if 'Hand' in n and n.endswith('3'):
    native_axis=tm(capture['bones'][n]).to_3x3().col[0]
    aim=S.to_3x3()@native_axis
    if n.startswith('Right'):aim=-aim
    leaf=bone.tail_local-bone.head_local
    rot=(inherited@leaf).rotation_difference(aim).to_matrix()@inherited
  m=(rot@rest[n].to_3x3()).to_4x4();m.translation=targets[n];desired[n]=m
 for n,m in desired.items():rig.pose.bones[n].matrix=m;bpy.context.view_layer.update()
 scene.frame_start=scene.frame_end=scene.frame_current=1
 for mark in list(scene.timeline_markers):scene.timeline_markers.remove(mark)
 scene.timeline_markers.new(f'{side.upper()} - ACTUAL CAPTURE {cid}',frame=1)
 # Show native axes as an optional separate collection. The raw transforms are
 # preserved exactly, independent of mesh retarget orientation.
 raw=bpy.data.collections.new('CAPTURE DATA - native bone frames');scene.collection.children.link(raw)
 for n,rows in capture['bones'].items():
  obj=bpy.data.objects.new('Native '+n,None);raw.objects.link(obj);m=S@tm(rows)@C;obj.matrix_world=m;obj.empty_display_type='ARROWS';obj.empty_display_size=.035;obj['native_rows_json']=json.dumps(rows)
 raw.hide_viewport=True;raw.hide_render=True
 # Schematic AK, placed using the captured weapon WORLD transform relative to
 # the captured actor. No hand-relative guess or original guide animation.
 weapon_ms=tm(capture['actor']).inverted()@tm(capture['weapon'])
 weapon_bl=S@weapon_ms@C
 guncol=bpy.data.collections.new('RIFLE GUIDE - captured transform');scene.collection.children.link(guncol)
 gun=bpy.data.objects.new('AK74 guide - captured weapon transform',None);guncol.objects.link(gun);gun.matrix_world=weapon_bl
 mat=bpy.data.materials.new('Rifle charcoal');mat.diffuse_color=(.075,.09,.105,1)
 def box(name,center,size):
  # Vertices built in Blender-local coordinates from DayZ gun-local coordinates.
  bpy.ops.mesh.primitive_cube_add(size=1)
  o=bpy.context.object;o.name=name;o.location=(S@Vector((*center,1)))[:3]
  dims=S.to_3x3()@Vector(size);o.dimensions=tuple(abs(v) for v in dims)
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for col in list(o.users_collection):col.objects.unlink(o)
  guncol.objects.link(o);o.parent=gun;o.data.materials.append(mat)
  return o
 # Native AK model has barrel along -X, up +Y, lateral +Z. Placing a
 # Z-forward proxy would turn the rifle sideways despite the correct transform.
 for args in [('AK receiver',(.065,.085,0),(.25,.075,.045)),('AK stock',(.30,.075,0),(.23,.095,.045)),('AK fore-end',(-.16,.08,0),(.20,.055,.05)),('AK barrel',(-.38,.10,0),(.27,.018,.018)),('AK suppressor',(-.58,.10,0),(.17,.04,.04)),('AK grip',(.12,.005,0),(.045,.11,.035)),('AK magazine',(-.005,-.05,0),(.065,.18,.033)),('AK optic',(.06,.145,0),(.07,.05,.043))]:box(*args)
 scene['native_capture_id']=cid;scene['native_lean']=float(-1 if side=='Left' else 1);scene['native_capture_source']='Mosin-Lean-v43-Logs-20261026-052008.zip'
 notes=f'''NATIVE IN-GAME {side.upper()} LEAN — Blender 4.3.2\n\nFrozen walking/aiming pose captured from the NPC, ID {cid}.\nAll 114 joint origins are imported from DayZ. This is one instant in the\nwalking cycle, not a looping walking animation or a stationary pose.\n\nThe supplied weighted body is retargeted to those joint positions. Its\nlocal bone axes differ from DayZ, so mesh bone rotations are fitted to the\ncaptured landmarks, with inherited twist for single-child chains. Native\nraw orientation matrices are preserved separately in the hidden CAPTURE\nDATA collection and Native-Captures.json. Skin twist may differ from DayZ.\n\nThe schematic AK is positioned using the captured weapon transform. It\nis a guide, not the original weapon mesh, so stock/grip dimensions may differ.\n\nSelect Armature, Pose Mode, select a bone and R to rotate. Frame 1 is the\ncapture. Send back the edited .blend to transfer the pose change to the mod.\nOriginal rest skeleton and skin weights preserved; no gameplay files changed.\n'''
 for text in list(bpy.data.texts):bpy.data.texts.remove(text)
 bpy.data.texts.new('READ ME - captured pose').write(notes)
 (OUT/f'README-{side}.txt').write_text(notes)
 bpy.context.view_layer.update()
 errors={n:(rig.pose.bones[n].head-targets[n]).length*.01 for n in targets}
 assert max(errors.values())<.00002,(side,max(errors.values()))
 reports[side]={'capture_id':cid,'captured_bones':len(targets),'max_joint_origin_error_metres':max(errors.values()),'joint_errors_metres':errors,'weapon_modelspace_rows':[list(row) for row in weapon_ms],'mesh_orientation':'landmark fit; native axes preserved separately','original_rest_and_weights_preserved':True}
 scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
 scene.world.color=(.1,.1,.1);scene.render.resolution_x=850;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
 cam=bpy.data.objects.new('Preview Camera',bpy.data.cameras.new('Preview Camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=2.08
 for name,loc in [('Front',(0,-5,1.3)),('Angle',(3,-5,1.7))]:
  cam.location=loc;cam.rotation_euler=(Vector((0,-.08,.95))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'{side}-{name}.png');bpy.ops.render.render(write_still=True)
 for obj in bpy.context.selected_objects:obj.select_set(False)
 rig.select_set(True);bpy.context.view_layer.objects.active=rig;rig.show_in_front=False;bpy.ops.object.mode_set(mode='POSE')
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    space=area.spaces.active;space.overlay.show_extras=False;space.region_3d.view_perspective='PERSP';space.region_3d.view_distance=2.8;space.region_3d.view_location=Vector((0,0,.95));space.region_3d.view_rotation=(Vector((1.7,-5,1.5))-Vector((0,0,.95))).to_track_quat('Z','Y')
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'DayZ_Native_Lean_{side}_Blender_4_3.blend'),compress=True)
(OUT/'Import-Validation.json').write_text(json.dumps(reports,indent=2)+'\n')
