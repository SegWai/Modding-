from pathlib import Path
import re,collections

def end(s,start):
 q=False;esc=False;depth=0;opened=False
 for i in range(start,len(s)):
  c=s[i]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':q=False
  elif c=='"':q=True
  elif c=='{':depth+=1;opened=True
  elif c=='}' and opened:
   depth-=1
   if not depth:return i+1
 raise ValueError('Unclosed block')
def oldnodes(s):
 out={}
 for m in re.finditer(r'\$Node\s+(\w+)\s*\{',s):
  b=s[m.start():end(s,m.start())];t=re.findall(r'"(?:[^"\\]|\\.)*"|[^\s{}]+',b[b.index('{')+1:]);out[t[0].strip('"')]=(m[1],b,t)
 return out
def newnodes(s):
 out={}
 for m in re.finditer(r'\b(AnimSrcNode\w+)\s+("[^"]+"|[^\s{]+)\s*\{',s):out[m[2].strip('"')]=s[m.start():end(s,m.start())]
 return out
