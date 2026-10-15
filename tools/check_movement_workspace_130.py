from pathlib import Path
import re,sys,json,collections
from dayz_graph_formats import end,oldnodes
r=Path(__file__).resolve().parents[1]/'hud-icons-test/MovementLabLocomotion_v66';p=r/'WorkspacePatches'
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
legacy=oldnodes((r.parent/'MovementLabLocomotion_v65/WorkspacePatches/locomotion.agr').read_text())
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
assert (r/'StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_bytes()==(r.parent/'MovementLabLocomotion_v65/StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_bytes()
print('PASS: all custom nodes preserved, no missing graph children/cycles, custom variables declared,',customkeys,'custom clip mappings declared, handoff/camera script unchanged')
