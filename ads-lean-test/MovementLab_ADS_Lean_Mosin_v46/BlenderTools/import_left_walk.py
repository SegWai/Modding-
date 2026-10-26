"""Parse a continuous MLWALK46 capture and bake editable Blender sample frames.
Blender --background --python import_left_walk.py -- --log PATH --output FILE.blend
PATH can be a script log, collected ZIP, or the test's profile directory.
No frames are fabricated when a complete continuous capture is unavailable.
"""
from pathlib import Path
import json,re,sys,argparse,zipfile,math

def parse_log(text,expected_frames=36):
    sessions={};pending=None;active=None
    for line in text.splitlines():
        mark=re.search(r'\[MLWALK46\] FRAME session=(\S+) frame=(\d+) time_ms=(\d+)',line)
        if mark:
            session,index,t=mark.groups();pending={'session':session,'index':int(index),'time_ms':int(t)};active=None;continue
        complete=re.search(r'\[MLWALK46\] COMPLETE session=(\S+) frames=(\d+) nominal_fps=(\d+)',line)
        if complete:
            session,count,fps=complete.groups();s=sessions.setdefault(session,{'frames':[]});s['complete_count']=int(count);s['fps']=int(fps);continue
        m=re.search(r'\[MLPOSE46\] (BEGIN|BONE|ACTOR|WEAPON|WEAPON_TYPE|END) id=(\S+)(.*)',line)
        if not m or pending is None:continue
        kind,cid,tail=m.groups()
        if kind=='BEGIN':
            active=dict(pending,id=cid,meta=tail.rstrip("'"),bones={},actor={},weapon={});continue
        if active is None or active['id']!=cid:continue
        if kind in ('BONE','ACTOR','WEAPON'):
            rm=re.search(r'row=(\d+) value=<([^>]+)>',tail)
            if not rm:raise ValueError('Malformed matrix row in capture')
            row,values=rm.groups();v=list(map(float,values.split(',')))
            if len(v)!=3 or not all(math.isfinite(x) for x in v):raise ValueError('Invalid transform values')
            target=active['bones'].setdefault(re.search(r'name=(\S+)',tail)[1],{}) if kind=='BONE' else active[kind.lower()]
            if row in target:raise ValueError('Duplicate matrix row')
            target[row]=v
        elif kind=='WEAPON_TYPE':active['weapon_type']=tail.rstrip("'")
        elif kind=='END':
            sessions.setdefault(active['session'],{'frames':[]})['frames'].append(active);pending=None;active=None
    usable=[]
    for session,s in sessions.items():
        frames=s['frames']
        if s.get('complete_count')!=expected_frames or len(frames)!=expected_frames or s.get('fps')!=24:continue
        if [f['index'] for f in frames]!=list(range(expected_frames)):continue
        valid=True
        for i,f in enumerate(frames):
            meta=f['meta'];lean=re.search(r'\blean=([-\d.eE]+)',meta);move=re.search(r'\bmove_blend=([-\d.eE]+)',meta)
            if 'demo=true' not in meta or not lean or float(lean[1])>-.98 or not move or float(move[1])<.98:valid=False;break
            if len(f['bones'])!=114:valid=False;break
            if any(set(rows)!=set('0123') for rows in [f['actor'],f['weapon'],*f['bones'].values()]):valid=False;break
            if i and not 0<f['time_ms']-frames[i-1]['time_ms']<=250:valid=False;break
            if i and set(f['bones'])!=set(frames[0]['bones']):valid=False;break
        if valid:usable.append(dict(session=session,fps=s['fps'],frames=frames))
    if not usable:raise ValueError('No complete continuous 36-frame character-left walk capture found. Press F9 in v46 and wait for Left walk clip captured, then collect logs.')
    return usable[-1]

def load_capture(path):
    path=Path(path)
    if path.is_dir():
        logs=sorted(path.glob('script_*.log'),key=lambda p:p.stat().st_mtime,reverse=True)
        for log in logs:
            try:return parse_log(log.read_text(encoding='utf8',errors='replace'))
            except ValueError:continue
        raise ValueError('No complete left-walk capture in profile logs')
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for name in reversed(sorted(n for n in z.namelist() if Path(n).name.startswith('script_') and n.endswith('.log'))):
                try:return parse_log(z.read(name).decode('utf8',errors='replace'))
                except ValueError:continue
        raise ValueError('No complete left-walk capture in ZIP')
    return parse_log(path.read_text(encoding='utf8',errors='replace'))

def build(capture,output,template=None):
    import bpy
    from mathutils import Matrix,Vector
    import numpy as np
    output=Path(output)
    if output.exists():raise ValueError('Output exists; choose a new filename to preserve edits: '+str(output))
    template=Path(template) if template else Path(__file__).with_name('Lean_Template.blend')
    bpy.ops.wm.open_mainfile(filepath=str(template));scene=bpy.context.scene;rig=bpy.data.objects['Armature'];mesh=bpy.data.objects['Male_body']
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    raw=bpy.data.collections.get('CAPTURE DATA - native bone frames')
    if raw:
        for obj in list(raw.objects):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.collections.remove(raw)
    for obj in scene.objects:obj.animation_data_clear()
    for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
    for b in rig.pose.bones:
        for constraint in list(b.constraints):b.constraints.remove(constraint)
        b.matrix_basis=Matrix.Identity(4);b.rotation_mode='QUATERNION'
    rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
    S=Matrix(((-1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)));C=S.inverted()
    def tm(rows):
        m=Matrix.Identity(4)
        for col in range(4):
            for row in range(3):m[row][col]=rows[str(col)][row]
        return m
    def fit(av,bv,fallback):
        if len(av)<2:return fallback
        a=np.array([list(v.normalized()) for v in av]);b=np.array([list(v.normalized()) for v in bv]);u,sv,vt=np.linalg.svd(b.T@a)
        if sv[1]<.01:return fallback
        fix=np.eye(3);fix[2,2]=np.linalg.det(u@vt)
        return Matrix((u@fix@vt).tolist())
    gun=bpy.data.objects['AK74 guide - captured weapon transform'];gun.rotation_mode='QUATERNION'
    previous={};max_error=0;sample_errors=[]
    for index,sample in enumerate(capture['frames'],start=1):
        if set(sample['bones'])!=set(rest):raise ValueError('Capture bones differ from supplied template')
        scene.frame_set(index)
        targets={n:(S@tm(rows)).translation*100 for n,rows in sample['bones'].items()};desired={}
        for bone in rig.data.bones:
            n=bone.name;parent=bone.parent
            inherited=Matrix.Identity(3) if not parent else desired[parent.name].to_3x3()@rest[parent.name].to_3x3().inverted()
            direct=[ch.name for ch in bone.children if (targets[ch.name]-targets[n]).length>.01]
            if n=='Head':direct=[k for k in ('EyeLeft','EyeRight','Face_Hub','Face_Jawbone','Face_Forehead') if k in targets]
            if direct:
                av=[rest[k].translation-rest[n].translation for k in direct];bv=[targets[k]-targets[n] for k in direct];i=max(range(len(av)),key=lambda j:av[j].length)
                rot=fit(av,bv,(inherited@av[i]).rotation_difference(bv[i]).to_matrix()@inherited)
            else:
                rot=inherited
                if 'Hand' in n and n.endswith('3'):
                    aim=S.to_3x3()@tm(sample['bones'][n]).to_3x3().col[0]
                    if n.startswith('Right'):aim=-aim
                    rot=(inherited@(bone.tail_local-bone.head_local)).rotation_difference(aim).to_matrix()@inherited
            m=(rot@rest[n].to_3x3()).to_4x4();m.translation=targets[n];desired[n]=m
        for n,m in desired.items():rig.pose.bones[n].matrix=m;bpy.context.view_layer.update()
        errors=[(rig.matrix_world@rig.pose.bones[n].head-(S@tm(sample['bones'][n])).translation).length for n in targets]
        err=max(errors);max_error=max(max_error,err);sample_errors.append(err)
        if err>.00002:raise ValueError('Joint import error exceeds tolerance')
        for b in rig.pose.bones:
            q=b.rotation_quaternion
            if b.name in previous and q.dot(previous[b.name])<0:q.negate()
            previous[b.name]=q.copy()
            for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(prop,frame=index,group=b.name)
        gun.matrix_world=S@tm(sample['actor']).inverted()@tm(sample['weapon'])@C
        for prop in ('location','rotation_quaternion','scale'):gun.keyframe_insert(prop,frame=index)
        scene.timeline_markers.new(f'Sample {index:02d} | game {sample["time_ms"]} ms',frame=index)
    for obj in (rig,gun):
        for fc in obj.animation_data.action.fcurves:
            for key in fc.keyframe_points:key.interpolation='CONSTANT'
    scene.frame_start=1;scene.frame_end=len(capture['frames']);scene.render.fps=capture['fps'];scene.frame_set(1);bpy.context.view_layer.update()
    # Verify playback evaluation at EVERY saved integer sample frame.
    for index,sample in enumerate(capture['frames'],start=1):
        scene.frame_set(index);bpy.context.view_layer.update()
        for n,rows in sample['bones'].items():
            err=(rig.matrix_world@rig.pose.bones[n].head-(S@tm(rows)).translation).length
            max_error=max(max_error,err)
            if err>.00002:raise ValueError('Playback joint error exceeds tolerance')
    scene.frame_set(1);scene['native_capture_session']=capture['session'];scene['capture_samples']=len(capture['frames']);scene['native_direction']='character left';scene['nominal_capture_fps']=capture['fps'];scene['capture_time_span_ms']=capture['frames'][-1]['time_ms']-capture['frames'][0]['time_ms']
    for txt in list(bpy.data.texts):bpy.data.texts.remove(txt)
    bpy.data.texts.new('RAW NATIVE WALK CAPTURE.json').write(json.dumps(capture,indent=2))
    bpy.data.texts.new('READ ME - captured walking clip').write('''Frame 1–36: 36 captured samples of one continuous CHARACTER-LEFT walking/aiming lean pass.\nOne captured pose per frame, nominal 24 fps; actual game times are in timeline markers and raw JSON.\nNo reverse-direction or separate patrol passes joined. No invented intermediate sample frames.\nConstant interpolation preserves each recorded sample; this is not a seamless loop.\nAll 114 joint origins and held-weapon transforms imported; source mesh, weights and rest skeleton retained.\nThe body uses landmark-fit source bone rotations; native local axes differ, so skin twist may differ.\nRifle is a schematic guide at the measured transform, not the original weapon mesh.\nUse Left/Right Arrow to step frames; select Armature in Pose Mode to edit a sample.\nEnable Auto Keying or insert a keyframe after editing. Send back the saved .blend and frame numbers.\n''')
    for obj in bpy.context.selected_objects:obj.select_set(False)
    rig.select_set(True);bpy.context.view_layer.objects.active=rig
    if rig.mode!='POSE':bpy.ops.object.mode_set(mode='POSE')
    bpy.context.preferences.filepaths.save_version=0
    output.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
    output.with_suffix('.capture.json').write_text(json.dumps(capture,indent=2)+'\n')
    report={'samples':len(capture['frames']),'native_direction':'character-left','nominal_fps':capture['fps'],'actual_time_span_ms':scene['capture_time_span_ms'],'max_joint_position_and_playback_error_m':max_error,'all_sample_joint_positions_verified':True,'source_frames':sample_errors,'skin_rotations':'landmark fit; native matrices preserved in raw data','clip_type':'continuous sampled pass, not a seamless loop'}
    output.with_suffix('.validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('SAVED CAPTURED LEFT WALK:',output)
    return report

def main():
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    p=argparse.ArgumentParser();p.add_argument('--log',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--template',type=Path)
    args=p.parse_args(argv);build(load_capture(args.log),args.output,args.template)
if __name__=='__main__':main()
