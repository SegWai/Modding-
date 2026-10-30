from pathlib import Path
import struct,hashlib,re,importlib.util,zipfile
r=Path(__file__).resolve().parents[1];kit=r/'hud-icons-test/MovementLabLocomotion_v80_StartupFix1';out=r/'artifacts/MovementLab_v80_StartupFix1_PBOs';(out/'@MovementLabStartGate/Addons').mkdir(parents=True,exist_ok=True);(out/'@MovementLabSlowCrouchClips/Addons').mkdir(parents=True,exist_ok=True)
script=(kit/'@MovementLabStartGate/Addons/MovementLabStartGate.pbo').read_bytes();(out/'@MovementLabStartGate/Addons/MovementLabStartGate.pbo').write_bytes(script)
ws=kit/'WorkspacePatches';entries={p.relative_to(ws).as_posix().replace('/','\\'):p.read_bytes()for p in ws.rglob('*')if p.is_file()}
entries['config.cpp']=b'class CfgPatches { class MovementLabCrouchWheelWorkspace { units[] = {}; weapons[] = {}; requiredVersion = 0.1; requiredAddons[] = {"DZ_Anims_Cfg", "MovementLabSlowCrouchClips"}; }; };'
header=b'\0'+struct.pack('<5I',0x56657273,0,0,0,0)+b'prefix\0DZ\\anims\\workspaces\\player\\player_main\0\0'
for name,data in sorted(entries.items()):header+=name.encode()+b'\0'+struct.pack('<5I',0,0,0,0,len(data))
body=header+b'\0'+struct.pack('<5I',0,0,0,0,0)+b''.join(data for _,data in sorted(entries.items()));workspace=body+b'\0'+hashlib.sha1(body).digest();(out/'@MovementLabSlowCrouchClips/Addons/MovementLabCrouchWheelWorkspace.pbo').write_bytes(workspace)
spec=importlib.util.spec_from_file_location('reader',r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v225/build_pbos.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prefix,actual=m.read_pbo(workspace);assert prefix=='DZ\\anims\\workspaces\\player\\player_main'and actual==entries
prefix,actual=m.read_pbo(script);assert prefix=='MovementLabStartGate';assert actual['Scripts\\4_World\\MovementLabDiagnosticInventory.c']==(kit/'StartGateSource/Scripts/4_World/MovementLabDiagnosticInventory.c').read_bytes()
(out/'INSTALL.txt').write_text('''V80 STARTUP FIX1 - TWO UPDATED PBOs

Close DayZ. In your extracted v80 test folder, replace BOTH matching files:
1. @MovementLabStartGate/Addons/MovementLabStartGate.pbo
2. @MovementLabSlowCrouchClips/Addons/MovementLabCrouchWheelWorkspace.pbo

KEEP your existing @MovementLabSlowCrouchClips/Addons/MovementLabSlowCrouchClips.pbo.
It contains original/retimed animation clips generated on your PC and is still
required. These two update PBOs alone do not replace that third clip PBO.

Use Launch-Prebuilt-PBO-Test.cmd from inside your test folder to test these
PBOs without the setup script rebuilding and overwriting the workspace PBO.
Copy that CMD alongside your existing Launch-Movement-Test.cmd.
Existing SNAFU/MMG resolved paths and mission are retained.
Do not load alongside older duplicate MovementLab versions.

Offline PBO checksum/prefix/source-content and ZIP integrity verified.
Native DayZ startup fix remains unconfirmed. Send fresh logs if it crashes.
''')
# Use exact existing launch/configuration path, skip ONLY the regeneration step.
cmd=(kit/'Launch-Movement-Test.cmd').read_text();call='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%movementlabTestDir%Prepare-Crouch-Clips.ps1"\nif errorlevel 1 goto failed';assert call in cmd
replacement='''if not exist "%movementlabTestDir%@MovementLabSlowCrouchClips\\Addons\\MovementLabSlowCrouchClips.pbo" (
    echo Required animation clips PBO is missing. Run the full test setup first.
    goto failed
)
if not exist "%movementlabTestDir%@MovementLabSlowCrouchClips\\Addons\\MovementLabCrouchWheelWorkspace.pbo" (
    echo Updated workspace PBO is missing. Copy both update PBOs into this folder.
    goto failed
)'''
cmd=cmd.replace(call,replacement,1);(out/'Launch-Prebuilt-PBO-Test.cmd').write_bytes(cmd.replace('\r\n','\n').replace('\n','\r\n').encode())
zip_path=r/'artifacts/MovementLab_v80_StartupFix1_PBOs.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted(out.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(out).as_posix())
with zipfile.ZipFile(zip_path)as z:
 assert z.testzip()is None
 assert 'Prepare-Crouch-Clips.ps1'not in z.read('Launch-Prebuilt-PBO-Test.cmd').decode()
 for f in out.rglob('*'):
  if f.is_file():assert z.read(f.relative_to(out).as_posix())==f.read_bytes()
print('PASS:both PBO prefix/checksum/source payload;private workspace reference;launcher skips regeneration;ZIPexact. Game NOT RUN.')
print(zip_path,zip_path.stat().st_size)
