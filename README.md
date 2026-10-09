# MovementLab

DayZ remains the base game. The goal is original player animations and movement
inspired by the weight and pacing of Red Dead Redemption 2.

[Download the animation test bundle (ZIP, 1.4 MB)](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_ArmLift_Test.zip)

If GitHub shows the ZIP's file page, use **Download raw file** (the download
arrow) to save it. The bundle includes the editable Blender file, DayZ animation
source, import metadata, checks, and asset notices.

## Confirmed so far

- The user's DayZ 1.29 Animation Editor loads the player model and plays an
  existing walking animation.
- The user opened the original arm-lift Blender file in Blender 4.3.2 and
  confirmed that its animation plays.
- Workbench produced `MovementLab_ArmLift_Test.anm` after reimporting the TXA.
  The user assigned it to a separate preview instance and confirmed that the
  arm lifts in DayZ 1.29 Animation Editor.
- The offline baseline mission launches on the user's PC, the character can
  move, and F6 plays the original greeting.
- The user packed the custom profile and confirmed that **F1** plays our
  original arm-lift animation inside DayZ.
- The user confirmed normal movement returns after the gesture ends, with
  no body distortion observed during playback.
- Blender 4.3.2 here authors and exports an original four-second arm-lift test
  as TXA. Checks cover frame ranges, bone names against the authoring rig,
  finite transforms, normalized rotations, stationary feet, and matching loop
  endpoints. Rendered start and middle poses were inspected.

The Blender → TXA → Workbench ANM → PBO → in-game playback pipeline is confirmed
by the user’s local tests.
Replacing the locomotion controller, aiming, combat, and multiplayer behavior
remain unproven. This test is an import diagnostic, not the intended final gait.

## First original walking study

[Download the walking study](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Unarmed_Walk_v01.zip).
Open `TestAnimations/MovementLab_Unarmed_Walk_v01.blend` in Blender 4.3.2 and
press Space. This original in-place loop has alternating foot contacts, a
small hip weight shift, and opposing arm swing. The bundle includes a GIF,
TXA source, import metadata, and a separate Workbench preview workspace.
Its README gives the import and **Set Anim** steps already used for the arm lift.

The study uses a 1.2-second cycle and a nominal 0.80 m/s authoring reference.
Cloud checks verify matching endpoint poses, stationary root, reachable leg
targets, unchanged bone scales, the baked action against authored poses, and
contact drift compensated for that nominal travel. The TXA was parsed back
and checked for finite transforms, normalized rotations, and all 152 nodes.
Rendered contact and swing poses were inspected. This does not establish foot
contact at DayZ's actual speed: walking Workbench import, native timing,
footstep events, and gameplay blending remain pending. Keep the working
arm-lift runtime test as-is until the new clip's preview and pace are checked.

To reproduce it after the existing cloud setup:

```sh
BLENDER_USER_CONFIG=/tmp/dayz-local-workbench/blender-config \
BLENDER_USER_EXTENSIONS=/tmp/dayz-local-workbench/blender-extensions \
blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python tools/build_walk_clip.py -- \
  --rig /tmp/dayz-local-workbench/dayz_reference_rig.blend \
  --addon-root /tmp/dayz-animation-plugin/BlenderPlugin \
  --output /tmp/movementlab-walk-v01
BLENDER_USER_CONFIG=/tmp/dayz-local-workbench/blender-config \
BLENDER_USER_EXTENSIONS=/tmp/dayz-local-workbench/blender-extensions \
blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python tools/render_walk_preview.py -- --output /tmp/movementlab-walk-v01
python tools/package_walk_test.py --generated /tmp/movementlab-walk-v01
```

## First Windows test

Extract `artifacts/MovementLab_ArmLift_Test.zip`. Copy its `TestAnimations`
folder into `D:\DayZProjects\MovementLabWorkbench`.

Open the included `.blend` in Blender 4.3.2 and press Space to play the arm-lift
loop. This step needs no addon installation.

Then restart DayZ Workbench through the configured shortcut. In the **main
Workbench window**, expand **Game Root → MovementLabWorkbench → TestAnimations**.
The bundle contains TXA source and ANM import metadata, but no compiled ANM.
Opening the ANM entry in Animation Editor does not perform the import.

Right-click the `.txa` source and choose **Register resource and import** if
that action is offered. For an already registered resource, use **Reimport
Resource**. If the browser shows only the virtual `.anm` entry, use its
**Reimport Resource** action. The user confirmed that reimporting created the
ANM file, and subsequent assignment confirmed Animation Editor playback.

After import, check for a nonempty `MovementLab_ArmLift_Test.anm` next to the
source. If no ANM is produced, capture the **main Workbench console** and the
resource's context menu. Metadata alone can make the browser list an ANM that
does not yet exist on disk.

## Preview the compiled clip

[Download the separate editor preview workspace](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Editor_Preview.zip).
Copy its two files into the existing `TestAnimations` folder. In Animation
Editor use **Workspace → Open** and select `MovementLab_ArmLift_Preview.aw`.
The user confirmed that this preview instance plays the original arm-lift clip
after selecting a walking cell and using **Set Anim**.

Select the **MovementLab_ArmLift_Preview** instance. Pick an assigned walking
cell in **Anim Sets**, then select the compiled test ANM in the editor's **File
Browser** and click **Set Anim**. Press Play to test the clip. The new instance
inherits the vanilla assignments, so edits belong to the separate preview ASI.
The template and graph stay references to the existing extracted resources.
See the preview ZIP's README for the complete steps and expected result.
Filtering `walk` alone shows inherited DayZ slots; it does not assign the
arm-lift test. This test keeps the feet still and lifts the right arm over a
four-second loop.

If manual assignment is difficult, [download the local preview helper](https://github.com/SegWai/Modding-/raw/refs/heads/main/tools/create_bound_preview.ps1).
Open it in Notepad, inspect it, and copy its contents into Windows PowerShell.
It reads walking assignments from the installed `player_main.asi` and creates
`MovementLab_ArmLift_Bound.asi` and `.aw` beside the compiled animation, with
the test already assigned. Open that new workspace, select its instance, and
use the exact filter printed by the helper to select an animation cell and
press Play. The helper preserves existing files and stops without writing if
it cannot find walking assignments. It has not been executed in Windows or
validated in DayZ Tools here.

Do not assign this clip to the existing player workspace yet. That workspace
still references extracted vanilla animation instances and templates. A separate
test instance is needed before saving edited assignments or testing in-game.

The existing `player_main_preview.aw` omits the unavailable event table only
for editor preview. It is not a gameplay-ready replacement workspace. The
earlier `MeshParam` messages remain unresolved, although existing clip playback
works.

## Offline in-game diagnostic

The local setup report confirms standing greeting slots
`Gesture.SaluteErc.In`, `.Loop`, and `.Out`, and the diagnostic executable at
`D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe`.
The user has DayZ and DayZ Tools installed. The supplied baseline mission now
works on their PC; no additional offline-mode installation was needed.

[Download the offline test sources and launchers](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Offline_Test.zip).
Extract into `D:\DayZProjects`, producing `MovementLabOfflineTest`. With Steam
running and DayZ closed, open **Launch-Baseline.cmd**. Check that a character
loads and can move, then stand upright with empty hands and press **F6** for
the original greeting. The user confirmed all of these baseline checks passed.
The baseline loads no animation mod.

After the baseline works, **Prepare-Animation.cmd** copies the already compiled
arm-lift ANM into the new source folder, preserving a different existing file.
Pack `MovementLabOfflineTest\MovementLabRuntimeTest` with Addon Builder to
the destination **directory** `MovementLabOfflineTest\@MovementLabRuntimeTest\Addons`,
with prefix `MovementLabRuntimeTest`, including `.c`, `.asi`, and `.anm` files.
The resulting file should be `Addons\MovementLabRuntimeTest.pbo`. The installed
Addon Builder treated a destination ending in `.pbo` as an extra directory;
use the folder only. The user's actual extraction root is
`D:\DayZProjects\MovementLab_Offline_Test\MovementLabOfflineTest`, so all packing
paths must be based on that root. The launchers already resolve their own folder.
The ZIP's README gives the packing details. Use **Launch-With-Mod.cmd** and **F1** to
test the arm-lift greeting. The runtime ASI overrides only
`Gesture.SaluteErc.Loop`, retaining the vanilla greeting's entry/exit phases.

The practice mission creates one character without an economy or character
persistence. Separate baseline and mod profile folders retain logs for
diagnosis. The user confirmed native mission compilation, packing, and custom
animation playback on F1. F6 remains a separate mission diagnostic trigger;
the reason for the observed difference between the keys has not been established.
Rebuild the ZIP with `python tools/package_runtime_test.py`.

File-presence checks must use `Test-Path -PathType Leaf`; a plain `Test-Path`
also accepts folders. The launcher explicitly rejects a directory at its
expected PBO path. Preserve mistaken build-output directories outside the mod
before copying the actual file into place.

The child ASI uses `ModItemRegisterCallbacks.RegisterEmptyHanded` and
`DayZPlayerType.SetDefaultItemInHandsProfile` without replacing the player graph.
This test confirms the original clip can play through that profile. It does not
establish compatibility with other mods or multiplayer, or replacement of the
locomotion controller. The user confirmed movement resumes after the gesture
and observed no distortion. The walking study above is the next separate test.

Reference: [official DayZ 1.29 scripts](https://github.com/BohemiaInteractive/DayZ-Script-Diff/tree/86974a0f5bd16b1ee3e334ad828133c93dca80a1),
build 1.29.163709, scripts revision 125372.

## Reproduce the cloud export

Run `bash tools/setup-cloud.sh` to prepare the pinned reference dependency.
The cloud image already provides Blender 4.3.2; the helper verifies that version.

```sh
BLENDER_USER_CONFIG=/tmp/dayz-local-workbench/blender-config \
BLENDER_USER_EXTENSIONS=/tmp/dayz-local-workbench/blender-extensions \
blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python tools/build_diagnostic_clip.py -- \
  --rig /tmp/dayz-local-workbench/dayz_reference_rig.blend \
  --addon-root /tmp/dayz-animation-plugin/BlenderPlugin \
  --output /tmp/movementlab-export-check
```

The addon export function runs in headless Blender without registering the
addon. Its current importer uses a newer Action API; this experiment does not
claim that the complete addon is compatible with Blender 4.3.2.

Reference rig and exporter:
[DayZAnimationPluginDemo](https://github.com/jdfnc24/DayZAnimationPluginDemo),
commit `7075310c8aa3ae75f9487168577661809e5caa15`.
The official character-rig reference is
[BohemiaInteractive/DayZ-Misc](https://github.com/BohemiaInteractive/DayZ-Misc).
See the asset notices inside the test bundle before redistributing its rig or
mesh. No Rockstar animation assets are included.
