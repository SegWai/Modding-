MovementLab arms-only renderer test v2 (separate from stable movement)

Close DayZ. Extract this whole ZIP to a new folder. Steam must be running.
Run Launch-Movement-Test.cmd. It prepares the existing movement workspace and
loads your installed SNAFU Weapons mod from DayZ\!Workshop automatically.
If it cannot find the mod, create SNAFU-Mod-Path.txt in this folder containing
one local folder path, for example D:\SteamLibrary\steamapps\common\DayZ\!Workshop\@SNAFU Weapons.
No Workshop assets are included in this download.

Use FIRST PERSON. Raise a gun for hip aiming (hold RMB, not a quick ADS tap).
F9 enables/disables the fixed screen-space diagnostic arms and gun.
F10 cycles three candidate framings. The last shows arms/gun side by side to
check model loading separately. F9 restores the original view immediately.
The model contains arms/hands only, not a character body. It is static and grey.
The gun renderer uses the weapon actually in your hands, including attachments.
Both widget orientations are fixed; mouse turns do not rotate their models.
Their native item-preview cameras must be calibrated in-game. This is not yet
a calibrated grip or a finished FPS viewmodel. Independent widgets do not share
3D depth; gun/hand overlap is a known limitation of this diagnostic route.

ADS, third person, free-look, obstruction, weapon actions and reloads return to
native rendering. Fire/reload animation mirroring has not been implemented.
The test starts with the preview OFF. No full-body preview dummy is created.
Only one local, nonpersistent diagnostic arms item is created far below the
world and deleted when the mission ends. No AI targets are added.

Loadout: attempts SNAFU assault rifle, sniper, SMG and pistol by scanning loaded
public weapon configs and compatible magazine lists. Selected classes are in
script logs. Each has a loaded magazine and FIVE FULL SPARE MAGS; no loose ammo.
The installed SNAFU Weapons pack has not been available in the cloud, so class
recognition and ammunition compatibility require the local test. Missing roles
are logged; no item names or model paths from the pack are invented.
Existing black military clothing is retained because no SNAFU gear pack was
identified. The black test bag has expanded cargo to hold the spare magazines.

ModelSource contains the editable arms rig, baked static Blender scene, native
MLOD P3D, diagnostic preview image, validation report and asset attribution.
The P3D is already included in the script PBO; no Blender addon/import step is
needed for this FIRST DayZDiag loading test. DayZ Tools/native MLOD acceptance
and actual renderer output are unverified. A retail/binarized distribution has
not been built. Run Collect-Logs.cmd after testing if it fails to load.

Unchanged: movement speed logic, aiming controls, breathing, recoil and camera
logic from Revision49. The stable version and earlier tests remain separate.
