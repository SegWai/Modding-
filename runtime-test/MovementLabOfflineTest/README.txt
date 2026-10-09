MovementLab offline arm-lift diagnostic — DayZ 1.29

STATUS
The original animation has been confirmed in Blender and DayZ Animation Editor.
The user confirmed that this offline baseline launches, the character moves,
and F6 plays the original greeting. Packing and the custom runtime profile test
remain pending. New installations should still check the baseline first.
This is a small practice mission, not a complete offline DayZ survival mode.

1. EXTRACT AND CHECK THE BASELINE
Extract the ZIP into D:\DayZProjects. The resulting folder should be:
  D:\DayZProjects\MovementLabOfflineTest
Keep all files together. Steam must be running; close any running DayZ game.
Double-click Launch-Baseline.cmd in that folder.
Expected: Chernarus loads with one controllable, empty-handed character.
Use your Change perspective control to see the character (Enter by default).
Stand still, upright, and press F6. The original DayZ greeting should play.
Exit the game after checking. A script error here is a mission issue, before
any animation mod is loaded.

2. PREPARE THE EXISTING COMPILED ANIMATION
Double-click Prepare-Animation.cmd. It copies the ANM that already plays in
Animation Editor from the Workbench test folder into this new mod's Animations
folder. No conversion is needed. A different existing destination is preserved.
The source/launch paths match the installation reported in this conversation.

3. PACK WITH DAYZ TOOLS / ADDON BUILDER
Use the folder containing Launch-Baseline.cmd as the test root. Windows Extract
All can add an outer folder named MovementLab_Offline_Test; include that folder
in both paths if present. For the installation in this conversation:
Source:
  D:\DayZProjects\MovementLab_Offline_Test\MovementLabOfflineTest\MovementLabRuntimeTest
Destination DIRECTORY (folder only):
  D:\DayZProjects\MovementLab_Offline_Test\MovementLabOfflineTest\@MovementLabRuntimeTest\Addons
Do not append a .pbo filename to the destination field: the installed builder
created an extra folder with that name. It should produce the file
MovementLabRuntimeTest.pbo directly inside Addons.
If a directory with that filename already exists, preserve it outside Addons
before putting the actual PBO file in its place. In PowerShell, confirm the
result with Test-Path -PathType Leaf; an ordinary Test-Path also accepts folders.
Use prefix MovementLabRuntimeTest (the source includes a $PBOPREFIX$ file).
For this diagnostic use packing without binarizing:
the animation is already compiled, and the config/scripts/ASI are text.
Ensure .anm, .asi, and .c files are included. If your Addon Builder uses a
"List of files to copy directly", include *.anm;*.asi;*.c;*.cpp in that list.
Keep the prefix exactly MovementLabRuntimeTest. If the installed packing
controls differ, capture the Addon Builder window before changing other options.
No signing or Workshop publishing is needed for this local diagnostic launch.

4. LAUNCH WITH THE MOD
Double-click Launch-With-Mod.cmd. It requires the packed PBO in the folder above.
Stand still, upright, with empty hands. Use Change perspective, then press F6.
Expected: the greeting's standing loop uses our four-second right arm lift.
The greeting's original entry/exit phases remain, so a brief vanilla movement
can appear before/after the test loop. Walking/running slots are inherited.
Check that the body stays correctly shaped, the arm moves, and movement resumes.
Report vanilla-only playback, distortion, or a stuck gesture separately.

LOGS
Baseline: MovementLabOfflineTest\Profiles\Baseline
With mod: MovementLabOfflineTest\Profiles\WithMod
Expected script markers:
  [MovementLab] Offline character selected...
  [MovementLab] Greeting requested...
With mod, also:
  [MovementLab] Registered the arm-lift greeting profile for empty hands.
The registration marker only confirms the script ran, not that the ANM loaded.
Send the first script/animation error or a screenshot if launch or playback fails.

SCOPE AND REFERENCE
The mission creates one player, sets noon, and protects it from damage during
testing. It starts no economy and saves no character. It uses its own profiles.
The launchers do not kill processes, delete saves, or change Steam launch options.
The mod supplies a child ASI and uses RegisterEmptyHanded /
SetDefaultItemInHandsProfile. It changes Gesture.SaluteErc.Loop only, matching
the installed slot reported by the user. It replaces no vanilla graph files.
Compatibility with other mods and multiplayer has not been tested.

APIs checked against official scripts, build 1.29.163709, revision 125372:
https://github.com/BohemiaInteractive/DayZ-Script-Diff/tree/86974a0f5bd16b1ee3e334ad828133c93dca80a1
The offline mission lifecycle was cross-checked with the community offline-mode
implementation, commit f10b18313aac4fde8eebb9dedff7d303046b34c4:
https://github.com/Arkensor/DayZCommunityOfflineMode
Its admin tools, scripts, assets, and destructive batch launcher are not bundled.

See ASSET_NOTICES.txt for the authored animation's rig/exporter references.
No Rockstar assets are used. Full movement/controller replacement remains unproven.
