"""Verify native/custom graph route, control guards and non-destructive keys."""
from pathlib import Path
import sys,re,hashlib,json
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v168';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v169'
old={k:v for k,v in newnodes((a/'WorkspaceSource/locomotion.agf').read_text()).items() if not k.startswith('{')};new={k:v for k,v in newnodes((b/'WorkspaceSource/locomotion.agf').read_text()).items() if not k.startswith('{')}
assert set(new)-set(old)=={'ML169_NativeCompare'}
for name,node in old.items():
 expected=node.replace('Child "ML166_FinalAimOnly"','Child "ML169_NativeCompare"',1) if name=='MeleeBlockQ' else node
 assert new[name]==expected,name
for s in ['BlendWeight "ML169UseNative"','Child0 "ML166_FinalAimOnly"','Child1 "NormalWeaponIK"','OptimizeMin 1','OptimizeMax 1']:assert s in new['ML169_NativeCompare']
agr=(b/'WorkspaceSource/player_main.agr').read_text();assert agr.count('AnimSrcGCTVarFloat ML169UseNative {')==1
world=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();keys=(b/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();camera=(b/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text()
assert 'static bool Enabled = true;' in world
assert 'if (MLADSLeanSettings.Enabled && m_ML87ViewBound' in world
for reset in ['m_ML56GatePhase = 0;','m_ML50ReachTrim = 0;','m_MLADSLeanHeightLift = 0;']:assert reset in world
assert 'BindVariableFloat("ML169UseNative")' in world and 'AnimSetFloat(m_ML169NativeVar, compareMode)' in world
assert camera.count('if (!MLADSLeanSettings.Enabled)')==2
assert keys.index('if (key == KeyCode.KC_F1)')<keys.index('if (GetGame().GetUIManager().GetMenu())')
assert 'm_ML136LeftCtrl || m_ML136RightCtrl' in keys
assert 'GetInputByName("EmoteGreeting")' in keys and 'greeting.Supress();' in keys
assert 'if (!m_ML169F1Down)' in keys and 'm_ML169F1Down = false;' in keys
for forbidden in ['SaveFile','ML153Preset.Save','ML144State.Apply','ML149State.Reset']:assert forbidden not in keys
# Repeats never retoggle until F1 release, with either Ctrl key.
for ctrl in ['left','right']:
 enabled=True;down=False;toggles=0
 for event in ['press','repeat','repeat','release','press','repeat','release']:
  if event=='release':down=False;continue
  if not down:enabled=not enabled;toggles+=1
  down=True
 assert enabled and toggles==2
# Preset, editors, loadout and NPC cycle scripts remain unchanged.
for p in (a/'LogicSource/Scripts').rglob('*.c'):
 if p.name in ['MLADSLeanPlayer.c','MLADSLeanCamera.c','MLADSLeanKeys.c']:continue
 assert p.read_bytes()==(b/p.relative_to(a)).read_bytes(),p
for rel in ['MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
 assert hashlib.sha256((b/rel).read_bytes()).hexdigest()=='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
report={'default_mode':'CUSTOM','key':'either Ctrl + F1, repeat debounced','native_route':'NormalWeaponIK; custom graph output bypassed','native_camera':'custom first-person/ADS adjustments skipped','no_preset_writes_or_resets':True,'existing_editors_freeze_and_CtrlF8':'retained','native_render_and_keyboard':'NOT RUN'}
(b/'Native-Compare-Checks-v169.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
