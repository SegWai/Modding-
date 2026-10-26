"""Only increase the proven standing-left elbow seed; preserve all other pose logic."""
from pathlib import Path
import sys,re,json,hashlib,zipfile,math
sys.dont_write_bytecode=True
from dayz_graph_formats import newnodes
from package_ads_lean_runtime import runtime_files
R=Path(__file__).resolve().parents[1];A=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v51';B=R/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v52'
a=newnodes((A/'WorkspaceSource/locomotion.agf').read_text());b=newnodes((B/'WorkspaceSource/locomotion.agf').read_text());assert set(a)==set(b)
changed=[]
for n in a:
 if n.startswith('{'):continue
 if a[n]!=b[n]:changed.append(n)
assert changed==['ML51_StandingRightElbowOut']
assert b[changed[0]]==a[changed[0]].replace('Amount -0.349065850398','Amount -1.047197551197')
amount=float(re.search(r'Amount ([-\d.]+)',b[changed[0]])[1]);assert abs(math.degrees(amount)+60)<1e-8
for p in (A/'LogicSource/Scripts').rglob('*.c'):
 s=(B/p.relative_to(A)).read_text()
 for x,y in [('MLADSLEAN52','MLADSLEAN51'),('MLPOSE52','MLPOSE51'),('MLWALK52','MLWALK51'),('MLCAM52','MLCAM51'),('MLDIST52','MLDIST51'),('lean v52','lean v51'),('Lean v52','Lean v51')]:s=s.replace(x,y)
 assert s==p.read_text(),str(p)
for p,h in json.loads((B/'validation.json').read_text())['pbo_sha256'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
sys.path.insert(0,str(B));from build_pbos import read_pbo
_,packed=read_pbo((B/'@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo').read_bytes());assert packed['MLADSLeanLocomotion_v52.agf']==(B/'WorkspaceSource/locomotion.agf').read_bytes()
with zipfile.ZipFile(R/'artifacts/MovementLab_ADS_Lean_Mosin_v52.zip') as z:
 assert z.testzip() is None;assert set(z.namelist())=={B.name+'/'+p for p in runtime_files(B)}
 assert not any(re.search(r'blender|\.blend|\.png|\.py$',n,re.I) for n in z.namelist())
print('PASS: one elbow amount changed20->60deg only; grip solver, 32cm reach, camera and other modes unchanged; PBO/ZIP verified')
