"""Validate native-profile coordinate bridge, no arm-output feedback or probe."""
from pathlib import Path
import sys,re,json
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v5';b=a.with_name('MovementLab_Ambidextrous_Lean_v7');w=b/'LogicSource/Scripts/4_World'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());named={n for n in set(new)-set(old)if not n.startswith('{')};assert named=={'MLASwapAnchor'+str(i)for i in range(6)}
for n,v in old.items():
 if n.startswith('{'):continue
 expected=v.replace('Child "ML166_FinalHorizontalAim"','Child "MLASwapAnchor5"').replace('hand = LeftHand"','hand = Weapon"').replace('weaponrotator = LeftHand"','weaponrotator = Weapon"')if n=='MLASwapLeftWeapon'else v
 assert new[n]==expected,n
for n in named:assert 'Bone "Weapon"'in new[n] and 'Space Model'in new[n]
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'Profiles/LeanMosin/'+n,'LogicSource/Presets/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['Missions/MLADSLeanMosin.ChernarusPlus/init.c','LogicSource/Inputs.xml']:assert(a/rel).read_bytes()==(b/rel).read_bytes()
# Verify published skeleton evidence rather than inventing a new bone/API.
skeleton=json.loads((r/'docs/native-skeleton-comparison.json').read_text());assert ['weapon','pelvis']in skeleton['models'][0]['bones']
# Hand-profile frame conversion: a LEFT anatomical hand must carry RIGHT native
# grip axes without rotating the visible left wrist/hand/fingers themselves.
rng=np.random.default_rng(7);maxerr=0
for _ in range(1000):
 R=lambda:Rotation.random(random_state=rng).as_matrix()
 right,left,weapon=R(),R(),R();motion=R();basis=left.T@right;left_current=motion@left
 anchor=left_current@basis;profile=right.T@weapon;output=anchor@profile
 maxerr=max(maxerr,float(abs(output-motion@weapon).max()));assert np.allclose(output,motion@weapon,atol=1e-12)
 # Native animation helper reconstruction uses unaffected parent, never its
 # own last corrected world frame; moving pelvis cannot accumulate an offset.
 pelvisR,pelvisP=R(),rng.normal(0,.1,3);nativeR,nativeP=R(),rng.normal(0,.1,3)
 localR=pelvisR.T@nativeR;localP=pelvisR.T@(nativeP-pelvisP)
 for _ in range(5):
  currentR,currentP=R(),rng.normal(0,.1,3);handP=rng.normal(0,.1,3)
  baselineR=currentR@localR;baselineP=currentP+currentR@localP
  correction=anchor@baselineR.T;translation=handP-baselineP
  assert np.allclose(correction@baselineR,anchor,atol=1e-12)
  assert np.allclose(baselineP+translation,handP,atol=1e-12)
# New tracking operates on the helper ONLY. It cannot change any measured arm
# or pelvis frame, and cannot form a corrected-arm feedback loop.
h=(w/'MLAShoulderPose.c').read_text();start=h.index(' bool WriteAnchor(');end=h.index(' void Write(',start);tracking=h[start:end]
assert 'ReadBoneFrame(actor, "LeftHand")'in tracking and 'ReadBoneFrame(actor, "Pelvis")'in tracking
assert 'ReadBoneFrame(actor, "Weapon")'not in tracking
assert 'solution.TriggerBasis = leftGripInverse.Times(sourceTrigger.Orientation)'in h
assert 'pelvis.Orientation.Times(solution.AnchorPelvisBasis)'in tracking
assert 'hand.Orientation.Times(solution.TriggerBasis)'in tracking
assert 'AlignmentStage'not in h and 'MLASwapGripRoll'not in h
assert 'ML144Math.Limb('not in h
assert not re.search(r'\w+\[[^\]]+\]\s*(?:\+\+|--)',h)
agr=(b/'WorkspaceSource/player_main.agr').read_text();ids=re.findall(r'AnimSrcGCTVar\w+ (\w+)\s*\{',agr);assert len(ids)==len(set(ids));assert len([n for n in ids if n.startswith('MLASwap')])==307
sys.setrecursionlimit(20000);done=set();visiting=set()
def visit(n):
 if n not in new or n in done:return
 assert n not in visiting,n
 visiting.add(n)
 for c in re.findall(r'\bChild\d* "([^"]+)"',new[n]):visit(c)
 visiting.remove(n);done.add(n)
for n in new:
 if not n.startswith('{'):visit(n)
print('PASS:1000 grip-basis cases +5000 parent-relative anchor cases; maxerror',maxerr,';6 helper-only nodes/6vars, no arm feedback, graph/DAG/presets/input/scene. Native Weapon-helper IK/load/placement NOT RUN.')
