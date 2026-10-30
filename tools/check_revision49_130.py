from pathlib import Path
import re,sys,json,collections
from dayz_graph_formats import end,oldnodes
r=Path(__file__).resolve().parents[1]/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision49_Compatible130';p=r/'WorkspacePatches'
# Scope nodes at the direct Nodes-block level, excluding states/transitions/IK items.
nodes={};nativecount=0
for f in sorted(p.glob('*.agf'), key=lambda f:f.name=='locomotion.agf'):
 s=f.read_text();assert end(s,0)==len(s.rstrip()),f
 for m in re.finditer(r'\bNodes\s*\{',s):
  limit=end(s,m.start());i=s.index('{',m.start())+1
  while i<limit-1:
   match=re.match(r'\s*(AnimSrcNode\w+)\s+("[^"]+"|[^\s{]+)\s*\{',s[i:])
   if not match:
    assert not s[i:limit-1].strip(),s[i:i+100];break
   start=i+match.start()+len(match[0])-1;stop=end(s,start);name=match[2].strip('"');b=s[i:stop]
   # Native 1.30 has some node names shared across separate graph files.
   nodes[name]=(match[1],b);i=stop
print('all graph nodes:',len(nodes))
legacy=oldnodes((r.parent/'MovementLabAim_Linked_v2_Revision49/WorkspacePatches/locomotion.agr').read_text())
assert set(legacy)-set(nodes)=={'LocomotionQBufferSave','LocomotionQBufferUse'} # Native 1.30 removes these old buffers.
for n,(typ,b) in nodes.items():
 for child in re.findall(r'\b(?:Child|Child0|Child1)\s+"([^"\n]+)"',b):assert re.sub(r'^\{[^}]+\}', '', child) in nodes,(n,child)
 for m in re.finditer(r'\bChildren\s*\{([^}]+)',b):
  for child in re.findall(r'"([^"]+)"',m[1]):assert re.sub(r'^\{[^}]+\}', '', child) in nodes,(n,child)
# Cycles use real node-child edges, not animation names, expression strings or transition state names.
edges={n:re.findall(r'\b(?:Child|Child0|Child1)\s+"([^"\n]+)"',b)+[c for m in re.finditer(r'\bChildren\s*\{([^}]+)',b) for c in re.findall(r'"([^"]+)"',m[1])] for n,(_,b) in nodes.items()}
seen=set();active=set()
def visit(n):
 assert n not in active,('cycle',n)
 if n in seen:return
 active.add(n)
 for c in edges[n]:visit(re.sub(r'^\{[^}]+\}', '', c))
 active.remove(n);seen.add(n)
for n in nodes:visit(n)
# Native declarations plus custom variables cover all custom expression identifiers.
main=(p/'player_main.agr').read_text();decl=set(re.findall(r'AnimSrcGCTVar\w+\s+(\w+)',main))
used=set()
for f in p.glob('*.agf'):used.update(re.findall(r'\bMovementLab\w+',f.read_text()))
# Sheet name is not a runtime variable.
used.discard('MovementLabCustom')
used -= set(nodes)
assert used<=decl,used-decl
# Every custom instance key is declared by its custom animation group.
ast=(p/'player_main.ast').read_text();groups={}
for m in re.finditer(r'AnimSetTemplateSource_AnimationGroup\s+"[^"]+"\s*\{',ast):
 b=ast[m.start():end(ast,m.end()-1)];match=re.search(r'\bName\s+"([^"]+)"',b)
 if not match:continue
 name=match[1]
 a=re.search(r'Animations\s*\{([^}]+)',b);c=re.search(r'Columns\s*\{([^}]+)',b)
 groups[name]=(set(re.findall(r'"([^"]+)"',a[1])),set(re.findall(r'"([^"]+)"',c[1])) if c else set())
customkeys=0
for f in p.rglob('*.asi'):
 s=f.read_text();assert s.startswith('AnimSetInstanceSource'),f
 assert end(s,0)==len(s.rstrip()),f
 keys=re.findall(r'AnimSetInstanceSource_Line\s+"([^"]+)"',s)
 assert len(keys)==len(set(keys)),('duplicate line',f)
 for key in keys:
  if key.startswith('ZZMovementLab'):
   group,column,anim=key.split('.');assert group in groups and column in groups[group][1] and anim in groups[group][0],(f,key)
   customkeys+=1
for f in (r.parent/'MovementLabAim_Linked_v2_Revision49'/'StartGateSource').rglob('*'):
 if f.is_file():assert f.read_bytes()==(r/'StartGateSource'/f.relative_to(r.parent/'MovementLabAim_Linked_v2_Revision49'/'StartGateSource')).read_bytes()
assert (r/'@MovementLabStartGate/Addons/MovementLabStartGate.pbo').read_bytes()==(r.parent/'MovementLabAim_Linked_v2_Revision49/@MovementLabStartGate/Addons/MovementLabStartGate.pbo').read_bytes()
print('PASS:modern schema/reference/DAG/custom controls/groups/mappings;all original49 logic+PBO byteexact. Native game/PowerShell NOT RUN.')
# Current native base mappings stay exact: no legacy medical/item action rollback.
def mappings(path):
 s=path.read_text();result={}
 for m in re.finditer(r'AnimSetInstanceSource_Line\s+"([^"]+)"\s*\{',s):
  b=s[m.start():end(s,m.start())];v=re.search(r'Resource "([^"]+)"',b)
  if v:result[m[1]]=v[1]
 return result
base=Path('/workspace/output/ADS_Lean_Game_Test/source-workspace/player_main')
native=mappings(base/'player_main.asi');actual=mappings(p/'player_main.asi')
assert all(actual[k]==v for k,v in native.items())
assert all(k in native or k.startswith('ZZMovementLab')for k in actual)
plan=json.loads((r/'Armed-Speed-Plan.json').read_text())
for instance in plan['instances']:
 rows=mappings(p/instance['file'])
 for key,value in {**instance['replace'],**instance['add']}.items():assert rows[key]==value,(instance['file'],key)
prep=(r/'Prepare-Crouch-Clips.ps1').read_text()
assert '.IndexOf(\'$animations\')'not in prep
assert 'Get-ChildItem -LiteralPath $movementlabPatchRoot -Recurse -File'in prep
assert "Join-Path $movementlabProjectRoot ($movementlabArmedVariant.source.Replace('/','\\'))"in prep
assert 'MovementLabRevision49.agf'in (p/'player_main.agr').read_text()
assert(p/'MovementLabRevision49.agf').read_bytes()==(p/'locomotion.agf').read_bytes()
print('PASS:modern native actions unchanged;all armed instance plan mappings exact;no legacy runtime patcher;private graph;auto data root retained.')
