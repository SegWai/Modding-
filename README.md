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
- Blender 4.3.2 here authors and exports an original four-second arm-lift test
  as TXA. Checks cover frame ranges, bone names against the authoring rig,
  finite transforms, normalized rotations, stationary feet, and matching loop
  endpoints. Rendered start and middle poses were inspected.

Workbench compilation and in-game playback of the original clip are pending.
Replacing the locomotion controller, aiming, combat, and multiplayer behavior
remain unproven. This test is an import diagnostic, not the intended final gait.

## First Windows test

Extract `artifacts/MovementLab_ArmLift_Test.zip`. Copy its `TestAnimations`
folder into `D:\DayZProjects\MovementLabWorkbench`.

Open the included `.blend` in Blender 4.3.2 and press Space to play the arm-lift
loop. This step needs no addon installation.

Then restart DayZ Workbench through the configured shortcut. In its resource
browser, expand **Game Root → MovementLabWorkbench → TestAnimations**. The TXA
and its ANM import metadata are supplied. Select the test resource and report
whether Workbench imports it or displays an error. Its exact import action is
still to be verified on the user's installed Workbench.

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
