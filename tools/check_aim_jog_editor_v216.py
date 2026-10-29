"""Armed walking/jogging preview isolation, gait references and native profile scope."""
from pathlib import Path
import re,hashlib
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v215';b=a.with_name('MovementLab_ADS_Lean_Mosin_v216');digest='96135c85d6c493b050e15416ab38925a55205b05fc178df50d152a31e9260194'
for rel in ['MLSodaCanWalkingLeanPreset.json','LogicSource/Presets/MLSodaCanWalkingLeanPreset.json','Profiles/LeanMosin/MLSodaCanWalkingLeanPreset.json']:assert hashlib.sha256((b/rel).read_bytes()).hexdigest()==digest
for p in (a/'LogicSource/Presets').glob('*.json'):
 for rel in [p.name,'LogicSource/Presets/'+p.name,'Profiles/LeanMosin/'+p.name]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for rel in ['MLJoggingLeanPreset.json','LogicSource/Presets/MLJoggingLeanPreset.json','Profiles/LeanMosin/MLJoggingLeanPreset.json']:assert(b/rel).read_bytes()==(a/'MLWalkingLeanPreset.json').read_bytes()
assert(a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
# Scoped bank exchange is the same synchronous tested pattern, with independent states.
assert (b/'LogicSource/Scripts/4_World/MLJoggingEditorScope216.c').read_text()==(a/'LogicSource/Scripts/4_World/MLWalkingEditorScope173.c').read_text().replace('ML173','ML216')
p=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
for s in ['m_ML181HoldRevision[4]','m_ML181BodyRevision[4]','m_ML154ReferenceReady[8]','m_ML146Root[16]','m_ML146Elbow[16]','m_ML146Wrist[16]','clearBank < 8','bank = 3;','state.m_iMovement == 2 && m_MLADSLeanMoveBlend > 0.98','previewSpeed = m_ML216PreviewGait;','m_ML216Scope.Enter();','m_ML216Scope.Leave();']:assert s in p,s
# Reference indices for four banks, two lean sides, two arm chains fit all arrays.
assert max((bank*2+side)*2+arm for bank in range(4)for side in range(2)for arm in range(2))==15
assert p.index('m_ML216Scope.Enter();')<p.index('  ML173UpdateGraph(pDt, pCurrentCommandID, pCurrentCommandFinished);')<p.index('m_ML216Scope.Leave();')
m=(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_text();scene=m[m.index(' void ML181SpawnCrouchPair()'):m.index(' override void OnMissionFinish()')]
assert scene.count('ML206CreatePreview(')==2
assert '"AK74", "Hoodie_Grey", true, true, false' in scene and '"AK74", "Hoodie_Blue", true, true, false' in scene
assert 'walker.ML216StartAimGaitPreview(1)'in scene and 'jogger.ML216StartAimGaitPreview(2)'in scene
assert 'MLADSLeanSettings.DemoActor = jogger'in scene
assert 'm_ML183UnarmedPreview = false;'in p[p.index(' void ML213StartRaisedLineup'):p.index(' protected bool m_ML207SmgEditor')]
clock=(b/'LogicSource/Scripts/4_World/MLAimGaitCycle216.c').read_text();assert '(elapsed - 12000) / 1000'in clock and 'ML216WeaponState.Open'in clock
assert 'return now - Epoch >= 3000;'in clock
for t in range(12000,24000,1000):assert ((t-12000)//1000)%2 != (((t+1000)-12000)//1000)%2
bank=(b/'LogicSource/Scripts/4_World/MLJoggingEditor216.c').read_text();assert '$profile:MLJoggingLeanPreset.json'in bank and 'MLWalkingLeanPreset.json'not in bank
for f in (b/'LogicSource/Scripts/5_Mission').glob('*.c'):
 s=f.read_text();assert 'ML214WeaponState'not in s
 for member in re.findall(r'ML216WeaponState\.(\w+)',s):assert re.search(r'\b'+member+r'\b',bank),member
# Check the approved can/bandage exception is not a blanket one-handed override.
cat=(b/'LogicSource/Scripts/4_World/MLHeldCategory192.c').read_text();classify=cat[cat.index(' static bool UsesCanBandageHolding'):cat.index(' static bool UsesOneHandedHolding')]
assert 'player_main_1h_sodacan'in classify and 'player_main_1h_bandage'in classify
assert 'Lassi_ColorBase'in classify and 'BandageDressing'in classify and 'ItemBehaviorType.ONEHANDED'in classify
sdk=Path('/tmp/dayz-native162/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c').read_text()
for item,profile in [('SodaCan_ColorBase','player_main_1h_sodacan.asi'),('Lassi_ColorBase','player_main_1h_sodacan.asi'),('BandageDressing','player_main_1h_bandage.asi')]:
 line=next(l for l in sdk.splitlines()if 'AddItemInHandsProfileIK("'+item+'"'in l);assert profile in line
print('PASS:all14approved banks exact+jogseed;walking1/jog2raised2NPC/one-second clock;isolated jogging scope/4bank8side16arm caches and gait2calibration;menu members;can-bandage scope. Native compile/actual jog/grip/UI/FPS NOT RUN.')
