"""Regression checks for arm-reference lifecycle and idempotent editor events."""
from pathlib import Path
import re,json
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v175';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v176';w=b/'LogicSource/Scripts/4_World'
state=(w/'MLWalkingEditor173.c').read_text();player=(w/'MLADSLeanPlayer.c').read_text()
assert 'if (SameWeaponValues(candidate, Values))\n   return true;' in state
assert 'Values == SideValues(left)' in state # loading new refs still refreshes selected UI values
select=state.split(' static void SelectSide(')[1].split(' static void Init()')[0]
assert 'HoldRevision++' not in select and 'ValuesRevision++' in select
assert 'if (identical)\n   return true;\n  data.Parts[SelectedPart] = part;' in state
assert 'if (!m_ML173Walking && m_ML154BodyRevision != ML149State.GeometryRevision)' in player
assert '&& m_ML104CalibAttempts < 3)' in player # no endless capture starvation if native pole solve fails
assert 'if (!m_ML146Ready)\n  {\n   if (stable)' in player
assert 'm_ML176CaptureCount[leanSide]++;' in player
assert 'm_ML176SampleCount[sideIndex] >= 12' in player
for name,n in [('MLPoseEditorMenu144.c',17),('MLBodyMenu149.c',6)]:
 text=(b/'LogicSource/Scripts/5_Mission'/name).read_text()
 assert f'm_ML176Displayed[{n}]' in text
 assert 'm_ML176Displayed[i] = m_Sliders[i].GetCurrent();' in text
 assert 'm_Sliders[index].GetCurrent() != m_ML176Displayed[index]' in text
# Lifecycle model exercises repeated unchanged native widget events while held.
# Old behavior invalidates on every accepted F7 event; new behavior ignores
# no-op events and also keeps the reference for downstream actual F7 edits.
class Ref:
 def __init__(self,old=False):self.old=old;self.ready=False;self.time=0;self.captures=0
 def tick(self,dt,event=None):
  if event=='weapon_hold' or (self.old and event in ('body_same','body_edit','select_same')):self.ready=False;self.time=0
  if not self.ready:
   self.time+=dt
   if self.time>.2:self.ready=True;self.captures+=1
old=Ref(True);new=Ref()
for frame in range(3600):
 event='body_same' if frame%30==0 else None
 old.tick(1/60,event);new.tick(1/60,event)
assert old.captures>50 and new.captures==1
for event in ['body_edit','select_same',None]*120:new.tick(1/60,event)
assert new.captures==1
new.tick(1/60,'weapon_hold')
for _ in range(60):new.tick(1/60)
assert new.captures==2
# Uploaded saved zero/baseline and actual animation graph remain byte-identical.
for rel in ['WorkspaceSource/locomotion.agf','MLWalkingLeanPreset.json','Profiles/LeanMosin/MLWalkingLeanPreset.json','MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','LogicSource/Presets/MLWalkingArmBaseline.json','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes(),rel
# Full baseline roundtrip math reused for new version, adjusted only for panels
# whose notification filtering changed, not their layout/controls.
source=(r/'tools/check_ads_lean_arm_zero_v174.py').read_text().replace("b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v174'", "b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v176'").replace("['LogicSource/Scripts/5_Mission','LogicSource/GUI']", "['LogicSource/GUI']").replace('Arm-Zero-Checks-v174.json','Arm-Zero-Checks-v176.json')
exec(compile(source,str(r/'tools/check_ads_lean_arm_zero_v174.py'),'exec'),{'__file__':str(r/'tools/check_ads_lean_arm_zero_v174.py')})
result={'steady_hold_model_frames':3600,'old_recaptures_under_noop_body_events':old.captures,'new_captures_until_actual_hold_change':1,'new_captures_after_real_hold_change':new.captures,'graph_and_presets_unchanged':True,'native_compilation_and_oscillation_resolution':'NOT RUN'}
(b/'Arm-Stability-Checks-v176.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
