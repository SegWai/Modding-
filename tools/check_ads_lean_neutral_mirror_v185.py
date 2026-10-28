"""Regression: mirror deformation relative to bone basis, not absolute bone frames."""
from pathlib import Path
import sys,json,re
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];old=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v184';out=old.with_name('MovementLab_ADS_Lean_Mosin_v185');S=np.diag([-1.,1,1]);rng=np.random.default_rng(185)
for name in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [name,'Profiles/LeanMosin/'+name,'LogicSource/Presets/'+name]:assert(old/rel).read_bytes()==(out/rel).read_bytes()
assert(out/'WorkspaceSource/locomotion.agf').read_bytes()==(old/'WorkspaceSource/locomotion.agf').read_bytes()
maxerr=0
for _ in range(1000):
 B=Rotation.random(random_state=rng).as_matrix();D=Rotation.from_rotvec(rng.normal(0,.3,3)).as_matrix();R=D@B
 mirrored=S@(R@B.T)@S@B
 expected=S@D@S@B
 maxerr=max(maxerr,float(abs(mirrored-expected).max()));assert np.allclose(mirrored,expected,atol=1e-12)
 # Identity deformation must leave a rotated bone's own basis UNCHANGED.
 assert np.allclose(S@(B@B.T)@S@B,B,atol=1e-12)
 # Mirror is reversible when the same neutral skeleton is used.
 back=S@(mirrored@B.T)@S@B;assert np.allclose(back,R,atol=1e-12)
# Regression fixture uses the actual stored spine's non-XYZ bone basis.
t=json.loads((old/'Unarmed-Body-Targets-v184.json').read_text());B=np.array(t['targets']['right']['Spine'])[:3,:3];naive=S@B@S
naiveangle=Rotation.from_matrix(naive@B.T).magnitude()*180/np.pi
assert naiveangle>150,naiveangle
fixed=S@(B@B.T)@S@B;assert np.allclose(fixed,B,atol=1e-10)
# Serialized source applies row-wise S D S correctly, with original orientation
# restored afterwards, and cached references cannot be re-read after UI changes.
h=(out/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text()
for line in ['rightBone.Orientation.Times(neutralInverse)','Vector(rowA[0], -rowA[1], -rowA[2])','Vector(-rowB[0], rowB[1], rowB[2])','Vector(-rowC[0], rowC[1], rowC[2])','reflected.Times(neutralBone.Orientation)','desiredRotation.Times(currentInverse)','rotations.Insert(desiredRotation)','if (!NeutralTried && NeutralTime > 0.35)','sampled = LeftReference != null;']:
 assert line in h,line
assert 'ValuesRevision'not in h and 'BodyRevision'not in h
# Simulate first-cycle ordering: left snapshot waits for neutral, neutral once,
# then left solves ONCE from its cached original, regardless of later changes.
left=None;neutral=None;solved=None;captures=[0,0];solves=0
for phase in ['left','centre','right','centre']*50:
 if phase=='left'and left is None:left='native-left';captures[0]+=1
 if phase=='centre'and neutral is None:neutral='native-centre';captures[1]+=1
 if left and neutral and solved is None:solved='mirror';solves+=1
assert captures==[1,1]and solves==1
# New placeholder left literals cannot carry the rejected inverted basis.
literal=(out/'LogicSource/Scripts/4_World/MLUnarmedTargets183.c').read_text();rows=re.findall(r'Add\(result, (.*)\);',literal);assert len(rows)==28
for i in range(14):assert rows[i].split('), Vector(',1)[1]==rows[i+14].split('), Vector(',1)[1]
assert not re.search(r'\w+\[[^\]]+\]\s*(?:\+\+|--)',h)
result={'identity_mirror_preserves_neutral_basis':True,'reversible_orientation_cases':1000,'max_error':maxerr,'old_absolute_mirror_error_degrees':naiveangle,'preset_graph_identity':'passed','one_shot_reference_lifecycle':'passed','native_compile_visual_mesh':'NOT RUN'}
(out/'Neutral-Mirror-Checks-v185.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
