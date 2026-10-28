"""Offline structural/math checks, NOT native left-weapon-IK validation."""
from pathlib import Path
import sys,json,re,itertools,xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
import captured_pose_bridge as bridge
r=Path(__file__).resolve().parents[1];base=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v186';out=r/'shoulder-swap-test/MovementLab_Ambidextrous_Lean_v1';j=json.loads((out/'Ambidextrous-v1.json').read_text());w=out/'LogicSource/Scripts/4_World'
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'Profiles/LeanMosin/'+n,'LogicSource/Presets/'+n]:assert(base/rel).read_bytes()==(out/rel).read_bytes()
assert not(w/'MLInspectionCamera171.c').exists()
for p in w.glob('*.c'):
 assert 'modded class DayZPlayerCamera3rdPerson'not in p.read_text()
config=(out/'LogicSource/config.cpp').read_text();assert 'inputs = "MLAmbidextrousLogic/Inputs.xml"'in config
x=ET.parse(out/'LogicSource/Inputs.xml');assert x.find('.//actions/input').attrib['name']=='UAMLAShoulderSwap';assert x.find('.//preset/input/btn').attrib['name']=='mB4'
old=newnodes((base/'WorkspaceSource/locomotion.agf').read_text());nodes=newnodes((out/'WorkspaceSource/locomotion.agf').read_text());added=set(nodes)-set(old);named={n for n in added if not n.startswith('{')};assert named==set(j['new_nodes'])and len(named)==303
assert 'Child "MLASwapBeforeAim"'in nodes['ML166_FinalVerticalAim']
assert 'max(MLASwapActive,'in nodes['ML166_FinalAimOnly']
left=nodes['MLASwapLeftWeapon']
for text in ['hand = LeftHand','weaponrotator = LeftHand','weaponaxis= +x','chain = LeftArm, LeftArmRoll, LeftForeArm, LeftForeArmRoll, LeftHand','secchain = RightArm, RightArmRoll, RightForeArm, RightForeArmRoll, RightHand','outputweaponoffsettobuffer = true','WeightSecondaryChain "true"']:assert text in left,text
# No unsupported mirror node/op; only known native transforms/IK/binary blends.
for n in named:
 assert nodes[n].split()[0]in ['AnimSrcNodeProcTransform','AnimSrcNodeWeaponIk','AnimSrcNodeBlend']
for n in ['MLASwapBeforeAim','MLASwapWeaponOutput']:assert 'OptimizeMin 1'in nodes[n]and 'OptimizeMax 1'in nodes[n]
sys.setrecursionlimit(20000);done=set();visiting=set()
def visit(n):
 if n in done or n not in nodes:return
 assert n not in visiting,n
 visiting.add(n)
 for c in re.findall(r'\bChild\d* "([^"]+)"',nodes[n]):
  if c.startswith('MLASwap'):assert c in nodes,c
  visit(c)
 visiting.remove(n);done.add(n)
for n in nodes:
 if not n.startswith('{'):visit(n)
agr=(out/'WorkspaceSource/player_main.agr').read_text();assert len(re.findall(r'AnimSrcGCTVarFloat MLASwap\w+\s*\{',agr))==301
# Chest-relative mirrored deformation twice is identity, regardless of neutral
# bone bases. This guards185's semantic basis issue for swapped L/R bones too.
S=np.diag([-1.,1,1]);rng=np.random.default_rng(709);maxerr=0
for sample in range(500):
 C=Rotation.random(random_state=rng).as_matrix();Bl=Rotation.random(random_state=rng).as_matrix();Br=Rotation.random(random_state=rng).as_matrix();R=Rotation.random(random_state=rng).as_matrix()
 mirrored=C@S@(C.T@R@Br.T)@S@Bl
 back=C@S@(C.T@mirrored@Bl.T)@S@Br
 maxerr=max(maxerr,float(abs(back-R).max()));assert np.allclose(back,R,atol=1e-12)
 # No deformation preserves destination basis, rather than inverting it.
 neutral=C@S@(C.T@(C@Br)@Br.T)@S@Bl;assert np.allclose(neutral,C@Bl,atol=1e-12)
# Actual hierarchical FK, target positions across all50 model bones. Native
# profile weapon publication is outside this math and must be tested in game.
names=j['bones'];parents={n:None if p<0 else names[p]for n,p in zip(names,j['parents'])};opposite={n:names[o]for n,o in zip(names,j['opposite'])}
assert len(names)==50 and sum('Hand' in n for n in names)>30
for n in names:assert opposite[opposite[n]]==n
captures=json.loads((base/'Native-Head-Travel-v55.json').read_text());source={n:np.array(captures['sides']['right']['desired'][n])for n in names};neutral={n:np.array(captures['sides']['left']['reference'][n])for n in names};root=source['Spine3'];C=root[:3,:3]@neutral['Spine3'][:3,:3].T;target={}
for n in names:
 target[n]=source[n].copy()
 if n=='Spine3':continue
 other=opposite[n];target[n][:3,:3]=C@S@(C.T@source[other][:3,:3]@neutral[other][:3,:3].T)@S@neutral[n][:3,:3];target[n][:3,3]=root[:3,3]+C@S@C.T@(source[other][:3,3]-root[:3,3])
src={n:m.tolist()for n,m in source.items()};dst={n:m.tolist()for n,m in target.items()};corr=bridge.solve(src,dst,parents);replay=bridge.reconstruct(src,parents,corr);fk=max(abs(np.array(replay[n])-target[n]).max()for n in names);assert fk<1e-10
h=(w/'MLAShoulderPose.c').read_text();assert 'actor.MLAShoulderCaptureReady()'in h
assert 'ML172Snapshot source = Capture(actor);'in h and 'Cache[key] = cached;'in h
assert 'LocalTakeEntityToHands'not in h and 'ObjectDelete'not in h and 'SetPosition('not in h
assert 'Override3rdIsRightShoulder'in h and 'm_fDistance'not in h
assert not re.search(r'\w+\[[^\]]+\]\s*(?:\+\+|--)',h)
keys={s*18+m*6+l*2+a for s,m,l,a in itertools.product(range(2),range(3),range(3),range(2))};assert keys==set(range(36))
res={'saved_four_banks':'byte-identical186','third_person_framing':'native class override removed','input':'XML registered/rebindable, mouse4 default; native binding NOT RUN','new_nodes':303,'new_controls':301,'known_native_node_types_only':True,'reflection_cases':500,'max_reflection_error':maxerr,'50bone_FK_error':float(fk),'context_keys':36,'native_compile_left_weapon_IK_firing_ADS_reload_contact_FPS':'NOT RUN'}
(out/'Ambidextrous-Checks-v1.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
