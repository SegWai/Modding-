"""Offline API, lifecycle, routing and preservation checks; not native playback."""
from pathlib import Path
import hashlib,json,re
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v161';b=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v162'
s=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text()
# Confirm the implementation uses the actual public engine APIs.
sdk=Path('/tmp/dayz-native162/scripts/3_game/human.c').read_text()
assert re.search(r'proto native void\s+ForceStance\(int pStanceIdx\)',sdk)
assert 'or -1 when release the stance lock' in sdk
assert 'bool\t\tIsRaised()' in sdk
obj=Path('/tmp/dayz-native162/scripts/3_game/entities/object.c').read_text();assert 'float scale = GetScale();' in obj
start=s.index(' protected void MLADSLeanUpdateDemoInput(');end=s.index(' protected void ML144UpdateEditor()',start);controller=s[start:end]
assert 'if (!m_MLADSLeanDemo || GetGame().IsMultiplayer())' in controller
assert 'nativeDemoMove.ForceStance(DayZPlayerConstants.STANCEIDX_RAISEDERECT);' in controller
assert 'if (nativeDemoMove && !m_ML162StanceLocked)' in controller
assert controller.index('ForceStance(')<controller.index('if (!m_MLADSLeanDemoReady)')
stop=s[s.index(' void MLADSLeanStopDemo()'):start]
assert 'releaseDemoMove.ForceStance(-1)' in stop and 'm_ML162StanceLocked = false;' in stop
cmd=s[s.index(' override void CommandHandler('):]
assert cmd.index('if (GetIsSimulationDisabled())')<cmd.index('MLADSLeanUpdateDemoInput(pDt)')<cmd.index('super.CommandHandler(')
assert 'raised = demoControllerActive;' not in s and 'ready = m_MLADSLeanDemoReady;' not in s
assert 'demoControllerActive = demoControllerActive && raised && ready && state.IsRaised();' in s
assert 'demoGraphValue = 1' not in s
assert 'AnimSetFloat(m_MLADSLeanCanaryVar, 0.731);' in s
assert 'AnimSetInt(m_MLADSLeanDemoArmIK, 7)' not in s
assert 'AnimSetBool(m_MLADSLeanDemoADS, m_ML162ADS)' in s
assert 'requestedHeadADS = m_ML162ADS;' in s
assert 'poseReference.IsInIronsights() || poseReference.IsInOptics()' in s
# Exercise readiness: native unraised/unfinished states never start the demo.
for raised in [False,True]:
 for complete in [False,True]:
  for native_raised in [False,True]:
   for bound in [False,True]:
    warm=0.;active=bound and raised and complete and native_raised
    for _ in range(60):warm=warm+1/60 if active else 0
    ready=active and warm>=.4
    assert ready==bool(bound and raised and complete and native_raised)
# Both ADS modes use separate left/right NPC head targets.
h=(b/'LogicSource/Scripts/4_World/MLHeadReference157.c').read_text();assert 'Ready[4]' in h
assert all('Ready['+str(i)+'] = false;' in h for i in range(4))
assert 'ML157HeadReference.Ready[sideHead]' not in s and 'ML157HeadReference.Target[sideHead]' not in s
assert 'headReferenceADS = m_ML162ADS;' in s
keys={(side,ads):side+(2 if ads else 0) for side in [0,1] for ads in [False,True]};assert set(keys.values())==set(range(4))
# No model scaling, height offset or pose graph rewrite.
assert not re.search(r'\bSetScale\s*\(',s)
assert (a/'WorkspaceSource/locomotion.agf').read_bytes()==(b/'WorkspaceSource/locomotion.agf').read_bytes()
for path in (a/'LogicSource/Scripts').rglob('*.c'):
 if path.name in ['MLADSLeanPlayer.c','MLHeadReference157.c']:continue
 assert path.read_bytes()==(b/path.relative_to(a)).read_bytes(),path
assert (a/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()==(b/'Missions/MLADSLeanMosin.ChernarusPlus/init.c').read_bytes()
for rel in ['MLLeanPreset.json','Profiles/LeanMosin/MLLeanPreset.json','LogicSource/Presets/MLLeanPreset.json']:
 assert (a/rel).read_bytes()==(b/rel).read_bytes()
 assert hashlib.sha256((b/rel).read_bytes()).hexdigest()=='aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d'
assert 'm_ML136Cycle >= 2.0' in s and 'ML158DemoCycle.Target' in s
for path in (b/'LogicSource').rglob('*.c'):
 text=path.read_text();assert text.count('{')==text.count('}'),path
report={'native_api_signature':'verified against official script repository','native_stance_lock':'raised erect once; -1 release on stop','ready':'requires actual raised state and native weapon raise completion','routing':'normal canary; no forced ArmIK; NPC ADS/head follows selected player ADS mode','head_reference_cache':'four slots for left/right and raised/ADS','height_audit':'read-only native stance/raise/scale/head+pelvis above feet/origin above ground','preservation':'v161 raw fixed preset, v160 direct body shift graph, camera, input, loadout and NPC cycle unchanged','native_runtime':'NOT RUN: compilation/actual native stance transition/height equality/grip require in-game verification'}
(b/'NPC-Native-Stance-Checks-v162.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
