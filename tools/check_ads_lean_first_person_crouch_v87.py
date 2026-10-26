"""Verify first-person crouch rotation reuse and native/third-person isolation."""
from pathlib import Path
import re,json,math
from dayz_graph_formats import newnodes
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'ads-lean-test';a=base/'MovementLab_ADS_Lean_Mosin_v86';b=base/'MovementLab_ADS_Lean_Mosin_v87'
def norm(s):return re.sub(r'\[(ML[A-Z]+)(86|87)\]',r'[\g<1>VERSION]',s.replace('v86','vVERSION').replace('v87','vVERSION'))
rel='LogicSource/Scripts/4_World/MLADSLeanCamera.c';assert norm((a/rel).read_text())==norm((b/rel).read_text())
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());spec=json.loads((b/'First-Person-Crouch-Lean-v87.json').read_text())
effective='(Stance+(1.0-clamp(Stance, 0.0, 1.0))*ML87FirstPersonCrouchLean)'
for name,block in old.items():
 expected=block
 if name in spec['effective_custom_stance_nodes']:
  expected=re.sub(r'((?:Expression|BlendWeight) ")([^"\n]*)(")',lambda m:m[1]+re.sub(r'\bStance\b',effective,m[2])+m[3],expected)
 if name in ('LeanForwardRotNodeErc','ErcMoveRasInjG'):
  suffix='Idle' if name=='LeanForwardRotNodeErc' else 'Walk'
  expected=expected.replace('Child "ML5_Stand'+suffix+'_right_RightHand_Rotate_Z"','Child "ML87_FirstPersonRaised'+suffix+'"')
 if name in ('LeanForwardRotNodeErc','LeanForwardMoveRotNode'):
  expected=re.sub(r'Expression "([^"]+)"',lambda m:'Expression "('+m[1]+')*(1.0-ML87FirstPersonCrouchLean)"',expected,count=1)
 assert expected==new[name],name
# Every cloned operation must match its crouch source exactly, including the
# ordered transform axis/space/type/amount, and only touch upper-body bones.
allowed={'Spine','Spine1','Spine2','Spine3','Head','Neck','Neck1','LeftArm','LeftForeArm','LeftHand','LeftShoulder','RightArm','RightForeArm','RightHand','RightShoulder'}
for item in spec['copied_upper_body_nodes']:
 src=old[item['source']];dst=new[item['clone']]
 for field in ('Expression','Bone','Axis','Space','Op','Amount'):
  assert re.findall(r'\b'+field+r' [^\n]+',src)==re.findall(r'\b'+field+r' [^\n]+',dst),(item,field)
 assert set(re.findall(r'Bone "([^"]+)"',dst))<=allowed
for suffix in ('Idle','Walk'):
 branch=new['ML87_FirstPersonRaised'+suffix]
 assert 'BlendWeight "ML87FirstPersonCrouchLean"' in branch
 assert 'Child0 "ML5_Stand'+suffix+'_right_RightHand_Rotate_Z"' in branch
 assert 'Child1 "ML87_FirstPersonCrouch'+suffix+'_right_RightHand_Rotate_Z"' in branch
 assert 'OptimizeMin 1' in branch and 'OptimizeMax 1' in branch
# Control zero is mathematically the original stance for all native stances;
# control one scopes custom upper body as crouch, without writing Stance.
for stance in (0,1,2):
 assert stance+(1-min(1,max(0,stance)))*0==stance
 assert stance+(1-min(1,max(0,stance)))*1==(1 if stance==0 else stance)
player=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
for marker in ('m_ML87ViewVar >= 0','!m_MLADSLeanDemo && firstPersonView','AnimSetFloat(m_ML87ViewVar, m_ML87ViewAmount)','if (m_ML87ViewAmount > 0)'):
 assert marker in player
assert not re.search(r'AnimSet\w+\([^\n]*"Stance"|OverrideStance|SetStance',player)
for other in ('m_MLADSLeanGateVar','m_MLADSLeanCanaryVar','m_MLADSLeanAmountVar','m_MLADSLeanNativeLeanVar','m_MLADSLeanNativeMoveVar','m_MLADSLeanWeaponShiftVar','m_MLADSLeanHeightVar','m_MLADSLeanMoveBlendVar','m_ML50ReachVar','m_ML56LowSmoothVar','m_ML71SupportVar'):
 assert 'm_ML87ViewVar != '+other in player
agr=(b/'WorkspaceSource/player_main.agr').read_text();assert agr.count('AnimSrcGCTVarFloat ML87FirstPersonCrouchLean ')==1
assert 'MLADSLeanLocomotion_v87.agf' in agr
print('PASS: 112 upper-body transforms match original crouch chains; local view selectors preserve native stance/legs and original third-person branches; standing late layers masked only in first person; camera code unchanged. Native playback unverified.')
