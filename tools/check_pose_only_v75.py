"""Verify retained pose implementation and absence of head/camera control overrides."""
from pathlib import Path
from dayz_graph_formats import end
root=Path(__file__).resolve().parents[1]
base=root/'hud-icons-test/MovementLabLocomotion_v66'
new=root/'hud-icons-test/MovementLabLocomotion_v75'
a=(base/'StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').read_text()
b=(new/'StartGateSource/Scripts/4_World/MovementLabPoseCorrections.c').read_text()
def method(s,name):
 start=s.rfind('\n',0,s.index(name))+1
 return s[start:end(s,start)]
for name in ['MovementLabCombatOwnsUpperBody','MovementLabUpdateSquareIdle']:
 before=method(a,name).replace('m_MovementLabHead90Active','m_MovementLabSquareIdleActive').replace('v64','v75')
 assert before==method(b,name),name
for token in ['OverrideFreeLook','OverrideAimChange','SetLookLimits','UpdateLRAngle','UpdateUDAngle','HeadingModel','SetOrientation','m_CameraTM','Handoff']:
 assert token not in b,token
assert '0.25, 2.0, blendDt' in b
assert '0.35, 30 * Math.DEG2RAD, blendDt' in b
assert 'm_MovementLabContinuousHeadPose = MovementLabCanUsePoseCorrections(pCurrentCommandID, true)' in b
assert 'm_MovementLabSquareIdleActive = MovementLabCanUsePoseCorrections(pCurrentCommandID)' in b
assert not (new/'StartGateSource/Scripts/4_World/MovementLabHeadLook90.c').exists()
for sub in ['WorkspacePatches','Missions']:
 for f in (base/sub).rglob('*'):
  if f.is_file():assert f.read_bytes()==(new/sub/f.relative_to(base/sub)).read_bytes(),f
for f in (base/'StartGateSource').rglob('*'):
 if f.is_file() and f.name!='MovementLabHeadLook90.c':assert f.read_bytes()==(new/'StartGateSource'/f.relative_to(base/'StartGateSource')).read_bytes(),f
print('PASS: exact shoulder correction/combat guard retained; continuous moving/idle blend retained; v66 graphs and other gameplay untouched; pose module cannot override look/camera/input/root direction. Native playback pending.')
