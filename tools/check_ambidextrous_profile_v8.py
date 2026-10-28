"""Full rigid profile inversion regression; does not emulate native WeaponIK."""
from pathlib import Path
import sys
import numpy as np
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[1]
a=r/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v7'
b=a.with_name('MovementLab_Ambidextrous_Lean_v8')
rng=np.random.default_rng(8);S=np.diag([-1.,1.,1.]);worst=0.;old_failures=0
R=lambda:Rotation.random(random_state=rng).as_matrix()
for _ in range(2000):
 chest,hand,gun,left=R(),R(),R(),R()
 root,hp,gp,lp=[rng.normal(0,.1,3) for i in range(4)]
 targetR=chest@S@chest.T@gun@S
 targetP=root+chest@S@chest.T@(gp-root)
 # Native right hand -> sight rigid profile from the original snapshot.
 profileR=hand.T@gun;profileP=hand.T@(gp-hp)
 anchorR=targetR@gun.T@hand
 anchorP=targetP-anchorR@profileP
 basis=left.T@anchorR;offset=left.T@(anchorP-lp)
 assert np.linalg.det(targetR)>0.999999
 for j in range(3):
  motion=R();shift=rng.normal(0,.1,3)
  liveLeft=motion@left;liveP=motion@lp+shift
  liveAnchor=liveLeft@basis;liveAnchorP=liveP+liveLeft@offset
  outputR=liveAnchor@profileR;outputP=liveAnchorP+liveAnchor@profileP
  err=max(abs(outputR-motion@targetR).max(),abs(outputP-(motion@targetP+shift)).max())
  worst=max(worst,float(err));assert err<1e-12
 # V7 wrist-only origin demonstrably fails this invariant for nonzero offsets.
 if np.linalg.norm(lp+left@(left.T@hand)@profileP-targetP)>1e-4:old_failures+=1
assert old_failures==2000
assert (a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for p in [n,'Profiles/LeanMosin/'+n,'LogicSource/Presets/'+n]:assert(a/p).read_bytes()==(b/p).read_bytes()
for p in ['LogicSource/Inputs.xml','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:
 assert(a/p).read_bytes()==(b/p).read_bytes()
h=(b/'LogicSource/Scripts/4_World/MLAShoulderPose.c').read_text()
tracking=h[h.index(' bool WriteAnchor('):h.index(' void Write(')]
assert 'ReadBoneFrame(actor, "Weapon")'not in tracking
assert 'hand.Orientation.Apply(solution.TriggerOffset)'in tracking
old=(a/'LogicSource/Scripts/4_World/MLAShoulderPose.c').read_text()
start='  ML172Frame root = source.Frames[0];';end='  int triggerIndex = Names.Find("RightHand");'
assert old[old.index(start):old.index(end)]==h[h.index(start):h.index(end)]
print(f'PASS: 6000 full-profile transform cases; max error {worst:.3g}; old wrist-only failure 2000/2000. Visible arm mirror, graph, presets/input/scene unchanged. Native renderer/IK NOT tested.')
