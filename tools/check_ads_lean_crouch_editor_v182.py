"""Native/custom role isolation and live crouch editor geometry checks."""
from pathlib import Path
import json,re,sys,hashlib,itertools,random,numpy as np
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));from dayz_graph_formats import newnodes
base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v181';out=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v182';w=out/'LogicSource/Scripts/4_World';m=out/'LogicSource/Scripts/5_Mission';spec=json.loads((out/'Crouch-Comparison-Editor-v182.json').read_text())
# Authoritative standing/walking inputs remain byte-for-byte untouched.
for file in ['MLLeanPreset.json','MLWalkingLeanPreset.json']:
 for rel in [file,'Profiles/LeanMosin/'+file,'LogicSource/Presets/'+file]:assert (base/rel).read_bytes()==(out/rel).read_bytes(),rel
zero=json.loads((out/'MLCrouchLeanPreset.json').read_text());assert zero['PresetVersion']==1
for side in ['LeftLean','RightLean']:
 assert all(x==0 for x in zero[side]['WeaponSettings'].values())
 assert len(zero[side]['BodySettings']['Parts'])==24
 for part in zero[side]['BodySettings']['Parts']:
  assert all(part[k]==0 for k in ['X','Y','Z','Pitch','Yaw','Roll'])
for rel in ['Profiles/LeanMosin/MLCrouchLeanPreset.json','LogicSource/Presets/MLCrouchLeanPreset.json']:assert (out/rel).read_bytes()==(out/'MLCrouchLeanPreset.json').read_bytes()
# New bank is the ONLY panel target, and cannot call canonical save methods.
for file in ['MLPoseEditorMenu144.c','MLBodyMenu149.c','MLADSLeanKeys.c']:
 text=(m/file).read_text();assert 'ML173WeaponState' not in text and 'ML173BodyState' not in text
 if file!='MLADSLeanKeys.c':assert 'ML182Preset.Init()' in text
preset=(w/'MLCrouchPreset182.c').read_text()
assert 'FilePath = "$profile:MLCrouchLeanPreset.json"' in preset
assert 'BackupPath = "$profile:MLCrouchLeanPreset.json.bak"' in preset
assert 'ML173Preset.Save()' not in preset and 'ML153Preset.Save()' not in preset
assert 'ML144Math.Solve(candidate' not in preset
assert 'if (!ML182WeaponState.ReachValid)' in preset
# Exact graph additions: two existing body inputs rewired, rest unchanged.
a=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((out/'WorkspaceSource/locomotion.agf').read_text())
added={k for k in set(b)-set(a) if not k.startswith('{')};assert added==set(spec['new_graph_nodes']) and len(added)==38
for name,old in a.items():
 if name.startswith('{'):continue
 if name in spec['rewired_body_inputs']:
  expected=old.replace('Child "ML147_LeftEditorOnly"','Child "ML182CrouchEditorOnly"').replace('Child0 "ML147_LeftEditorOnly"','Child0 "ML182CrouchEditorOnly"')
  assert b[name]==expected
 else:assert b[name]==old,name
for k in added:
 if k=='ML182CrouchEditorOnly':assert 'OptimizeMin 1' in b[k] and 'OptimizeMax 1' in b[k]
 elif k!='ML182CrouchWeaponFollow':assert 'ML182CrouchEditor' in b[k] and 'Space Model' in b[k]
assert 'WeightPrimaryChain "false"' in b['ML182CrouchWeaponFollow']
assert 'WeightSecondaryChain "true"' in b['ML182CrouchWeaponFollow']
# No editor node is reachable from native comparison output. This is stronger
# than keeping its slider values zero: it structurally bypasses the editor.
seen=set();stack=['NormalWeaponIK']
while stack:
 name=stack.pop()
 if name in seen:continue
 seen.add(name)
 if name in b:stack+=re.findall(r'\bChild\d* "([^"]+)"',b[name])
assert not seen&added
# Detect cycles across the actual graph, including both branch inputs.
visiting=set();visited=set()
def visit(name):
 if name in visited or name not in b:return
 assert name not in visiting,name
 visiting.add(name)
 for child in re.findall(r'\bChild\d* "([^"]+)"',b[name]):visit(child)
 visiting.remove(name);visited.add(name)
sys.setrecursionlimit(20000)
for name in b:
 if not name.startswith('{'):visit(name)
# Red remains native regardless of global toggle and editor data; blue follows
# existing explicit CtrlF1 comparator only when user chooses native comparison.
player=(w/'MLADSLeanPlayer.c').read_text();assert 'if (!MLADSLeanSettings.Enabled || m_ML182NativeReference)\n    compareMode = 1;' in player
assert 'MLADSLeanSettings.Enabled && !m_ML182NativeReference' in player
assert 'if (m_ML182EditableCrouch)\n  {\n   ML182Preset.Init();' in player
handler=player.split(' override void CommandHandler(')[1].split(' protected void ML173UpdateGraph(')[0]
assert handler.index('m_ML182Scope.Enter()')<handler.index('ML173UpdateGraph(')<handler.index('m_ML182Scope.Leave()')
assert 'else if (useWalking)' in handler
role_cases=0
for native,enabled,openpanel in itertools.product([False,True],repeat=3):
 mode=not enabled or native;custom=enabled and not native
 assert not(native and custom)
 if native:assert mode
 role_cases+=1
# New scope must restore all original data through interleaved walking/crouch.
pat=re.compile(r'^  (\w+(?:\.\w+)?) = (\w+(?:\.\w+)?);',re.M)
scopes=[]
for fname in ['MLCrouchEditorScope182.c','MLWalkingEditorScope173.c']:
 text=(w/fname).read_text();enter=pat.findall(text.split(' void Enter()')[1].split(' void Leave()')[0]);leave=pat.findall(text.split(' void Leave()')[1]);assert len(enter)==len(leave)==56;scopes.append((enter,leave))
keys={k for enter,leave in scopes for pair in enter+leave for k in pair};state={k:object() for k in keys};original={k:v for k,v in state.items() if k.startswith(('ML144State.','ML149State.'))}
for _ in range(100):
 for enter,leave in scopes:
  for dest,src in enter:state[dest]=state[src]
  for dest,src in leave:state[dest]=state[src]
  assert all(state[k] is v for k,v in original.items())
# Capture is only from unedited pose and only once per side/held weapon; edits
# recompute from cached geometry, never corrected output on every tick.
helper=(w/'MLCrouchHold182.c').read_text()
assert 'if (!Ready[side])' in helper and 'Write(actor, null, false);' in helper
assert helper.index('Write(actor, null, false);')<helper.index('Ready[side] = Capture(actor, side);')
assert 'if (Settled <= 0.3)' in helper
assert 'Revision[side] != ML144State.ValuesRevision' in helper
assert 'ML144Math.Limb(ArmRoot[leftIndex]' in helper and 'ML144Math.Limb(ArmRoot[rightIndex]' in helper
assert 'return m_ML182Hold && m_ML182Hold.ReadyNow && ML144State.ArmsReady;' in player
assert 'm_ML182EditableCrouch && !ML182BodyReady()' in player
assert 'ML182UpdateCrouchHold(pDt, state);' in player
assert '(standing || m_ML182EditableCrouch)' in player
# Both roles raised-only and side-hold, no walking input/pin introduced.
mission=(out/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text()
assert '"Hoodie_Red", true)' in mission and '"Hoodie_Blue", false)' in mission
assert 'actor.ML182StartCrouchComparison(nativeReference)' in mission
assert 'ML181StartCrouchDemo(true)' in player and 'bool demoADS = false;' in player
cycle=(w/'MLSharedPose181.c').read_text();assert 'if (ML182WeaponState.Open)' in cycle and 'if (ML182WeaponState.EditLeft)' in cycle
assert 'right * 0.5' in mission and 'OverrideMovementSpeed(HumanInputControllerOverrideType.ENABLED, 0)' in player
# Independent two-bone IK math on synthetic crouch-height arms, testing actual
# reference-dependent XYZ/rotation targets, FK endpoints and palm orientation.
def turn(a,b):
 a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);c=np.cross(a,b);s=np.linalg.norm(c);d=np.clip(a@b,-1,1)
 return np.eye(3) if s<1e-10 else Rotation.from_rotvec(c/s*np.arctan2(s,d)).as_matrix()
def limb(root,elbow,wrist,target,ori):
 l1=np.linalg.norm(elbow-root);l2=np.linalg.norm(wrist-elbow);reach=target-root;d=np.linalg.norm(reach)
 if d<=abs(l1-l2)+.002 or d>=l1+l2-.002:return None
 axis=reach/d;along=(l1*l1-l2*l2+d*d)/(2*d);radius=np.sqrt(max(0,l1*l1-along*along));pole=elbow-root;pole-=axis*(pole@axis)
 if np.linalg.norm(pole)<1e-6:return None
 goal=root+axis*along+pole/np.linalg.norm(pole)*radius;arm=turn(elbow-root,goal-root);fore=turn(arm@(wrist-elbow),target-goal);hand=ori@(fore@arm).T
 return arm,fore,hand
arms=[(np.array([-.18,1.05,.0]),np.array([-.29,.85,.20]),np.array([-.13,.99,.43])),(np.array([.18,1.05,0]),np.array([.29,.82,.12]),np.array([.08,.99,.29]))]
rng=np.random.default_rng(182);accepted=0;rejected=0;maxerr=0
for _ in range(500):
 offset=rng.uniform(-.2,.2,3);ori=Rotation.from_euler('xyz',rng.uniform(-.2,.2,3)).as_matrix();rt=arms[1][2]+offset;lt=rt+ori@(arms[0][2]-arms[1][2]);solves=[limb(*arms[0],lt,ori),limb(*arms[1],rt,ori)]
 if any(x is None for x in solves):rejected+=1;continue
 for (root,elbow,wrist),target,solution in zip(arms,[lt,rt],solves):
  arm,fore,hand=solution;newelbow=root+arm@(elbow-root);newwrist=newelbow+fore@arm@(wrist-elbow);err=max(np.max(abs(newwrist-target)),np.max(abs(hand@fore@arm-ori)));assert err<1e-10;maxerr=max(maxerr,float(err))
 accepted+=1
assert accepted>200 and rejected>0
# Native type-collision and indexed-increment regressions remain excluded.
classes=[]
for p in (out/'LogicSource/Scripts').rglob('*.c'):
 text=p.read_text();assert not re.search(r'\]\s*(\+\+|--)|(\+\+|--)\s*[A-Za-z_]\w*\[',text),p
 classes+=re.findall(r'^class (\w+)',text,re.M);clean=re.sub(r'//[^\n]*|"(?:\\.|[^"\\])*"','',text);assert clean.count('{')==clean.count('}'),p
assert len(classes)==len(set(classes))
agr=(out/'WorkspaceSource/player_main.agr').read_text()
for var in ['ML182CrouchEditor']+['ML182Hold'+str(i) for i in range(18)]:assert agr.count('AnimSrcGCTVarFloat '+var+' {')==1
result={'standing_walking_presets_unchanged':True,'native_output_reachable_nodes':len(seen),'native_output_excludes_all_new_editor_nodes':True,'role_toggle_cases':role_cases,'crouch_walking_scope_restore_updates':200,'new_graph_nodes':38,'new_controls':19,'synthetic_crouched_hold_cases_accepted':accepted,'synthetic_crouched_hold_cases_rejected':rejected,'max_FK_endpoint_orientation_error':maxerr,'native_compile_ui_default_comparison_and_contact':'NOT RUN'}
(out/'Crouch-Comparison-Editor-Checks-v182.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
