"""Blender-rendered controller illustration. Not native DayZ animation/physics."""
import bpy,math,argparse,sys,json
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);out=a.output;out.mkdir(parents=True,exist_ok=True);(out/'frames').mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False
s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.fps=30
s.world=bpy.data.worlds.new('Backdrop');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.015,.022,.04,1)
s.view_settings.view_transform='Standard'
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
white=mat('White',(.9,.94,1));grey=mat('Muted',(.35,.46,.6));grid=mat('Grid',(.08,.13,.21));orange=mat('Before',(.98,.42,.18));green=mat('After',(.18,.87,.64));yellow=mat('Timeline',(.95,.78,.23))
def text(body,x,y,size=.28,material=white):
 c=bpy.data.curves.new(body,'FONT');c.body=body;c.size=size;c.align_y='CENTER';o=bpy.data.objects.new(body,c);s.collection.objects.link(o);o.location=(x,y,.1);o.data.materials.append(material);return o
def line(name,points,material,r=.018):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=1;sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);s.collection.objects.link(o);o.data.materials.append(material);return o
text('JOG -> WALK: BEFORE / AFTER',-7.4,3.85,.48)
text('Controller illustration, not DayZ character animation footage',-7.4,3.28,.26,grey)
text('Playback 4x slower  |  Same actual transition: 0.42 seconds',-7.4,2.85,.29,yellow)
markers=[];cursors=[]
for idx,(x,title,color) in enumerate([(-6.9,'BEFORE - v8',orange),(1.0,'AFTER - v9',green)]):
 text(title,x,2.1,.36,color)
 for v in [0,.25,.5,.75,1]:
  y=-1.35+v*2.8;line('Grid',[(x,y,0),(x+5.6,y,0)],grid,.009)
 for v,label in [(1,'JOG 2'),(0,'WALK 1')]:text(label,x-.55,-1.35+v*2.8,.19,grey)
 points=[]
 for i in range(121):
  t=i/120;blend=2*t-t*t if idx==0 else t*t*(3-2*t);points.append((x+5.6*t,-1.35+2.8*(1-blend),.03))
 line('Gait curve',points,color,.035)
 text('0s',x,-1.72,.23,grey);text('0.21s',x+2.35,-1.72,.23,grey);text('0.42s',x+4.7,-1.72,.23,grey)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.11,location=points[0]);dot=bpy.context.object;dot.name=title+' current request';dot.data.materials.append(white);markers.append((dot,x,idx))
 cursor=line('Time cursor',[(0,-1.35,.01),(0,1.45,.01)],yellow,.011);cursor.location.x=x;cursors.append((cursor,x))
text('Requested gait (not measured metres/second)',-7.4,-2.35,.28,grey)
text('Halfway (0.21s): 1.25 before  |  1.50 after',-7.4,-2.85,.33)
text('After retains more early momentum; both finish at walking on time.',-7.4,-3.4,.3)
text('No changed animation clip, added pause, or longer transition.',-7.4,-3.9,.25,grey)
bpy.ops.object.camera_add(location=(0,0,20));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=16;s.camera=cam
s.frame_start=1;s.frame_end=90
for frame in range(1,91):
 t=max(0,min((frame-16)/(0.42*4*30),1))
 for dot,x,idx in markers:
  blend=2*t-t*t if idx==0 else t*t*(3-2*t);dot.location=(x+5.6*t,-1.35+2.8*(1-blend),.1);dot.keyframe_insert('location',frame=frame)
 for cursor,x in cursors:cursor.location.x=x+5.6*t;cursor.keyframe_insert('location',frame=frame)
for o in list(bpy.data.objects):
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(41) # Halfway for an explanatory still.
s.render.filepath=str(out/'comparison.png');bpy.ops.render.render(write_still=True)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'Jog_Walk_Controller_Comparison.blend'))
for frame in range(1,91):
 s.frame_set(frame);s.render.filepath=str(out/'frames'/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
(out/'notes.json').write_text(json.dumps({'kind':'controller curve illustration, not native DayZ animation footage','source':'v8 Ctrl jog-to-walk ease-out vs v9 smoothstep','actual_duration_seconds':.42,'playback_slowdown':4,'before':'2-(2*t-t*t)','after':'2-t*t*(3-2*t)','unchanged':'endpoints/deadline, clips, crouch rules, fixed turning','limits':'Requested gait units, no native clip blend or physical velocity reconstruction'},indent=2)+'\n')
