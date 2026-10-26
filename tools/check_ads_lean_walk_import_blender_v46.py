# TEST ONLY: repeated existing isolated left snapshots exercise the importer.
# This is NOT a real walking clip and must never be distributed as one.
import bpy,sys,json,importlib.util,copy
from pathlib import Path
repository=Path(__file__).resolve().parents[1]
root=repository/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v46/BlenderTools'
spec=importlib.util.spec_from_file_location('walk46',root/'import_left_walk.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
caps=json.loads((repository/'ads-lean-test/Blender_Native_Lean_v43/Native-Captures.json').read_text())
frames=[]
for i in range(36):
 s=copy.deepcopy(caps['60375_true' if i%2==0 else '74575_true']);s.update(index=i,time_ms=1000+42*i,session='TEST_FIXTURE_NOT_A_REAL_WALK');frames.append(s)
out=Path('/tmp/TEST_ONLY_left_walk_import46.blend')
if out.exists():out.unlink()
report=m.build({'session':'TEST_FIXTURE_NOT_A_REAL_WALK','fps':24,'frames':frames},out)
bpy.ops.wm.open_mainfile(filepath=str(out));r=bpy.data.objects['Armature'];assert bpy.context.scene.frame_end==36
assert all(len(r.animation_data.action.fcurves.find('pose.bones["'+n+'"].rotation_quaternion',index=0).keyframe_points)==36 for n in frames[0]['bones'])
assert all(k.interpolation=='CONSTANT' for fc in r.animation_data.action.fcurves for k in fc.keyframe_points)
print('TEST FIXTURE ONLY: 36-sample bake, playback validation, quaternion keys and reopen passed',report['max_joint_position_and_playback_error_m'])

from mathutils import Matrix
S=Matrix(((-1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
for index,sample in enumerate(frames,start=1):
 bpy.context.scene.frame_set(index);bpy.context.view_layer.update()
 for name,rows in sample['bones'].items():
  target=S.to_3x3()@__import__('mathutils').Vector(rows['3'])
  assert (r.matrix_world@r.pose.bones[name].head-target).length < .00002
print('INDEPENDENT REOPEN CHECK: every saved frame matches every recorded joint origin')
