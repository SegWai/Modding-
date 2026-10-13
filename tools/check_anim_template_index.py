#!/usr/bin/env python3
from pathlib import Path
import re,bisect,sys
root=Path(__file__).resolve().parents[1]
def end(s,start):
 i=s.index('{',start);depth=0;quoted=False
 for j in range(i,len(s)):
  ch=s[j]
  if ch=='"':quoted=not quoted
  if quoted:continue
  if ch=='{':depth+=1
  elif ch=='}':
   depth-=1
   if not depth:return j+1
 raise AssertionError('Unclosed template block')
def check(path):
 s=path.read_text();rootStart=s.index('$animsettemplate');rootEnd=end(s,rootStart);groups=[];declared=int(re.search(r'#ngrouptypes (\d+)',s)[1])
 for m in re.finditer(r'\$groupType(?:\s+"([^"]+)")?\s*\{',s):
  stop=end(s,m.start());assert rootStart<m.start()<stop<rootEnd
  block=s[m.start():stop];names=re.search(r'\$groupnames\s*\{([^}]*)\}',block);labels=re.findall(r'"([^"]+)"',names[1]) if names else []
  slots=re.findall(r'"([^"]+)"',re.search(r'\$anims\s*\{([^}]*)\}',block)[1]);assert labels==sorted(labels) and slots==sorted(slots)
  assert len(labels)==int(re.search(r'#ngroupnames (\d+)',block)[1]);assert len(slots)==int(re.search(r'#nanims (\d+)',block)[1]);groups.append((m[1] or '',labels,slots))
 names=[g[0] for g in groups];assert len(groups)==declared;assert names==sorted(names), 'Template group types are not alphabetically indexed'
 for name,labels,slots in groups:
  assert names[bisect.bisect_left(names,name)]==name
  for label in labels:assert labels[bisect.bisect_left(labels,label)]==label
  for slot in slots:assert slots[bisect.bisect_left(slots,slot)]==slot
 return groups
broken=root/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision30/WorkspacePatches/player_main.ast'
try:check(broken)
except AssertionError as e:assert 'alphabetically' in str(e)
else:raise AssertionError('Regression check missed broken Revision30 template')
fixed=root/'ctrl-mode-test/MovementLabAim_Linked_v2_Revision31/WorkspacePatches/player_main.ast';g=check(fixed);momentum=next(x for x in g if x[0]=='ZZMovementLabCrouchMomentum');assert momentum[1]==['F93','F97'] and momentum[2]==['SprintF','SprintFL','SprintFR']
print('Revision30 rejected; Revision31 template root/count/order/label/slot lookup valid, including all six missing crouch source IDs.')
