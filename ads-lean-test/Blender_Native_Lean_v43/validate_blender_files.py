"""Reopen saved files and verify native joint origins and unchanged source rig."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath='/workspace/output/DayZ_ADS_Lean_v6/DayZ_ADS_Side_Lean_v6_Blender_4_3.blend')
def mesh_data():
 m=bpy.data.objects['Male_body'].data
 return ([tuple(v.co) for v in m.vertices],[[(g.group,g.weight) for g in v.groups] for v in m.vertices])
original=mesh_data();rest={b.name:b.matrix_local.copy() for b in bpy.data.objects['Armature'].data.bones}
caps=json.loads((R/'Native-Captures.json').read_text());report={}
S=Matrix(((-1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)));C=S.inverted()
def tm(rows):
 m=Matrix.Identity(4)
 for col in range(4):
  for row in range(3):m[row][col]=rows[str(col)][row]
 return m
for side,cid in [('Left','60375_true'),('Right','67091_true')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'DayZ_Native_Lean_{side}_Blender_4_3.blend'))
 r=bpy.data.objects['Armature'];scene=bpy.context.scene;capture=caps[cid]
 assert mesh_data()==original
 assert all(max(abs(b.matrix_local[i][j]-rest[b.name][i][j]) for i in range(4) for j in range(4))<1e-6 for b in r.data.bones)
 assert scene.frame_current==1 and scene.frame_start==scene.frame_end==1 and not r.animation_data
 assert r.mode=='POSE' and not bpy.data.libraries
 bpy.data.collections['CAPTURE DATA - native bone frames'].hide_viewport=False
 bpy.context.view_layer.update()
 errors=[];matrix_errors=[]
 for n,rows in capture['bones'].items():
  expected=(S@tm(rows)).translation
  errors.append((r.matrix_world@r.pose.bones[n].head-expected).length)
  native=bpy.data.objects['Native '+n].matrix_world;want=S@tm(rows)@C
  assert json.loads(bpy.data.objects['Native '+n]['native_rows_json'])==rows
  matrix_errors.append(max(abs(native[i][j]-want[i][j]) for i in range(4) for j in range(4)))
 assert len(errors)==114 and max(errors)<.00002
 assert max(matrix_errors)<.00005
 held=bpy.data.objects['AK74 guide - captured weapon transform'].matrix_world
 expected=S@tm(capture['actor']).inverted()@tm(capture['weapon'])@C
 assert max(abs(held[i][j]-expected[i][j]) for i in range(4) for j in range(4))<.00001
 assert all(math.isfinite(v) for b in r.pose.bones for row in b.matrix for v in row)
 report[side]={'reopened_in_blender':'4.3.2','capture':cid,'all_114_joint_positions_match':True,'max_joint_error_metres':max(errors),'native_axis_display_max_component_error':max(matrix_errors),'raw_native_matrices_json_exact':True,'weapon_transform_matches_capture':True,'original_mesh_weights_rest_skeleton_unchanged':True,'no_linked_libraries':True}
(R/'Reopen-Validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: both files reopened, 114 joint origins each, native matrices and weapon placement verified, rest/mesh/weights preserved')
