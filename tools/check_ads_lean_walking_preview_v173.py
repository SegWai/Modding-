"""Offline scope isolation, native-preview routing and graph regression checks."""
from pathlib import Path
import sys,re,json,hashlib,random,math,copy
sys.path.insert(0,str(Path(__file__).parent))
from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v172';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v173'
w=b/'LogicSource/Scripts/4_World';m=b/'LogicSource/Scripts/5_Mission'
expected='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
for f in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','MLWalkingLeanPreset.json','Profiles/LeanMosin/MLWalkingLeanPreset.json']:
 assert hashlib.sha256((b/f).read_bytes()).hexdigest()==expected,f
# Parse the exact bank exchange statements, simulate updates and early exits.
scope=(w/'MLWalkingEditorScope173.c').read_text();ent=scope.split(' void Enter()')[1].split(' void Leave()')[0];leave=scope.split(' void Leave()')[1]
assign=re.compile(r'^  (\w+(?:\.\w+)?) = (\w+(?:\.\w+)?);',re.M)
enter_ops=assign.findall(ent);leave_ops=assign.findall(leave)
assert len(enter_ops)==len(leave_ops)==56
keys={v for pair in enter_ops+leave_ops for v in pair};rng=random.Random(173)
for _ in range(100):
 state={k:{'id':rng.random()} for k in keys};baseline={k:v for k,v in state.items() if k.startswith(('ML144State.','ML149State.'))}
 for dest,source in enter_ops:state[dest]=state[source]
 # Changes inside the update persist to walking bank, even on a simulated return.
 changed={k:{'edited':rng.random()} for k in baseline}
 state.update(changed)
 for dest,source in leave_ops:state[dest]=state[source]
 assert all(state[k] is v for k,v in baseline.items())
 for k,v in changed.items():
  bk=k.replace('ML144State','ML173WeaponState').replace('ML149State','ML173BodyState')
  assert state[bk] is v
# New JSON loading allocates independent trees; edits/save cannot touch baseline.
preset=(w/'MLWalkingEditor173.c').read_text()
assert 'class ML173Preset' in preset and 'ML173PresetFile' not in preset
assert 'FilePath = "$profile:MLWalkingLeanPreset.json"' in preset
assert 'BackupPath = "$profile:MLWalkingLeanPreset.json.bak"' in preset
assert 'ML153Preset.Save()' not in preset and 'ML153Preset.Install(' not in preset
base=json.loads((b/'MLLeanPreset.json').read_text());walk=json.loads((b/'MLWalkingLeanPreset.json').read_text());original=copy.deepcopy(base)
walk['LeftLean']['WeaponSettings']['X']=10;walk['RightLean']['BodySettings']['Parts'][0]['Roll']=20
assert base==original
for name in ['MLPoseEditorMenu144.c','MLBodyMenu149.c','MLADSLeanKeys.c']:
 text=(m/name).read_text();assert 'ML144State.' not in text and 'ML149State.' not in text
assert 'ML173Preset.Init();' in (m/'MLPoseEditorMenu144.c').read_text()
# Unedited actors get exactly the previous graph math for preview flag zero.
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
assert old.keys()==new.keys()
changed=[k for k in old if old[k]!=new[k]]
spec=json.loads((b/'Walking-Preview-v173.json').read_text());assert set(changed)==set(spec['modified_editor_nodes'])
fields=re.compile(r'\b(Expression|BlendWeight|WeightAim|WeightPrimaryChain|WeightSecondaryChain|WeaponDirLr|WeaponDirUd|WeaponRoll) "([^"]*)"')
def ev(expr,values):
 expr=expr.replace('&&',' and ').replace('||',' or ')
 expr=re.sub(r'!(?!=)',' not ',expr)
 return eval(expr,{'__builtins__':{}},dict(values,clamp=lambda x,lo,hi:max(lo,min(hi,x)),abs=abs,true=True,false=False))
count=0
for name in changed:
 f0=fields.findall(old[name]);f1=fields.findall(new[name]);assert len(f0)==len(f1)
 # No changed children, bones, operations, branch optimization or IK config.
 assert fields.sub('',old[name])==fields.sub('',new[name]),name
 for (k,x),(k1,y) in zip(f0,f1):
  assert k==k1
  if x==y:continue
  identifiers=set(re.findall(r'\b[A-Za-z_]\w*\b',x+' '+y)) - {'clamp','abs','true','false','e'}
  for _ in range(50):
   vals={v:rng.uniform(-1,2) for v in identifiers};vals['ML173WalkingPreview']=0
   assert math.isclose(ev(x,vals),ev(y,vals),rel_tol=1e-12,abs_tol=1e-12),(name,k)
   count+=1
# The previous left-walk-stop crash safeguards remain unchanged.
for name in ['ML104_LeftElbowDirections','ML118_ContactHoldOnly','ML130_StandingLeftOnly','ML133_StandingLeftElbow']:
 assert new[name]==old[name]
player=(w/'MLADSLeanPlayer.c').read_text();handler=player.split(' override void CommandHandler(')[1].split(' protected void ML173UpdateGraph(')[0]
assert handler.count('return;')==1 and handler.index('return;')<handler.index('m_ML173Scope.Enter()')
assert handler.index('Enter()')<handler.index('super.CommandHandler')<handler.index('ML173UpdateGraph')<handler.index('SetPosition(m_ML173Anchor)')<handler.index('Leave()')
assert 'previewSpeed = 1;' in player and 'previewAngle = -90;' in player and 'previewAngle = 90;' in player
assert 'if (m_MLADSLeanDemo || !m_ML149Bound)' in player # v172 does not overwrite walking preview
assert 'if (editorHold)' in player and 'bool editorHold = ML173WeaponState.Open;' in player
assert player.count('BindVariableFloat("ML173WalkingPreview")')==1
mission=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert mission.count('GetHumanInventory().CreateInHands("AK74")')==2
assert 'right * 2.5' in mission and 'm_ML173NPC.ML173StartWalkingDemo()' in mission
assert 'GetGame().ObjectDelete(m_ML173NPC)' in mission
# All unmentioned native grip/head/camera/loadout helpers unchanged.
for f in (a/'LogicSource/Scripts/4_World').glob('*.c'):
 if f.name!='MLADSLeanPlayer.c':assert f.read_bytes()==(w/f.name).read_bytes(),f.name
# Balanced script blocks and no duplicate new classes.
alltext='\n'.join(p.read_text() for p in (b/'LogicSource/Scripts').rglob('*.c'))
classes=re.findall(r'^class (\w+)',alltext,re.M);assert len(classes)==len(set(classes))
for f in (b/'LogicSource/Scripts').rglob('*.c'):
 text=re.sub(r'//[^\n]*|"(?:\\.|[^"\\])*"','',f.read_text());assert text.count('{')==text.count('}'),f
result={'scope_isolation_cases':100,'unmodified_actor_expression_cases':count,'changed_editor_nodes':len(changed),'stationary_preset_sha256':expected,'native_compile_and_playback':'NOT RUN'}
(b/'Walking-Preview-Checks-v173.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
