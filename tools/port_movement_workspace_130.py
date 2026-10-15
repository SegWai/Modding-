from pathlib import Path
import sys,re,json,shutil,hashlib,zipfile
from dayz_graph_formats import end,oldnodes,newnodes
import argparse
parser=argparse.ArgumentParser(description='Port MovementLab v65 animation changes into native DayZ 1.30 source schemas.')
parser.add_argument('--old-workspace',type=Path,required=True)
parser.add_argument('--new-workspace',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1];src=root/'hud-icons-test/MovementLabLocomotion_v65';dst=root/'hud-icons-test/MovementLabLocomotion_v66';base=args.new_workspace;oldbase=args.old_workspace
shutil.copytree(src,dst,dirs_exist_ok=True)
patch=dst/'WorkspacePatches';shutil.rmtree(patch);shutil.copytree(base,patch)
# Obsolete legacy fragments must not shadow the new .agf graph files.
for p in patch.glob('*.agr'):
 if p.name!='player_main.agr':p.unlink()
legacy=(src/'WorkspacePatches/locomotion.agr').read_text();old=oldnodes((oldbase/'locomotion.agr').read_text());custom=oldnodes(legacy);modern=(base/'locomotion.agf').read_text();native=newnodes(modern)
def quoted(b):return re.findall(r'"((?:[^"\\]|\\.)*)"',b)
def q(x):
 lines=x.split('\n');return '\\\n     '.join('"'+v+'"' for v in lines)
def header(b):return re.findall(r'"(?:[^"\\]|\\.)*"|[^\s{}]+',b[b.index('{')+1:b.index('$',b.index('{')+1) if '$' in b[b.index('{')+1:] else b.rindex('}')])
def val(t):return t[1:-1] if t.startswith('"') else t

def convert(n,v):
 typ,b,_=v;t=[val(x) for x in header(b)];assert t[0]==n
 props=[];kind=typ.replace('AnimNode','AnimSrcNode',1)
 def put(k,x):props.append(k+' '+q(x))
 def flag(k,x):props.append(k+' '+str(x))
 if typ in ['AnimNodeSourceSync','AnimNodeSource']:
  put('Source',t[2]);put('Looptype',{'loop':'Loop','noloop':'No Loop'}[t[3]])
  if typ.endswith('Sync'):put('SyncLine',t[4])
 elif typ=='AnimNodeGroupSelect':
  for k,x in zip(['Child','Group','Column'],t[2:5]):put(k,x)
 elif typ in ['AnimNodeBlend','AnimNodeBlendT','AnimNodeBlendTAdd']:
  if typ=='AnimNodeBlend':
   for k,x in zip(['BlendWeight','Child0','Child1'],t[2:5]):put(k,x)
   bits=int(t[5])
  else:
   for k,x in zip(['Child0','Child1','TriggerOn','TriggerOff','Condition','BlendTime','BlendFn'],t[2:9]):put(k,x)
   bits=int(t[9])
  if typ=='AnimNodeBlendTAdd':flag('AdditiveAlways',bits)
  else:
   flag('OptimizeMin',bits&1);flag('OptimizeMax',(bits>>1)&1)
   if typ=='AnimNodeBlendT':flag('SelectMainPath',(bits>>2)&1)
 elif typ=='AnimNodeBlendN':
  put('BlendWeight',t[2]);put('BlendFn',t[4]);flag('IsCyclic',t[3])
  a=b.index('$Inputs');z=end(b,a);pairs=re.findall(r'([-+\d.eE]+)\s+"([^"]+)"',b[a:z]);assert pairs
  props+=['Thresholds {\n      '+' '.join(x for x,y in pairs)+'\n     }','Children {\n      '+' '.join(q(y) for x,y in pairs)+'\n     }']
 elif typ=='AnimNodePose2':
  for k,x in zip(['Source','ValueY','ValueX','Table'],t[2:6]):put(k,x)
 elif typ=='AnimNodeRot':
  kind='AnimSrcNodeProcTransform';put('Child',t[2]);put('Expression',t[3]);items=[]
  for i,(bone,mode,amt) in enumerate(re.findall(r'\$ri\s*\{\s*"([^"]+)"\s+"([^"]+)"\s+([-\d.]+)',b)):
   items.append('AnimSrcNodeProcTrBoneItem "{'+hashlib.sha256((n+str(i)).encode()).hexdigest()[:16].upper()+'}" {\n       Bone '+q(bone)+'\n       Axis '+mode[0].upper()+'\n       Space '+('Model' if mode[1]=='m' else 'Local')+'\n       Op '+('Rotate' if mode[2]=='r' else 'Translate')+'\n       Amount '+amt+'\n      }')
  assert items;props+=['Bones {\n      '+'\n      '.join(items)+'\n     }']
 else:
  # Preserve native 1.30 IK bindings, state-machine structure and graph flags.
  basen=n
  for suffix in ['MLStandingWheel','MLWheel']:
   if basen.endswith(suffix):basen=basen[:-len(suffix)]
  assert basen in old and basen in native,(n,typ)
  result=native[basen];original=old[basen][1]
  a=quoted(original);c=quoted(b);assert len(a)==len(c),(n,len(a),len(c))
  replacements={}
  for x,y in zip(a,c):
   if ' '.join(x.split()) != ' '.join(y.split()):
    assert x not in replacements or replacements[x]==y,(n,x)
    replacements[x]=y
  # State-machine transition duration changes can use the same quoted value
  # repeatedly; all uses in each modified machine have the same target.
  for x,y in sorted(replacements.items(),key=lambda z:-len(z[0])):
   if x==basen:
    result=re.sub(r'^(\w+)\s+(?:"'+re.escape(basen)+'"|'+re.escape(basen)+r')(?=\s*\{)',lambda m:m[1]+' '+q(y),result,count=1)
   elif '\n' not in x:
    result=result.replace(q(x),q(y))
   else:raise AssertionError(('unhandled multiline change',n,x))
  # Every changed graph child must have migrated into the modern structure.
  for x,y in replacements.items():
   if y in custom:assert q(y) in result or re.match(r'\w+\s+"?'+re.escape(y),result),(n,y)
  return result
 return kind+' '+q(n)+' {\n     '+'\n     '.join(props)+'\n    }'

# Keep native 1.30 sheets and untouched nodes byte-for-byte. Replace altered
# nodes and append new custom nodes in a separate sheet.
changes=[];add=[];converted=[]
for n,v in custom.items():
 if n in old and v[1]==old[n][1]:continue
 new=convert(n,v);converted.append(n)
 if n in native:changes.append((native[n],new))
 else:add.append(new)
for a,b in changes:
 assert modern.count(a)==1;modern=modern.replace(a,b)
# Renamed legacy nodes remain in native too, but custom names are new references;
# they must not create duplicate active output names. Original names have wrapper
# replacements where required, so retaining unused original nodes is safe.
at=modern.rfind('}');sheetend=modern.rfind('}',0,at)
modern=modern[:sheetend]+'\n  AnimSrcGraphSheet MovementLabCustom {\n   Nodes {\n    '+'\n    '.join(add)+'\n   }\n  }\n'+modern[sheetend:]
(patch/'locomotion.agf').write_text(modern)

# Add custom variables to the native 1.30 control template, retaining native IK chains/commands.
main=(base/'player_main.agr').read_text();custommain=(src/'WorkspacePatches/player_main.agr').read_text();varrows=[]
for name,typ,rest in re.findall(r'#Var\s+(MovementLab\w+)\s+(\w+)\s+([^\n]+)',custommain):
 fields=rest.split();assert typ=='float'
 varrows.append('AnimSrcGCTVarFloat '+name+' {\n    DefaultValue '+fields[0]+'\n    MinValue '+fields[1]+'\n    MaxValue '+fields[2]+'\n   }')
assert len(varrows)==len(set(re.findall(r'#Var\s+(MovementLab\w+)',custommain)))
main=main.replace('Variables {','Variables {\n   '+'\n   '.join(varrows),1)
(patch/'player_main.agr').write_text(main)

# Append custom animation groups to the native 1.30 template.
ast=(base/'player_main.ast').read_text();oldast=(src/'WorkspacePatches/player_main.ast').read_text();groups=[]
for m in re.finditer(r'\$groupType\s+"(ZZMovementLab[^"]+)"\s*\{',oldast):
 b=oldast[m.start():end(oldast,m.start())]
 anims=quoted(re.search(r'\$anims\s*\{([^}]+)',b)[1]);cols=quoted(re.search(r'\$groupnames\s*\{([^}]+)',b)[1])
 groups.append('AnimSetTemplateSource_AnimationGroup "{'+hashlib.sha256(m[1].encode()).hexdigest()[:16].upper()+'}" {\n   Name '+q(m[1])+'\n   Animations {\n    '+'\n    '.join(q(x) for x in anims)+'\n   }\n   Columns {\n    '+'\n    '.join(q(x) for x in cols)+'\n   }\n  }')
groupend=end(ast,ast.index('Groups {'))-1;ast=ast[:groupend]+'\n  '+'\n  '.join(groups)+'\n '+ast[groupend:];(patch/'player_main.ast').write_text(ast)

# Port the base instance overrides, plus all per-weapon profile mappings, into
# the 1.30 Lines schema without discarding newly added native mappings.
def oldmaps(p):
 s=p.read_text();return dict(re.findall(r'"([^"\n]+)"\s+"([^"\n]+)"',s.split('$animations',1)[1]))
vanillamaps=oldmaps(oldbase/'player_main.asi');custommaps=oldmaps(src/'WorkspacePatches/player_main.asi')
baseoverrides={k:v for k,v in custommaps.items() if vanillamaps.get(k)!=v}
plan=json.loads((src/'Armed-Speed-Plan.json').read_text());inst={v['file'].replace('\\','/'):v for v in plan['instances']}
for path in patch.rglob('*.asi'):
 rel=path.relative_to(patch).as_posix();s=path.read_text();assert s.startswith('AnimSetInstanceSource'),rel
 overrides=dict(baseoverrides) if rel=='player_main.asi' else {}
 if rel in inst:overrides.update(inst[rel]['replace']);overrides.update(inst[rel]['add'])
 if not overrides:continue
 for k,v in overrides.items():
  pat=r'AnimSetInstanceSource_Line\s+"'+re.escape(k)+r'"\s*\{'
  block='AnimSetInstanceSource_Line '+q(k)+' {\n   Resource '+q(v)+'\n  }'
  match=re.search(pat,s)
  if match:s=s[:match.start()]+block+s[end(s,match.start()):]
  else:
   at=s.index('{',s.index('Lines'))+1;s=s[:at]+'\n  '+block+s[at:]
 path.write_text(s)

# Launcher: patches include nested modern instances; no legacy $animations editing.
f=dst/'Prepare-Crouch-Clips.ps1';s=f.read_text();a=s.index('foreach ($movementlabPatch in Get-ChildItem');b=s.index("$movementlabFiles['config.cpp']",a)
s=s[:a]+'''$movementlabPatchRoot = Join-Path $PSScriptRoot 'WorkspacePatches'
foreach ($movementlabPatch in Get-ChildItem -LiteralPath $movementlabPatchRoot -Recurse -File) {
    $movementlabPatchName = $movementlabPatch.FullName.Substring($movementlabPatchRoot.Length + 1)
    $movementlabFiles[$movementlabPatchName] = [System.IO.File]::ReadAllBytes($movementlabPatch.FullName)
}
# All native 1.30 instance mappings and custom speed variants are pre-merged.
# Do not apply the old 1.29 $animations text patcher to AnimSetInstanceSource.

'''+s[b:];f.write_text(s)
(dst/'README-v66.txt').write_text('''MovementLab v66 - DayZ 1.30 animation workspace migration

Uses the freshly extracted 1.30 workspace supplied by the user. Native player_main.agr, .ast and .asi files now use the 1.30 source schemas. Custom locomotion nodes have been ported to locomotion.agf, which the native 1.30 main graph references. Custom variables, speed groups and per-weapon clip mappings are merged into the new schemas, preserving new native content and IK bindings. The launcher copies nested workspace files and no longer runs the legacy .asi text patcher.

Preserved from v65: movement look-direction handoff, stationary head-only look and camera stops, idle shoulder correction, combat safeguards, locomotion speed/momentum logic, six stance icons and MMG/SNAFU loadout. No preview UI is added.

Extract into a fresh folder and launch Launch-Movement-Test.cmd. Current game animation clips must be extracted under D:\\DayZProjects. Static migration/dependency/schema and PBO/ZIP checks passed; native DayZ compilation, graph loading and playback require local testing.
''')
(dst/'Migration-1.30.json').write_text(json.dumps({'source':'User-supplied freshly extracted player_main.7z','custom_nodes_ported':len(converted),'custom_variables':len(varrows),'custom_groups':len(groups),'runtime_test':'pending'},indent=2))
print('PORT',len(converted),'nodes',len(varrows),'variables',len(groups),'groups')
