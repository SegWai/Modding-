"""Offline graph/UI/lean-rate checks. Native Enforce/UI/feet/grip not executed."""
from pathlib import Path
import re,json,math,sys
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];KIT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v149';BASE=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v148'
spec=json.loads((KIT/'Body-Editor-v149.json').read_text());assert len(spec['parts'])==24 and len(spec['controls'])==145
agr=(KIT/'WorkspaceSource/player_main.agr').read_text();graph=(KIT/'WorkspaceSource/locomotion.agf').read_text();nodes=newnodes(graph);old=newnodes((BASE/'WorkspaceSource/locomotion.agf').read_text())
for name,node in old.items():
 if not name.startswith('{') and name!='MeleeBlockQ':assert nodes[name]==node,name
for control in spec['controls']:
 assert agr.count('AnimSrcGCTVarFloat '+control+' {')==1
 assert re.search(r'AnimSrcGCTVarFloat '+control+r' \{\s*DefaultValue 0',agr)
for bone,_ in spec['parts']:
 for kind,op in [('T','Translate'),('R','Rotate')]:
  for axis in 'XYZ':
   node=nodes['ML149_Body_'+bone+'_'+kind+axis]
   assert 'Expression "ML149'+bone+kind+axis+'"' in node
   assert 'Bone "'+bone+'"' in node and 'Op '+op in node
chain=re.search(r'Child0 "([^"]+)"',nodes['ML149_BodyWithWeapon'])[1];seen=[]
while chain!='ML147_LeftEditorOnly':
 seen.append(chain);chain=re.search(r'Child "([^"]+)"',nodes[chain])[1];assert len(seen)<=144
assert len(seen)==144
assert 'BlendWeight "ML149WeaponFollow"' in nodes['ML149_BodyWithWeapon']
body=(KIT/'LogicSource/Scripts/4_World/MLBodyEditor149.c').read_text();menu=(KIT/'LogicSource/Scripts/5_Mission/MLBodyMenu149.c').read_text();world=(KIT/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();keys=(KIT/'LogicSource/Scripts/5_Mission/MLADSLeanKeys.c').read_text();layout=(KIT/'LogicSource/GUI/MLBodyEditor149.layout').read_text()
for bone,label in spec['parts']:assert 'Bones.Insert("'+bone+'");' in body and 'Labels.Insert("'+label+'");' in body
assert 'MLBodyEditor_Left.json' in body and 'MLBodyEditor_Right.json' in body
for name in ['Previous','Next','ResetPart','ResetSide','Save','Load','Close','LeftSide','RightSide','Part']:
 assert len(re.findall(r'\b'+name+r' \{',layout))==1,name
for i in range(6):
 for prefix in ['Value','Readout','Minus','Plus']:assert len(re.findall(r'\b'+prefix+str(i)+r' \{',layout))==1
assert 'XComboBoxWidgetClass Part {' in layout and 'm_Part.AddItem(label)' in menu and 'm_Part.GetCurrentItem()' in menu
assert 'return new ML149Menu;' in keys and 'EnterScriptedMenu(86149, null)' in keys
assert 'AddActiveInputExcludes' in menu and 'RemoveActiveInputExcludes' in menu and 'super.OnShow();' in menu and 'super.OnHide();' in menu
assert world.index('super.CommandHandler(')<world.index('  ML149UpdateBody(state);')
assert 'float nativeLeanStep = 4.5 * Math.Clamp(pDt, 0, 0.25);' in world
assert 'm_ML149ArmFade' in world and 'upperAngles[axis] * m_ML149ArmFade' in world
# Abrupt full reversals follow native speed without overshoot, at multiple FPS.
results=[]
for hz in [30,60,144]:
 dt=1/hz
 for start,target in [(-1,1),(1,-1),(0,1),(0,-1)]:
  value=start;elapsed=0.;maxspeed=0
  while abs(value-target)>1e-9:
   before=value;step=4.5*dt;value+=max(-step,min(step,target-value));elapsed+=dt
   maxspeed=max(maxspeed,abs(value-before)/dt)
   assert min(start,target)-1e-9<=value<=max(start,target)+1e-9
  expected=abs(target-start)/4.5;assert abs(elapsed-expected)<=dt+1e-9 and maxspeed<=4.5+1e-9
  results.append({'fps':hz,'from':start,'to':target,'seconds':round(elapsed,6)})
 # Already-native-interpolated samples gain no additional lag.
 value=0.
 for i in range(hz):
  target=min(1,(i+1)*dt*4.5);step=4.5*dt;value+=max(-step,min(step,target-value));assert abs(value-target)<1e-9
for p in (KIT/'LogicSource').rglob('*.c'):
 s=p.read_text();assert s.count('{')==s.count('}'),p
 for m in re.finditer(r'(?:array<float>|TStringArray) \w+ = \{([^\n]+)\}',s):assert m[1].count(',')<8,p
assert (KIT/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes()==(BASE/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_bytes()
print(json.dumps({'parts':24,'new_zero_default_controls':145,'graph':'144body transforms follow approved poses, weapon follow conditional; original pose nodes unchanged','ui':'F7 open/close+Esc,24part dropdown,6sliders,left/right save/load/reset,balanced input focus; F6 retained','lean_transitions':results,'native_compile_playback_UI_foot_plant_grip':'NOT RUN; numeric4.5rate matches official1.30 source, not native visual verification'},indent=2))
