"""Keep weapon model axis invariant and prevent unmirrored support IK overwriting pose."""
from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v4';b=a.with_name('MovementLab_Ambidextrous_Lean_v5');old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());assert old.keys()==new.keys()
for n,v in old.items():
 expected=v.replace('weaponaxis= +x','weaponaxis= -x').replace('WeightSecondaryChain "true"','WeightSecondaryChain "false"')if n=='MLASwapLeftWeapon'else v
 assert new[n]==expected,n
left=new['MLASwapLeftWeapon'];right=new['ML166_PublishFinalAimedWeapon']
axis=lambda x:re.search(r'weaponaxis= ([+-]x)',x)[1]
assert axis(left)==axis(right)=='-x'
assert 'hand = LeftHand'in left and 'weaponrotator = LeftHand'in left
assert 'WeightPrimaryChain "false"'in left and 'WeightSecondaryChain "false"'in left
assert 'WeightAim "true"'in left and 'outputweaponoffsettobuffer = true'in left
# No hand/forearm/arm coefficients, reference solver, scene, inputs or data altered.
for name in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [name,'Profiles/LeanMosin/'+name,'LogicSource/Presets/'+name]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['LogicSource/Inputs.xml','Missions/MLADSLeanMosin.ChernarusPlus/init.c']:assert(a/rel).read_bytes()==(b/rel).read_bytes()
source=(a/'LogicSource/Scripts/4_World/MLAShoulderPose.c').read_text();changed=(b/'LogicSource/Scripts/4_World/MLAShoulderPose.c').read_text()
def method(text,name,nextname):return text[text.index(name):text.index(nextname,text.index(name)+len(name))]
assert method(source,' ML144Rot ReflectRotation',' void Write(')==method(changed,' ML144Rot ReflectRotation',' void Write(')
start=changed.index(' void ReportContact(');end=changed.index(' ML144Rot ReflectRotation',start);diagnostic=changed[start:end]
assert 'solution.ContactReported || ContactSettle < 0.25'in diagnostic
assert not any(call in diagnostic for call in ['AnimSet','SetPosition','Cache[','Solve('])
assert 'cached.SourceWeaponFrame = ReadWeaponFrame(actor)'in changed
assert 'ReportContact(actor, cached, key, dt)'in changed
assert 'Override3rdIsRightShoulder(HumanInputControllerOverrideType.ENABLED, !MLAShoulderSettings.LeftActive)'in changed
assert not re.search(r'\w+\[[^\]]+\]\s*(?:\+\+|--)',changed)
# Diagnostics reuse existing known native method calls from shipped FP camera.
known=(a/'LogicSource/Scripts/4_World/MLADSLeanCamera.c').read_text();assert 'WeaponGetCameraPointMSTransform'in known and 'GetCameraPoint'in known
print('PASS: exactly2 left-publisher graph fields changed; native model axis invariant; no native arm re-solve; mirror solver/input/presets/scene unchanged; diagnostics read-only and once/context. Native visual result NOT RUN.')
