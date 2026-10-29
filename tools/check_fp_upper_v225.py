"""Guard against full crouch skeleton leaking into standing first-person lean."""
from pathlib import Path
import re,json
from dayz_graph_formats import newnodes,end
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v224';b=a.with_name('MovementLab_ADS_Lean_Mosin_v225');original=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v222'
ns=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());old=newnodes((original/'WorkspaceSource/locomotion.agf').read_text());native=newnodes(Path('/workspace/output/ADS_Lean_Game_Test/source-workspace/player_main/locomotion.agf').read_text());info=json.loads((b/'First-Person-Upper-Only-v225.json').read_text())
assert {k for k in old if old[k]!=ns[k]}=={'MeleeBlockQ'}
assert old['MeleeBlockQ'].replace('Child "ML183_UnarmedOnly"','Child "ML223FirstPersonOnly"')==ns['MeleeBlockQ']
normalize=lambda s:re.sub(r'\{[A-F0-9]{16}\}','{GUID}',s)
mapping={n:'ML225Native_'+n for n in info['native_clones']};mapping['StanceMaster']='ML225ActualStance'
for n in info['native_clones']:
 expected=native[n]
 if n in info['modified_standing_lean_nodes']:
  cro=n.replace('Erc','Cro');items=[]
  for m in re.finditer(r'AnimSrcNodeProcTrBoneItem\s+"[^"]+"\s*\{',native[cro]):
   item=native[cro][m.start():end(native[cro],m.start())];bone=re.search(r'Bone "([^"]+)"',item)[1]
   if bone in {'Spine','Spine1','Spine2','Spine3'}:items.append(item)
  expr=re.search(r'Expression "([^"]+)"',native[cro])[1]
  expected=re.sub(r'Expression "[^"]+"','Expression "'+expr+'"',expected,count=1)
  i=expected.index('Bones {');j=end(expected,i);expected=expected[:i]+'Bones {\n'+'\n'.join(items)+'\n}'+expected[j:]
  bones=set(re.findall(r'Bone "([^"]+)"',ns[mapping[n]]));assert bones<={'Spine','Spine1','Spine2','Spine3'} and bones
 prefix=expected.split('{',1)[0];expected=expected.replace(prefix,prefix.replace(n,mapping[n],1),1)
 expected=re.sub(r'\b(Child[0-9]*) "([^"]+)"',lambda m:m[1]+' "'+mapping.get(m[2],m[2])+'"',expected)
 assert normalize(expected)==normalize(ns[mapping[n]]),n
# Real Stance0 selects standing, not crouched base sources; movement selector
# retains standing idle/move for all three actual speeds rather than forcing crouch.
assert 'BlendWeight "clamp(Stance,0.0,1.0)"'in ns['ML225ActualStance']
assert 'Child0 "ML225ErcRaised"'in ns['ML225ActualStance'] and 'Child1 "ML225CroRaised"'in ns['ML225ActualStance']
for hands in ['Ras','Low']:
 branch=ns['ML225Erc'+hands]
 assert 'BlendWeight "clamp(MovementSpeed*1000000.0,0.0,1.0)"'in branch
 assert 'Child0 "ML225Native_LeanIdleErc'+hands+'Right"'in branch
 assert 'Child1 "ML225Native_LeanMoveErc'+hands+'Right"'in branch
# Ensure standing left operators start from standing sources and right operators
# inherit the corresponding standing left operator.
for mode in ['Idle','Move']:
 for hands in ['Ras','Low']:
  left=ns['ML225Native_Lean'+mode+'Erc'+hands+'Left']
  assert 'Cro' not in left.split('Bones {')[0]
  assert 'Child "ML225Native_Lean'+mode+'Erc'+hands+'Left"'in ns['ML225Native_Lean'+mode+'Erc'+hands+'Right']
for p in(a/'LogicSource/Presets').glob('*.json'):
 for rel in [p.name,'LogicSource/Presets/'+p.name,'Profiles/LeanMosin/'+p.name]:assert(a/rel).read_bytes()==(b/rel).read_bytes(),rel
for p in(a/'LogicSource/Scripts').rglob('*.c'):
 assert p.read_text().replace('v224','v225')==(b/p.relative_to(a)).read_text(),p.name
# Every FP internal reference resolves; no cycles or custom-stage dependency.
seen=set();pending=set()
def walk(k):
 assert k not in pending,k
 if k in seen:return
 pending.add(k)
 for c in re.findall(r'\bChild[0-9]* "([^"]+)"',ns[k]):
  if c not in ns:
   assert c in {'DamageMaster','WeaponStanceMaster'};continue
  assert c.startswith('ML225'),(k,c);walk(c)
 pending.remove(k);seen.add(k)
walk('ML225Native_NormalWeaponIK')
print('PASS:standing native source+actual stance selector;8 lean operators borrow ONLY crouch spine transforms;other native clones exact;custom TP path/15presets/client routing unchanged;FP DAG valid. Native height/grip/FP-TP/FPS/MP NOT RUN.')
