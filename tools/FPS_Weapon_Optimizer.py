"""FPS weapon mesh optimizer for Blender 3.6+ / 4.x.
Run from Blender > Scripting with your weapon project open.
Creates copies only. This is automated simplification, not manual retopology.
"""
import bpy, bmesh, os, json, math
from datetime import datetime

QUALITY = "HIGH"  # ULTRA / HIGH / BALANCED / AGGRESSIVE
TARGET_TRIANGLES = 35000  # soft goal only
SAVE_BLEND_COPY = True
EXPORT_FBX = False
INCLUDE_HIDDEN_OBJECTS = False
RATIOS = {"ULTRA": .98, "HIGH": .90, "BALANCED": .80, "AGGRESSIVE": .65}
if QUALITY not in RATIOS: raise ValueError("Invalid QUALITY")
ratio = RATIOS[QUALITY]
src = bpy.data.filepath
outdir = os.path.dirname(src) if src else os.path.expanduser("~")
base = os.path.splitext(os.path.basename(src))[0] if src else "weapon"
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
prefix = f"{base}_FPS_{QUALITY.lower()}_{stamp}"
col = bpy.data.collections.new("FPS_OPTIMIZED_" + stamp)
bpy.context.scene.collection.children.link(col)
report = {"source":src,"quality":QUALITY,"target_soft":TARGET_TRIANGLES,"objects":[],"warnings":[]}
created = []

def stats(mesh):
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    d = dict(vertices=len(mesh.vertices), faces=len(mesh.polygons),
             triangles=len(mesh.loop_triangles), uv_layers=len(mesh.uv_layers),
             non_tri_faces=sum(len(f.verts)!=3 for f in bm.faces),
             nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),
             boundary_edges=sum(e.is_boundary for e in bm.edges))
    bm.free()
    return d

sources = [o for o in list(bpy.context.scene.objects) if o.type=="MESH"
           and not o.name.endswith("_FPS_OPT")
           and not any(c.name.startswith("FPS_OPTIMIZED_") for c in o.users_collection)
           and (INCLUDE_HIDDEN_OBJECTS or (not o.hide_get() and not o.hide_viewport))]
if not sources: raise RuntimeError("No eligible mesh objects found")

for original in sources:
    item = {"name":original.name,"before":stats(original.data)}
    clone = original.copy()
    clone.name = original.name + "_FPS_OPT"
    try:
        dg = bpy.context.evaluated_depsgraph_get()
        evaluated = original.evaluated_get(dg)
        clone.data = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=dg)
    except Exception as ex:
        item["evaluation_warning"]=str(ex)
        clone.data = original.data.copy()
    # The evaluated mesh already includes source modifiers; don't reapply them.
    clone.modifiers.clear()
    col.objects.link(clone)
    created.append(clone)
    item["evaluated"]=stats(clone.data)
    rigged = bool(original.vertex_groups) or bool(original.data.shape_keys) or any(
        m.type=="ARMATURE" for m in original.modifiers) or bool(
        original.parent and original.parent.type=="ARMATURE")
    if len(clone.data.polygons) and not rigged:
        try:
            bm=bmesh.new(); bm.from_mesh(clone.data)
            bmesh.ops.dissolve_limit(bm,angle_limit=math.radians(1.0),
                verts=list(bm.verts),edges=list(bm.edges),
                delimit={'UV','MATERIAL','SEAM','SHARP','NORMAL'})
            bm.to_mesh(clone.data); bm.free(); clone.data.update()
        except Exception as ex:
            item["dissolve_warning"]=str(ex)
        if stats(clone.data)["triangles"]>=800:
            mod=None
            try:
                mod=clone.modifiers.new("FPS_Decimate","DECIMATE")
                mod.decimate_type="COLLAPSE"; mod.ratio=ratio
                bpy.ops.object.select_all(action="DESELECT")
                clone.hide_set(False); clone.select_set(True)
                bpy.context.view_layer.objects.active=clone
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except Exception as ex:
                item["decimate_warning"]=str(ex)
                if mod and mod.name in clone.modifiers: clone.modifiers.remove(mod)
    elif rigged:
        item["reduction_skipped"]="Rigged or shape-key mesh: preserve deformation"
    try:
        bm=bmesh.new(); bm.from_mesh(clone.data)
        if bm.faces:
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            bmesh.ops.triangulate(bm,faces=list(bm.faces),
                quad_method="BEAUTY",ngon_method="BEAUTY")
        bm.to_mesh(clone.data); bm.free(); clone.data.update()
    except Exception as ex:
        item["triangulation_warning"]=str(ex)
    item["after"]=stats(clone.data)
    report["objects"].append(item)

a=sum(x["evaluated"]["triangles"] for x in report["objects"])
b=sum(x["after"]["triangles"] for x in report["objects"])
report["totals"]={"evaluated_triangles":a,"optimized_triangles":b,
    "reduction_percent":round(100*(a-b)/a,2) if a else 0,
    "nontri_faces":sum(x["after"]["non_tri_faces"] for x in report["objects"]),
    "nonmanifold_edges":sum(x["after"]["nonmanifold_edges"] for x in report["objects"])}
if b>TARGET_TRIANGLES:
    report["warnings"].append("Soft triangle target not reached; avoid blind additional decimation.")
report["warnings"].append("Check UVs, normals, silhouette, attachments, animation and LODs manually.")
report["warnings"].append("Not a manual retopology tool or DayZ P3D exporter.")
report_path=os.path.join(outdir,prefix+"_report.json")
with open(report_path,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
if EXPORT_FBX:
    try:
        bpy.ops.object.select_all(action="DESELECT")
        for o in created: o.select_set(True)
        bpy.context.view_layer.objects.active=created[0]
        bpy.ops.export_scene.fbx(filepath=os.path.join(outdir,prefix+".fbx"),
                                 use_selection=True,add_leaf_bones=False)
    except Exception as ex: print("FBX export failed:",ex)
if SAVE_BLEND_COPY:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(outdir,prefix+".blend"),copy=True)
print("FPS optimization complete:",report["totals"])
print("Report:",report_path)
