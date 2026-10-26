import bpy,sys,json,re,math
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,'/workspace/Modding-/tools')
from dayz_graph_formats import newnodes
from captured_pose_bridge import reconstruct,ordered
KIT=Path('/workspace/Modding-/ads-lean-test/MovementLab_ADS_Lean_Mosin_v41')
OUT=Path('/workspace/Modding-/ads-lean-test/Blender_Lean_Edit_v41')
snap=json.loads((KIT/'Pose-Snapshot.json').read_text());parents=snap['parents'];nodes=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text())
C=Matrix(((-1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
def empty():return {n:{'rotation_xyz':[0,0,0],'translation_xyz':[0,0,0]} for n in parents}
def apply_group(pose,prefix):
 corrections=empty()
 for name,node in nodes.items():
  if not name.startswith(prefix):continue
  m=re.search(r'Bone "([^\"]+)"\s+Axis ([XYZ])\s+Space Model\s+Op (Rotate|Translate)\s+Amount ([-\d.eE]+)',node)
  if m and m[1] in corrections:corrections[m[1]]['rotation_xyz' if m[3]=='Rotate' else 'translation_xyz']['XYZ'.index(m[2])]+=float(m[4])*(-1 if m[3]=='Rotate' else 1)
 out=reconstruct(pose,parents,corrections)
 for n,a in out.items():
  m=Matrix(a);q=m.to_quaternion().normalized().to_matrix().to_4x4();q.translation=m.translation;out[n]=[list(row) for row in q]
 return out
def pose_for(side,mode):
 p=apply_group(snap['reference'],f'ML5_{mode}_{side}_')
 if mode=='StandWalk':p=apply_group(p,'ML32_ReferenceHold_' if side=='left' else 'ML39_RightMovingLower_')
 p=apply_group(p,'ML15_HeadForwardNod')
 if side=='right':
  p=apply_group(p,'ML20_RightLeanHeadExposure')
  if mode=='StandWalk':p=apply_group(p,'ML21_RightMovingHeadLift')
 return p
for side,oldframe in [('left',49),('right',1)]:
 bpy.ops.wm.open_mainfile(filepath='/workspace/output/DayZ_ADS_Lean_v6/DayZ_ADS_Side_Lean_v6_Blender_4_3.blend')
 s=bpy.context.scene;r=bpy.data.objects['Armature'];s.frame_set(oldframe);bpy.context.view_layer.update()
 guide=bpy.data.objects['Aiming guide - schematic only'];guide_rel=(r.matrix_world@r.pose.bones['RightHand'].matrix).inverted()@guide.matrix_world
 r.animation_data_clear();guide.animation_data_clear()
 for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
 for text in list(bpy.data.texts):bpy.data.texts.remove(text)
 notes='''Editable lean authoring reference — Blender 4.3.2\nDirections are the CHARACTER'S own left/right.\nFrame 1: neutral raised; 25: stationary lean; 49: walking-lean authoring pose.\nSelected frame 49 is the pose for editing. Select Armature, Pose Mode, choose a bone, press R to rotate.\nOriginal mesh, skin weights and rest skeleton retained. Both files use v41 graph correction values.\nThe schematic rifle is a guide, not the actual DayZ AK/Mosin model.\nThis reconstructs procedural authoring transforms, NOT a captured native in-game frame.\nNative walking clips, final weapon/hand IK, elbow target solver, foot IK and runtime height controller are not baked here. Grip and gait may differ from the game.\nThe 1–49 transition is an editing aid, not an exported DayZ animation or the game's snap fix.\nSend back the edited .blend and specify the frame to transfer its pose changes to the shared player/NPC graph.\n'''
 bpy.data.texts.new('READ ME - editing and limits').write(notes)
 for frame,label,p in [(1,'NEUTRAL RAISED',snap['reference']),(25,side.upper()+' STATIONARY',pose_for(side,'StandIdle')),(49,side.upper()+' WALKING AUTHORING',pose_for(side,'StandWalk'))]:
  s.frame_set(frame)
  for b in r.pose.bones:b.rotation_mode='QUATERNION'
  for n in ordered(parents):
   m=C.inverted()@Matrix(p[n])@C;m.translation*=100;r.pose.bones[n].matrix=m;bpy.context.view_layer.update()
  for b in r.pose.bones:
   b.rotation_mode='QUATERNION';b.keyframe_insert('location',frame=frame,group=b.name);b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name);b.keyframe_insert('scale',frame=frame,group=b.name)
  guide.matrix_world=r.matrix_world@r.pose.bones['RightHand'].matrix@guide_rel
  guide.keyframe_insert('location',frame=frame);guide.keyframe_insert('rotation_euler',frame=frame);guide.keyframe_insert('scale',frame=frame)
  s.timeline_markers.new(label,frame=frame)
 s.frame_start=1;s.frame_end=49;s.frame_set(49);bpy.context.view_layer.update()
 for o in bpy.context.selected_objects:o.select_set(False)
 r.select_set(True);bpy.context.view_layer.objects.active=r;r.show_in_front=False
 if r.mode!='POSE':bpy.ops.object.mode_set(mode='POSE')
 for a in bpy.data.screens:
  for area in a.areas:
   if area.type=='VIEW_3D':
    v=area.spaces.active;v.region_3d.view_perspective='PERSP';v.region_3d.view_location=Vector((0,0,1));v.region_3d.view_distance=2.8;v.region_3d.view_rotation=(Vector((0,-5,1.6))-Vector((0,0,1))).to_track_quat('Z','Y');v.overlay.show_extras=False
 s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=700;s.render.resolution_y=850;s.render.resolution_percentage=100
 cam=bpy.data.objects.new('Pose Camera',bpy.data.cameras.new('Pose Camera'));s.collection.objects.link(cam);s.camera=cam
 s.camera.location=(0,-5,1.5);s.camera.rotation_euler=(Vector((0,0,.95))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=2.1
 s.render.filepath=str(OUT/f'Lean_{side.title()}_Preview.png');bpy.ops.render.render(write_still=True)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'DayZ_Lean_{side.title()}_Blender_4_3.blend'),compress=True)
(OUT/'README.txt').write_text(notes)
