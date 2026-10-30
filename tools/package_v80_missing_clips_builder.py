from pathlib import Path
import shutil,zipfile,hashlib,json
r=Path(__file__).resolve().parents[1];src=r/'hud-icons-test/MovementLabLocomotion_v80_StartupFix1';out=r/'artifacts/MovementLab_v80_MissingClips_Builder';out.mkdir(exist_ok=True)
s=(src/'Prepare-Crouch-Clips.ps1').read_text();cut=s.index('\n$movementlabWorkspaceRoot = Join-Path');s=s[:cut]
old='''    if ((Test-Path -LiteralPath (Join-Path $Candidate $movementlabUnarmedRelative) -PathType Container) -and
        (Test-Path -LiteralPath (Join-Path $Candidate $movementlabWorkspaceRelative) -PathType Container)) {'''
assert old in s;s=s.replace(old,'''    if (Test-Path -LiteralPath (Join-Path $Candidate $movementlabUnarmedRelative) -PathType Container) {''',1)
s=s.replace("    throw 'The selected folder lacks extracted DZ\\anims data. Use DayZ Tools > Extract Game Data, then select its output folder. This is not the Steam DayZ installation folder.'","    throw 'The selected folder lacks extracted DZ\\anims animation data. Use DayZ Tools > Extract Game Data, then select its output folder.'")
s+='''\nWrite-Host 'DONE: Missing animation-clips PBO built. Script and workspace PBOs were not changed.'
Write-Host 'Now run Launch-Prebuilt-PBO-Test.cmd from your existing test folder.'
'''
(out/'Build-Missing-Clips.ps1').write_text(s)
for name in ['Armed-Speed-Plan.json','RequiredOriginalClips.txt']:shutil.copy2(src/name,out/name)
(out/'Build-Missing-Clips.cmd').write_bytes('''@echo off
setlocal EnableExtensions DisableDelayedExpansion
powershell.exe -NoProfile -NonInteractive -Command "if (Get-Process -Name DayZ_x64,DayZDiag_x64 -ErrorAction SilentlyContinue) { exit 1 }"
if errorlevel 1 (
    echo Close DayZ before building the missing animation PBO.
    pause
    exit /b 1
)
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0Build-Missing-Clips.ps1"
if errorlevel 1 (
    echo Build failed. Keep the error text and send it for diagnosis.
    pause
    exit /b 1
)
echo Clips PBO ready. Run Launch-Prebuilt-PBO-Test.cmd in this test folder.
pause
'''.replace('\n','\r\n').encode())
(out/'READ-ME-FIRST.txt').write_text('''V80 MISSING CLIPS PBO - BUILD ONLY

The cloud workspace lacks your original animation clips. This is a builder,
not a pre-generated PBO. It uses extracted game files already on your PC.

1.CloseDayZ. Extract ALL files here into your EXISTINGv80testfolder, alongside
  Launch-Prebuilt-PBO-Test.cmd. Replacing Armed-Speed-Plan/RequiredOriginalClips
  with these identicalv80copies is fine.
2.Double-click Build-Missing-Clips.cmd. Select DayZProjects/DZ folder if asked.
3.It creates @MovementLabSlowCrouchClips/Addons/MovementLabSlowCrouchClips.pbo.
4.Run Launch-Prebuilt-PBO-Test.cmd again.

Original clip content/retiming/speed-plan code is exactlyv80StartupFix1's build
section. Includes1245armed variants,standingwalk/jog andcrouchtier variants.
Originaldatareadonly. Does NOT rebuild or replace MovementLabStartGate.pbo or
MovementLabCrouchWheelWorkspace.pbo. No workspacegraphpacking code included.
Only changes pathcache MovementLab-ProjectRoot.txt and writesclipsPBO.
Your extracteddata must contain all required originals. If not, extract them
using DayZTools beforebuilding;missingcliperrorsname the neededsource.
NativeWindowsPowerShell execution NOTRUN in cloud. No native PBO supplied here.
''')
# Prove the payload-generation section was copied exactly, including all FPS
# writes/source paths/config/PBO serialization. Only discovery is relaxed.
original=(src/'Prepare-Crouch-Clips.ps1').read_text();start="$movementlabRoot = (Resolve-Path -LiteralPath $OriginalRoot)";assert s[s.index(start):s.index("\nWrite-Host 'DONE:")].rstrip()==original[original.index(start):cut].rstrip()
assert s.count("$movementlabTarget = Join-Path")==1
assert 'MovementLabCrouchWheelWorkspace.pbo'not in s and 'MovementLabStartGate.pbo'not in s
for n in ['Armed-Speed-Plan.json','RequiredOriginalClips.txt']:assert(out/n).read_bytes()==(src/n).read_bytes()
zpath=r/'artifacts/MovementLab_v80_MissingClips_Builder.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted(out.iterdir()):z.write(f,f.name)
with zipfile.ZipFile(zpath)as z:
 assert z.testzip()is None
 for f in out.iterdir():assert z.read(f.name)==f.read_bytes()
print('PASS:clip-generation code+plan+requiredfiles exact v80;onlyoneoutputPBO/no workspace packing;ZIPexact. WindowsPowerShell NOT RUN.')
print(zpath,zpath.stat().st_size)
