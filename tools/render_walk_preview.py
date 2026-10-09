"""Render the walk study and save a useful Blender preview scene."""

import argparse
import sys
import bpy
from mathutils import Vector
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
p = args.output
bpy.ops.wm.open_mainfile(filepath=str(p/'MovementLab_Unarmed_Walk_v01.blend'), use_scripts=False)
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
 bpy.ops.object.mode_set(mode='OBJECT')
for obj in list(bpy.data.objects):
 if obj.name not in ('_DayZ_Character', 'zMale_body'):
  bpy.data.objects.remove(obj, do_unlink=True)
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.device='CPU'
s.cycles.samples=8
s.cycles.use_denoising=False
s.render.use_compositing=False
s.render.resolution_x=384
s.render.resolution_y=384
s.render.resolution_percentage=100
s.world.color=(.18,.18,.18)
body=bpy.data.objects['zMale_body']
m=bpy.data.materials.new('MovementLab preview clay'); m.diffuse_color=(.42,.49,.59,1)
body.data.materials.clear(); body.data.materials.append(m)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.002))
bpy.context.object.name='PreviewGround'
m=bpy.data.materials.new('Preview ground'); m.diffuse_color=(.23,.25,.27,1); bpy.context.object.data.materials.append(m)
bpy.ops.object.camera_add(location=(3,-4,2.1))
c=bpy.context.object
c.rotation_euler=(Vector((0,0,.85))-c.location).to_track_quat('-Z','Y').to_euler()
c.data.type='ORTHO'; c.data.ortho_scale=2.1; s.camera=c
for position,energy in (((-3,-4,5),600),((3,2,3),400)):
 bpy.ops.object.light_add(type='AREA',location=position)
 l=bpy.context.object;l.data.energy=energy;l.data.shape='DISK';l.data.size=4
 l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
# Give the editable file a useful initial viewport; only the armature is selected.
bpy.ops.object.select_all(action='DESELECT')
r=bpy.data.objects['_DayZ_Character']; r.select_set(True); bpy.context.view_layer.objects.active=r
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_location=Vector((0,0,.85))
   area.spaces.active.region_3d.view_distance=3
   area.spaces.active.region_3d.view_rotation=c.rotation_euler.to_quaternion()
   area.spaces.active.shading.type='SOLID'
s.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'MovementLab_Unarmed_Walk_v01.blend'))
(p/'frames').mkdir(exist_ok=True)
for frame in range(0,36,2):
 s.frame_set(frame);s.render.filepath=str(p/'frames'/f'walk_{frame:03d}.png');bpy.ops.render.render(write_still=True)
