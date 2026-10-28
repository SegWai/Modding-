"""Verify final support IK condition and scope from actual v177 trace evidence."""
from pathlib import Path
import sys,re,json,itertools
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));from dayz_graph_formats import newnodes
base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v177';out=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v178'
a=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((out/'WorkspaceSource/locomotion.agf').read_text());assert a.keys()==b.keys()
spec=json.loads((out/'Final-Walking-Grip-v178.json').read_text());changed=[]
for name in a:
 if a[name]==b[name]:continue
 changed.append(name);assert name=='ML166_PublishFinalAimedWeapon'
 assert a[name].replace('WeightSecondaryChain "'+spec['old_expression']+'"','WeightSecondaryChain "'+spec['new_expression']+'"',1)==b[name]
assert changed==['ML166_PublishFinalAimedWeapon']
# All non-preview actors retain old behavior, all off-centre paths unchanged,
# only centred moving preview rifles newly solve the support chain.
cases=0;enabled=0
for preview,move,pitch,yaw,rifle,fp in itertools.product([0,1],[0,.49,.51,1],[-90,-5,0,5,90],[-90,0,90],[0,1],[0,1]):
 old=(abs(pitch)>5 or abs(yaw)>5) and rifle>.5 and fp<.5
 new=((preview>.5 and move>.5) or abs(pitch)>5 or abs(yaw)>5) and rifle>.5 and fp<.5
 if preview==0 or move<=.5 or abs(pitch)>5 or abs(yaw)>5:assert new==old
 if new!=old:assert preview==1 and move>.5 and rifle==1 and fp==0;enabled+=1
 cases+=1
assert enabled>0
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','MLWalkingLeanPreset.json','LogicSource/Presets/MLWalkingLeanPreset.json','Profiles/LeanMosin/MLWalkingLeanPreset.json','LogicSource/Presets/MLWalkingArmBaseline.json','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
 assert (base/rel).read_bytes()==(out/rel).read_bytes(),rel
for p in (base/'LogicSource/Scripts/4_World').glob('*.c'):assert p.read_bytes()==(out/p.relative_to(base)).read_bytes()
for p in (base/'LogicSource/Scripts/5_Mission').glob('*.c'):
 text=p.read_text();new=(out/p.relative_to(base)).read_text()
 if p.name in ['MLPoseEditorMenu144.c','MLBodyMenu149.c']:
  assert text.replace('   GetGame().GetMission().RemoveActiveInputExcludes(m_Excludes);','   if (GetGame() && GetGame().GetMission())\n    GetGame().GetMission().RemoveActiveInputExcludes(m_Excludes);',1)==new
 else:assert text==new
# Counter compile fix stays in place, no indexed ++/-- reintroduced.
for p in (out/'LogicSource/Scripts').rglob('*.c'):assert not re.search(r'\]\s*(\+\+|--)|(\+\+|--)\s*[A-Za-z_]\w*\[',p.read_text()),p
# Check numerical evidence without private user paths in committed output.
evidence=json.loads((out/'Walking-Arm-Trace-Evidence-v178.json').read_text());samples=evidence['samples']
assert len(samples)==9 and evidence['capture_count']==1 and evidence['values_revision']==5
assert all(x['arm_correction']==samples[0]['arm_correction'] and x['hand_correction']==samples[0]['hand_correction'] for x in samples)
ys=[x['elbow'][1] for x in samples];span=max(ys)-min(ys);assert span>.25
result={'graph_changed_fields':1,'graph_condition_cases':cases,'newly_enabled_centred_preview_cases':enabled,'constant_correction_trace_samples':9,'observed_elbow_vertical_span_m':span,'all_presets_and_world_scripts_unchanged':True,'native_compile_and_grip_resolution':'NOT RUN'}
(out/'Final-Walking-Grip-Checks-v178.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
