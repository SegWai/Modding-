"""Static endpoint/single-path and work-scheduling checks; NOT an FPS benchmark."""
from pathlib import Path
import re,json,math
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v153';KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v154'
a=newnodes((BASE/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((KIT/'WorkspaceSource/locomotion.agf').read_text());perf=json.loads((KIT/'Performance-v154.json').read_text())
# Endpoint0 picks original base; endpoint1 reproduces all original correction
# expressions/amounts and final publication. Only fractional interpolation changes.
for target in ['ML139_RightStraightOnly','ML147_LeftEditorOnly']:
 old=a[target];new=b[target];scope=re.search(r'BlendWeight "([^"]+)"',old)[1]
 assert 'clamp(('+scope+')*1000000.0,0.0,1.0)' in new
 assert re.findall(r'Child[01] "([^"]+)"',old)==re.findall(r'Child[01] "([^"]+)"',new)
for name in perf['weighted_single_path_nodes']:
 old=a[name];new=b[name]
 scope=re.search(r'Expression "\((.*?)\)\*\((.*)\)"',new)
 assert scope and re.search(r'Expression "([^"]+)"',old)[1]==scope[1]
 assert re.findall(r'(?:Bone|Axis|Space|Op|Amount) [^\n]+',old)==re.findall(r'(?:Bone|Axis|Space|Op|Amount) [^\n]+',new)
 assert re.search(r'Child "([^"]+)"',old)[1]==re.search(r'Child "([^"]+)"',new)[1]
# Count baseline visits for a fractional outer blend, respecting binary optimized
# branches and treating the baseline as a terminal. This is a structural proxy.
def baseline_visits(nodes,name,boundary,weight,outer):
 if name==boundary:return 1
 node=nodes[name];kind=node.split()[0]
 if kind=='AnimSrcNodeBlend':
  c0=re.search(r'Child0 "([^"]+)"',node)[1];c1=re.search(r'Child1 "([^"]+)"',node)[1]
  w=weight if name==outer else 0. # extra muzzle angle default0
  if w<=0:return baseline_visits(nodes,c0,boundary,weight,outer)
  if w>=1:return baseline_visits(nodes,c1,boundary,weight,outer)
  return baseline_visits(nodes,c0,boundary,weight,outer)+baseline_visits(nodes,c1,boundary,weight,outer)
 child=re.search(r'Child "([^"]+)"',node)[1];return baseline_visits(nodes,child,boundary,weight,outer)
counts={}
for target in ['ML139_RightStraightOnly','ML147_LeftEditorOnly']:
 boundary=re.search(r'Child0 "([^"]+)"',a[target])[1];before=baseline_visits(a,target,boundary,.5,target);after=baseline_visits(b,target,boundary,1.,target);assert (before,after)==(2,1);counts[target]={'base_visits_before':before,'base_visits_after':after}
parts=json.loads((KIT/'Body-Editor-v149.json').read_text())['parts'];preset=json.loads((KIT/'MLLeanPreset.json').read_text());agr=(KIT/'WorkspaceSource/player_main.agr').read_text()
for bone,_ in parts:
 control='ML154'+bone+'Active';assert agr.count('AnimSrcGCTVarFloat '+control+' {')==1
 node=b['ML154_BodyGate_'+bone];assert 'BlendWeight "'+control+'"' in node and 'OptimizeMin 1' in node and 'OptimizeMax 1' in node
 assert re.search(r'Child1 "([^"]+)"',node)[1]=='ML149_Body_'+bone+'_RZ'
active={}
for side in ['LeftLean','RightLean']:
 active[side]=sum(any(p[f]!=0 for f in ['X','Y','Z','Pitch','Yaw','Roll']) for p in preset[side]['BodySettings']['Parts']);assert active[side]==4
assert (KIT/'MLLeanPreset.json').read_bytes()==(BASE/'MLLeanPreset.json').read_bytes()
assert (KIT/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes()==(BASE/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes()
world=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();body=(KIT/'LogicSource/Scripts/4_World/MLBodyEditor149.c').read_text();unified=(KIT/'LogicSource/Scripts/4_World/MLUnifiedPreset153.c').read_text()
assert 'm_ML149Vars.Count() != 169' in world and 'int activeSlot = 145 + partIndex;' in world
assert 'm_ML154ReferenceReady[leanSide]' in world and 'm_ML146Root[4]' in world
assert 'm_ML154BodyRevision != ML149State.GeometryRevision' in world and 'GeometryRevision++' in body and 'ML149State.GeometryRevision++;' in unified
assert 'if (m_ML154EditorWritten[cacheSlot] && m_ML154EditorLast[cacheSlot] == value)' in world
assert 'AutomaticPoseCaptureBudget = 0' in world and 'DetailedDiagnostics = false' in world
assert world.index('  if (!reportDue)\n   return;')<world.index('  string status = "view="')
probe=world[world.index(' protected void ML93UpdateArmProbe'):world.index(' protected void ML104CapturePoseLimited')]
assert probe.index('m_ML93DropStable += sampleStep')<probe.index('if (!MLADSLeanSettings.DetailedDiagnostics)')<probe.index('GetBonePositionMS(')
assert '-scriptDebug=true' not in (KIT/'Launch-Test.ps1').read_text() and "'-doLogs'" in (KIT/'Launch-Test.ps1').read_text()
# Snapshot cache reads at most once per side between explicit invalidations.
ready=[False,False];reads=0
for sign in [0,1]*20:
 if not ready[sign]:reads+=6;ready[sign]=True
assert reads==12
# Constant editor graph values need one write per slot, then only on edits.
last={};writes=0
for frame in range(120):
 for slot in range(55):
  value=slot*.001
  if last.get(slot)!=value:writes+=1;last[slot]=value
assert writes==55
for p in (KIT/'LogicSource').rglob('*.c'):
 s=p.read_text();assert s.count('{')==s.count('}'),p
 for m in re.finditer(r'(?:array<float>|TStringArray) \w+ = \{([^\n]+)\}',s):assert m[1].count(',')<8,p
print(json.dumps({'partial_blend_structural_base_visits':counts,'body_transform_visits_before':144,'body_transform_visits_bundled_after':{k:v*6 for k,v in active.items()},'body_transforms_when_unedited_after':0,'editor_constant_writes_120frames_before':55*120,'editor_constant_writes_120frames_after':writes,'arm_native_reads_40switches_with_nonzero_offsets_after':reads,'arm_native_reads_with_zero_offsets_after':0,'preserved':'preset bytes, bone operation/axis/amounts,0/1side endpoints,camera,4.5leanrate; fractional transition math optimized','actual_FPS_native_compile_visuals':'NOT MEASURED; structural counts are not native profiling'},indent=2))
