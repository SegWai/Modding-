"""Reduce evaluation recursion by batching independent bone transforms.

Only serial, single-input Model-space transforms with the EXACT same expression
are eligible. Operations on the same bone or ancestor/descendant remain ordered.
Original definitions remain for review; live consumers route to compact nodes.
"""
from pathlib import Path
import collections,json,re,sys,uuid
from dayz_graph_formats import newnodes
sys.setrecursionlimit(10000)
def compile_graph(source,parents):
 nodes={k:v for k,v in newnodes(source).items() if not k.startswith('{')}
 edges={k:[x for x in re.findall(r'\bChild\d* "([^"]+)"',v) if x in nodes] for k,v in nodes.items()}
 incoming=collections.Counter(c for children in edges.values() for c in children)
 depths={};visiting=set()
 def depth(k,graph,cache):
  if k in cache:return cache[k]
  if k in visiting:raise ValueError('Graph cycle: '+k)
  visiting.add(k);cache[k]=1+max((depth(c,graph,cache) for c in graph[k]),default=0);visiting.remove(k);return cache[k]
 for k in nodes:depth(k,edges,depths)
 ancestors={}
 for bone in parents:
  chain=set();p=parents[bone]
  while p:
   assert p not in chain;chain.add(p);p=parents[p]
  ancestors[bone]=chain
 eligible={}
 for name,node in nodes.items():
  if not node.startswith('AnimSrcNodeProcTransform '):continue
  if node.count('AnimSrcNodeProcTrBoneItem')!=1:continue
  expr=re.search(r'\bExpression "([^"]+)"',node);bone=re.search(r'\bBone "([^"]+)"',node);amount=re.search(r'\bAmount ([-+\d.eE]+)\s',node)
  if not expr or not bone or not amount or bone[1] not in parents or 'Space Model' not in node:continue
  child=re.search(r'\bChild "([^"]+)"',node)
  if not child or len(edges[name])!=1:continue
  item=next(v for k,v in newnodes(node).items() if v.startswith('AnimSrcNodeProcTrBoneItem'))
  eligible[name]={'expression':expr[1],'bone':bone[1],'item':item,'child':child[1],'amount':float(amount[1])}
 def related(a,b):return a==b or a in ancestors[b] or b in ancestors[a]
 consumed=set();runs=[]
 for top in sorted(eligible,key=lambda k:depths[k],reverse=True):
  if top in consumed:continue
  chain=[top];cursor=top;expr=eligible[top]['expression']
  while True:
   child=eligible[cursor]['child']
   if child not in eligible or child in consumed or incoming[child]!=1 or eligible[child]['expression']!=expr:break
   chain.append(child);cursor=child
  if len(chain)<2:continue
  operations=list(reversed(chain));pending=list(range(len(operations)));layers=[]
  while pending:
   ready=[]
   for i in pending:
    bone=eligible[operations[i]]['bone']
    if all(not related(eligible[operations[j]]['bone'],bone) for j in pending if j<i):ready.append(i)
   assert ready
   layers.append([operations[i] for i in ready]);pending=[i for i in pending if i not in ready]
  if len(layers)>=len(operations):continue
  consumed.update(chain);runs.append({'top':top,'base':eligible[operations[0]]['child'],'operations':operations,'layers':layers,'expression':expr})
 replacements={run['top']:f'ML164_Compact_{i}_{len(run["layers"])-1}' for i,run in enumerate(runs)}
 additions=[]
 for i,run in enumerate(runs):
  child=replacements.get(run['base'],run['base'])
  for level,layer in enumerate(run['layers']):
   items=[]
   for index,name in enumerate(layer):
    item=eligible[name]['item'];newguid=uuid.uuid5(uuid.NAMESPACE_URL,'ML164/'+str(i)+'/'+str(level)+'/'+str(index)).hex[:16].upper()
    item=re.sub(r'"\{[^}]+\}"','"{'+newguid+'}"',item,count=1);items.append(item)
   name=f'ML164_Compact_{i}_{level}'
   additions.append('    AnimSrcNodeProcTransform '+name+' {\n     Child "'+child+'"\n     Expression "'+run['expression']+'"\n     Bones {\n'+ '\n'.join(items)+'\n     }\n    }\n');child=name
 output=source
 for name,node in nodes.items():
  if name in consumed:continue
  modified=re.sub(r'\b(Child\d*) "([^"]+)"',lambda m:m[1]+' "'+replacements.get(m[2],m[2])+'"',node)
  if modified!=node:
   assert node in output,name;output=output.replace(node,modified,1)
 marker='    AnimSrcNodeQueue MeleeBlockQ {';assert marker in output;output=output.replace(marker,''.join(additions)+marker,1)
 new={k:v for k,v in newnodes(output).items() if not k.startswith('{')};newedges={k:[x for x in re.findall(r'\bChild\d* "([^"]+)"',v) if x in new] for k,v in new.items()};newdepth={}
 before=depths['LocomotionQ'];after=depth('LocomotionQ',newedges,newdepth)
 report={'root_depth_before':before,'root_depth_after':after,'original_operations_batched':sum(len(run['operations']) for run in runs),'compact_nodes':len(additions),'runs':runs,'replacements':replacements,'original_operations':eligible,'native_validation':'NOT RUN; commuting independent-bone transforms retain math, native playback must be verified'}
 return output,report
if __name__=='__main__':
 kit=Path(sys.argv[1]);parents=json.loads((kit/'Native-Head-Travel-v55.json').read_text())['parents'];p=kit/'WorkspaceSource/locomotion.agf';source=p.read_text();output,report=compile_graph(source,parents);p.write_text(output);(kit/'Graph-Compaction-v164.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['runs','replacements','original_operations']},indent=2))
