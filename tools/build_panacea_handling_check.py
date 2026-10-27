"""Build a separate native weapon-handling control; no custom lean code."""
from pathlib import Path
import importlib.util,json,hashlib,zipfile
r=Path(__file__).resolve().parents[1];b=r/'ads-lean-test/Panacea_Weapon_Handling_Check_v1'
spec=importlib.util.spec_from_file_location('pbo_builder',r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v106/build_pbos.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=b/'CheckSource';sources=list(source.rglob('*.c'))
assert len(sources)==1 and sources[0].name=='DiagInventory.c'
assert 'modded class PluginManager' in sources[0].read_text()
for forbidden in ['modded class PlayerBase','DayZPlayerCamera','AddItemInHandsProfile','AnimSetFloat','OverrideRaise','OverrideMovement']:
 assert forbidden not in '\n'.join(p.read_text() for p in sources)
sha=m.build(source,'PWHC',b/'@PWHC/Addons/PWHC.pbo')
launcher=(b/'Launch-Handling-Check.ps1').read_text()
assert '$mods = @($panacea,$helper)' in launcher
assert '$workspace' not in launcher and '$logic' not in launcher
assert '2389010221' in launcher
mission=(b/'Missions/PWHC.ChernarusPlus/init.c').read_text()
assert 'MLADSLean' not in mission
assert 'SpawnWeapon(player, "AK74", "Mag_AK74_30Rnd", 0)' in mission
for name in ['PNC_W_SCARH','PNC_W_AWM']:assert name in mission
assert 'm_Samples >= 120' in mission and 'OnMissionFinish()' in mission
(b/'manifest.json').write_text(json.dumps({'helper_sha256':sha,'purpose':'Native Panacea weapon handling vs vanilla AK74, no custom workspace/camera/player/ammo scripts','native_test_status':'not run; requires Windows DayZDiag'},indent=2)+'\n')
files=['@PWHC/Addons/PWHC.pbo','Missions/PWHC.ChernarusPlus/init.c','Launch-Handling-Check.cmd','Launch-Handling-Check.ps1','Collect-Logs.cmd','Collect-Logs.ps1','manifest.json','README.txt']
out=r/'artifacts/Panacea_Weapon_Handling_Check_v1.zip'
expected={b.name+'/'+name:(b/name).read_bytes() for name in files}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,data in expected.items():z.writestr(name,data)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and set(z.namelist())==set(expected)
 for name,data in expected.items():assert z.read(name)==data
print(f'PASS: native-only helper PBO independently parsed/verified, no pose/camera/profile/input overrides, bounded sampling, isolated launcher, {len(files)} runtime files; {out.stat().st_size} bytes. Native execution pending.')
