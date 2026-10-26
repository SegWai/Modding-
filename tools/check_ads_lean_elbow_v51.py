"""Reuse proven walking elbow chain after standing-left final pose only."""
from pathlib import Path
import sys,re,json,hashlib,zipfile
sys.dont_write_bytecode=True
from dayz_graph_formats import newnodes
from package_ads_lean_runtime import runtime_files
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v50';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v51'
a=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((B/'WorkspaceSource/locomotion.agf').read_text())
for name,node in a.items():
 if name.startswith('{'):continue
 expected=node.replace('Child "ML50_StandingBalancedOnly"','Child "ML51_StandingLeftElbowOnly"') if name=='MeleeBlockQ' else node
 assert b[name]==expected,name
assert {n for n in b.keys()-a.keys() if not n.startswith('{')}=={'ML51_CaptureStandingGrip','ML51_StandingRightElbowOut','ML51_RestoreStandingGrip','ML51_StandingLeftElbowOnly'}
for old,new,child in [('ML37_CaptureRightGrip','ML51_CaptureStandingGrip','ML50_StandingBalancedOnly'),('ML37_RightElbowOut','ML51_StandingRightElbowOut','ML51_CaptureStandingGrip'),('ML37_RestoreRightGrip','ML51_RestoreStandingGrip','ML51_StandingRightElbowOut')]:
 def normalize(s):
  s=re.sub(r'AnimSrcNode\w+ \w+ \{','NODE {',s,count=1);s=re.sub(r'Child "[^"]+"','Child "SOURCE"',s,count=1);s=re.sub(r'"\{[A-F0-9]+\}"','"GUID"',s);return s.replace('Expression "clamp(-MLADSLeanAmount, 0.0, 1.0)"','Expression "1.0"')
 assert normalize(a[old])==normalize(b[new]);assert f'Child "{child}"' in b[new]
assert re.findall(r'Bone "([^"]+)"',b['ML51_StandingRightElbowOut'])==['RightArm']
assert 'Amount -0.349065850398' in b['ML51_StandingRightElbowOut']
expr=re.search(r'BlendWeight "([^"]+)"',b['ML51_StandingLeftElbowOnly'])[1]
for lean in (-1,0,1):
 for gate in (0,1):
  for stance in (0,1,2):
   for move in (0,1):
    for speed in (0,1,2,3):
     w=eval(expr,{'__builtins__':{},'clamp':lambda x,a,b:max(a,min(b,x))},dict(MLADSLeanAmount=lean,MLADSLeanGate=gate,Stance=stance,MLADSLeanMoveBlend=move,MovementSpeed=speed))
     assert w==(1 if (lean,gate,stance,move,speed)==(-1,1,0,0,0) else 0)
assert 'MLADSLeanCanary' not in expr
for p in (A/'LogicSource/Scripts').rglob('*.c'):
 s=(B/p.relative_to(A)).read_text()
 for x,y in [('MLADSLEAN51','MLADSLEAN50'),('MLPOSE51','MLPOSE50'),('MLWALK51','MLWALK50'),('MLCAM51','MLCAM50'),('MLDIST51','MLDIST50'),('lean v51','lean v50'),('Lean v51','Lean v50')]:s=s.replace(x,y)
 assert s==p.read_text(),str(p)
for p,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
sys.path.insert(0,str(B));from build_pbos import read_pbo
_,packed=read_pbo((B/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes());assert packed['MLADSLeanLocomotion_v51.agf']==(B/'WorkspaceSource/locomotion.agf').read_bytes()
with zipfile.ZipFile(R/'artifacts/MovementLab_ADS_Lean_Mosin_v51.zip') as z:
 assert z.testzip() is None;assert set(z.namelist())=={B.name+'/'+p for p in runtime_files(B)}
 assert not any(re.search(r'blender|\.blend|\.png|\.py$',n,re.I) for n in z.namelist())
print('PASS: only standing-left elbow chain added; native capture/restore reused; 32cm, feet, camera and other modes unchanged; resources and essential ZIP verified')
