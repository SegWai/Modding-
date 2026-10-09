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
- The user reports that Workbench produced `MovementLab_ArmLift_Test.anm`
  after reimporting the TXA. Playing this compiled clip in Animation Editor is
  the next check.
- Blender 4.3.2 here authors and exports an original four-second arm-lift test
  as TXA. Checks cover frame ranges, bone names against the authoring rig,
  finite transforms, normalized rotations, stationary feet, and matching loop
  endpoints. Rendered start and middle poses were inspected.

Animation Editor playback and in-game playback of the original clip are pending.
Replacing the locomotion controller, aiming, combat, and multiplayer behavior
remain unproven. This test is an import diagnostic, not the intended final gait.

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
ANM file; its contents and native playback still need verification.

After import, check for a nonempty `MovementLab_ArmLift_Test.anm` next to the
source. If no ANM is produced, capture the **main Workbench console** and the
resource's context menu. Metadata alone can make the browser list an ANM that
does not yet exist on disk.

## Preview the compiled clip

[Download the separate editor preview workspace](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Editor_Preview.zip).
Copy its two files into the existing `TestAnimations` folder. In Animation
Editor use **Workspace → Open** and select `MovementLab_ArmLift_Preview.aw`.
The user reports selecting this preview instance, but the original clip has
not yet been confirmed playing in it.

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
