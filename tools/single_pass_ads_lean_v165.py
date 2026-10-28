"""Avoid duplicate base-pose evaluation inside selected additive correction gates.

Full endpoints remain the same; fractional transitions apply weighted correction
operations directly instead of blending two separately evaluated full poses.
"""
from pathlib import Path
import re,json,sys
from dayz_graph_formats import newnodes
TARGETS=['ML104_LeftElbowDirections','ML118_ContactHoldOnly','ML130_StandingLeftOnly','ML133_StandingLeftElbow']
def optimize(source):
 n=newnodes(source);changes={};records=[]
 for name in TARGETS:
  gate=n[name];scope=re.search(r'BlendWeight "([^"]+)"',gate)[1];base=re.search(r'Child0 "([^"]+)"',gate)[1];child=re.search(r'Child1 "([^"]+)"',gate)[1];chain=[];weighted=[];passthrough=[]
  while child!=base:
   node=n[child];chain.append(child)
   if node.startswith('AnimSrcNodeProcTransform '):
    old_expr=re.search(r'Expression "([^"]+)"',node)[1];new_expr='('+old_expr+')*('+scope+')';newnode=node.replace('Expression "'+old_expr+'"','Expression "'+new_expr+'"',1)
    assert child not in changes;changes[child]=newnode;weighted.append({'node':child,'old_expression':old_expr,'new_expression':new_expr})
   elif node.startswith(('AnimSrcNodeWeaponIk ','AnimSrcNodeIK2 ','AnimSrcNodeIK2Target ')):
    passthrough.append(child)
   else:raise ValueError('Unexpected branch node '+child)
   link=re.search(r'\bChild "([^"]+)"',node);assert link,child;child=link[1]
  assert weighted,name
  changes[name]=gate.replace('BlendWeight "'+scope+'"','BlendWeight "clamp(('+scope+')*1000000.0,0.0,1.0)"',1)
  records.append({'gate':name,'original_scope':scope,'base':base,'branch_nodes':chain,'weighted_transforms':weighted,'unchanged_ik_nodes':passthrough})
 result=source
 for name,newnode in changes.items():assert n[name] in result;result=result.replace(n[name],newnode,1)
 return result,{'gates':records,'changed_nodes':list(changes),'correction_transform_nodes_weighted':sum(len(x['weighted_transforms']) for x in records),'left_stop_duplicated_layers':['ML104_LeftElbowDirections','ML118_ContactHoldOnly','ML130_StandingLeftOnly','ML133_StandingLeftElbow'],'base_replays_through_these_layers_before':16,'base_replays_through_these_layers_after':1,'fractional_interpolation':'weighted correction transforms/IK, not full-pose blend; exact full endpoint operations preserved','native_validation':'NOT RUN'}
if __name__=='__main__':
 kit=Path(sys.argv[1]);path=kit/'WorkspaceSource/locomotion.agf';result,report=optimize(path.read_text());path.write_text(result);(kit/'Single-Pass-Transitions-v165.json').write_text(json.dumps(report,indent=2)+'\n');print('weighted',report['correction_transform_nodes_weighted'],'transform nodes,',len(report['gates']),'gates')
