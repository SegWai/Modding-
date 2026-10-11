## Current best version: Crouch Wheel Six Levels v4

User approved this version on 2026-10-11 as the best version so far.
Use `ctrl-mode-test/MovementLabCrouchWheel_SixLevels_v4/` as the baseline for
future changes. Preserve its source, ZIP and research/version history; package
future experiments separately.

[Download the preserved v4 package](https://github.com/SegWai/Modding-/raw/1eb9e67/artifacts/MovementLab_Crouch_Wheel_Six_Levels_v4.zip).

## Separate test: standing walking at half pace

[Download F8 walking comparison](artifacts/MovementLab_Standing_Walk_Half_Speed_Test_v1.zip).
Approved Six Levels v4 remains the baseline. Extract the entire test separately,
run `Launch-Movement-Test.cmd`, and use Ctrl to select walking. F8 OFF (default)
uses native walking; F8 ON selects six separate 15 FPS standing walk variants
instead of original 30 FPS clips. Root-motion displacement per frame is retained,
targeting half pace and travel speed together. Jog/sprint and crouch assets and
all existing movement methods are preserved. Walking portions of start/stop
blends also use the selected pace. Toggle at rest for clean comparisons; switching
clips mid-step can cause a one-time phase change. Native compilation and actual
travel speed require the user's DayZ test. Local translated controller and
schema/package checks pass. This test does not yet add standing scroll levels.

## Six-level v4: consistent Shift fast crouch

[Download six-level v4](artifacts/MovementLab_Crouch_Wheel_Six_Levels_v4.zip).
User confirmed v3 entry defaults work but held Shift sometimes stays at60%.
V4 explicitly requests native fast gait while crouched with Shift and directional
input, matching the wheel-native request. Saved defaults, speed tiers and all
animation assets unchanged. User subsequently approved v4 as the current best version.

## Six-level v3: crouch entry defaults

[Download six-level v3](artifacts/MovementLab_Crouch_Wheel_Six_Levels_v3.zip).
Every new crouch entry defaults to60% from walking/jogging/idle, regardless of
previous wheel choice. Entry after achieved full standing sprint selects native
fast crouch. Existing Shift override, standing/crouch-exit rules and87%-native
handoff retained. Extract fresh and launch. Local checks pass; native confirmation
pending. Earlier packages remain unchanged.

## Six-level v2: 87% to native source handoff test

[Download six-level v2](artifacts/MovementLab_Crouch_Wheel_Six_Levels_v2.zip).
Uploaded excerpt shows a lingering step during the fast-gait handoff. V2 changes
only the selector's level6 connection to retain level5's26FPS walk source while
native gait builds; unchanged original fast-crouch clips remain its endpoint.
Speeds/controller/timers unchanged. Extract fresh and launch. Local checks pass;
native visual outcome pending.

## Six selectable crouch speeds: new test

[Download six-level test](artifacts/MovementLab_Crouch_Wheel_Six_Levels.zip).
Levels:30%,approximately47%,60%,approximately73%,approximately87%,native fast
crouch. Extract fresh, close DayZ, keep Steam running and run
`Launch-Movement-Test.cmd`. Uses v1 controller rules without momentum/hidden/F8
experiments, plus the separate-column animation schema repair. Local checks
pass; native test pending. Original user-confirmed v1 remains unchanged.

## Crouch wheel v8: repair confirmed animation-table errors

[Download v8](artifacts/MovementLab_Crouch_Wheel_Test_v8.zip). Uploaded v7 RPT
contains missing animation-source IDs and an invalid native Locomotion column.
V8 restores that original column, moves extra speeds into a separate column,
corrects hidden mapping block placement and routes level5 through the native
Cro subtree directly. Extract fresh and run `Launch-Movement-Test.cmd`;
check level5 with F8 OFF first, then the hidden transition with F8 ON.
Native runtime outcome pending; local schema/controller checks pass.

## Crouch wheel v7: freeze isolation with exact v1 control

[Download v7](artifacts/MovementLab_Crouch_Wheel_Test_v7.zip). V6 was also reported
frozen at native speed with both toggle states. V7 removes every added selector
wrapper and preserves original group order. First run
`Launch-Known-Working-v1.cmd` (isolated exact v1 copy), then close DayZ and run
`Launch-Movement-Test.cmd` (v7, F8 OFF initially). Native result pending. If v7
still freezes, `Collect-Logs.cmd` creates an archive for diagnosis.

## Crouch wheel v6: native-speed freeze correction test

[Download v6](artifacts/MovementLab_Crouch_Wheel_Test_v6.zip). V5 was reported
frozen at native speed with F8 OFF and ON. V6 removes the experimental timed
selectors, restores working v1 wheel selection and retains a separate F8 hidden
stage comparison. Extract fresh, launch and test level5 with F8 OFF first.
Native visual correction is pending; original v1 remains available unchanged.

## Crouch wheel v5: hidden 90% comparison

[Download v5](artifacts/MovementLab_Crouch_Wheel_Test_v5.zip). Extract into a fresh
folder and run `Launch-Movement-Test.cmd`. **F8 OFF** (default) compares the v4
behavior; **F8 ON** inserts a brief automatic hidden 90% slow-crouch clip stage
when scrolling downward from level 5. Five selectable levels remain unchanged;
upward scrolling never triggers the hidden stage. Native visual result pending.

## Experimental crouch wheel v4: timed animation blends

[Download v4](artifacts/MovementLab_Crouch_Wheel_Test_v4.zip). Extract the entire
ZIP into a fresh folder, close DayZ, keep Steam running and run
`Launch-Movement-Test.cmd`. This separate experiment adds timed pose transitions
between wheel tiers. Native visual result is pending; v1 remains the approved
working version below. See [investigation](docs/crouch-wheel-timing-investigation.md).

# MovementLab

DayZ remains the base game. The goal is original player animations and movement
inspired by the weight and pacing of Red Dead Redemption 2.

## Working crouch wheel version: v1

[Download working crouch wheel v1](https://github.com/SegWai/Modding-/raw/6a17a24/artifacts/MovementLab_Crouch_Wheel_Test_v1.zip).

The user confirmed this version works. Keep `ctrl-mode-test/MovementLabCrouchWheel_v1/`
and its ZIP unchanged. Subsequent wheel momentum v2/v3 tests were rejected for
jumping animations. Continue using v1 while investigating continuous playback
and phase-preserving transitions. See [timing findings](docs/crouch-wheel-timing-investigation.md).

## Historical approved standing baseline: v10 Strafe Test v2

[Download the stable version](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Ctrl_Modes_v10_Strafe_Test_v2.zip).

The user previously approved v10 Strafe Test v2 as the stable standing version.
The current combined movement baseline is Six Levels v4, listed above.
The approved ZIP remains unchanged.

This retains original v10's stronger jog-to-walk momentum, Ctrl modes,
Shift sprint, permanent responsive turning and crouch rules. Abrupt pure
A/D reversals request near-stop movement; repeated reversals keep it slow.
Holding one direction for more than 0.30 seconds starts a short smooth
recovery, while releasing all movement lets the character stop normally.
F8 is absent.

Original Ctrl Modes v10 remains a fallback. The v11–v13 reversal experiments
and v10 Strafe Test v1 are superseded historical tests, not the stable baseline.

## Later walk entry with stronger jog-to-walk momentum

[Download Ctrl Modes v10 later walk blend](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Ctrl_Modes_v10_Later_Walk_Blend.zip).

After Ctrl from achieved full jogging, keep moving jogging for about 0.12s,
then blend toward walking over 0.30s. The total remains 0.42s. Native animation
continues playing; no frame freeze or extra walking tail. Other movement,
permanent responsive turning and crouch rules remain from v9. Extract fresh
and run the launcher. Actual translated checks match v9's completion deadline
and pass standing/crouch regressions. Visual blending requires the game test.

## Jog-to-walk momentum without extending the transition

[Download Ctrl Modes v9 jog-to-walk momentum](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Ctrl_Modes_v9_Jog_Walk_Momentum.zip).

Ctrl jog-to-walk now retains more momentum early and eases into walking with
the same transition deadline. No pause or additional walking tail. Permanent
responsive body rotation, crouch rules and other stopping curves remain from
v8. Extract fresh and run the launcher. Actual translated checks pass at
30/60/144 FPS, including differential duration/completion comparisons to v8.
Native visual blending still requires the game test.

## Blender controller timing illustration: v8 versus v9

[Watch/download the before-and-after MP4](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Jog_Walk_Before_After_Illustration.mp4).
[Editable Blender 4.3.2 scene](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Jog_Walk_Controller_Comparison.blend).

This illustrates the actual requested-gait curves at 4x slower playback. It
is **not DayZ character animation footage or a physical velocity simulation**.
Both transitions are 0.42 seconds for achieved forward gait 2. At halfway,
v8 requests 1.25 and v9 requests 1.50 (gait units). Native in-game blending
can make the difference subtle; Blender cannot reproduce the DayZ controller.
The script `tools/render_jog_walk_curve_comparison.py` renders the illustration.
No mod behavior is changed by these video/scene artifacts.

## Permanent preferred body rotation with v7 crouch rules

[Download Ctrl Modes v8 fixed turning](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Ctrl_Modes_v8_Fixed_Turning.zip).

The preferred responsive body rotation (former F8-on setting) is permanently
selected. The F8 toggle is removed. Direction response, sprint settings and
all v7 standing/crouch logic are retained. Extract fresh and run the launcher.
Actual translated filter outputs match v7 responsive mode; movement source
matches tested v7. Native validation requires the in-game test.

## Four crouch rules rebuilt directly from v4

[Download Ctrl Modes v7 crouch rules](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Ctrl_Modes_v7_Crouch_Rules.zip).

This update starts from the approved v4 source, excluding the rejected v5/v6
crouch experiments. Crouch without Shift is slow; Shift+direction uses native
DayZ fast crouch. Standing from active fast crouch selects persistent jogging,
consuming that existing Shift hold so it does not immediately sprint. Release
and press Shift again for normal standing sprint. Standing from slow crouch
preserves the previous standing walk/jog mode. Ctrl still toggles while standing.
Standing v4 timings, body-turn comparison and direction fixes are retained.
Extract fresh and run the included launcher. Mocked tests cover the four rules
and standing regressions; native compilation/visual validation requires DayZ.

## Stable movement test: v11

[Download stable movement test v11](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Movement_Logic_Test_v11.zip).
Extract the ZIP and open `Launch-Movement-Test.cmd`. Steam must be running and
DayZ closed. No animation import or PBO build is required. **F7** switches
between heavier movement with sprint braking and vanilla filters in the same
offline session. V11 is the historical baseline; the later reversal and walking-first controls
tests have been removed. Extract this ZIP into a fresh folder and use its launcher.

The user approved v11 walking starts and directional stopping behavior.
V11 retains the agreed stopping time with a longer jogging phase and a shorter
walking finish. The tested startup PBO remains included. This is the original
v11 package, without the later reversal additions.
Implementation and evidence are in [the API notes](movement-logic-test/MovementLabMovementLogicTest/API_NOTES.md).

## Ctrl walking/jogging toggle test

[Download Ctrl Modes v2](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Ctrl_Modes_v2.zip).

Built directly from v11: tap Ctrl to toggle walking/jogging, hold Shift to
sprint, release Shift to return to the pre-sprint mode. Releasing all movement
retains v11's sprint/jog/walk stop phases and direction. Sprint-to-walk follows
the same stopping curve down to walking, then keeps walking (including
partial sprint). Original v11 remains
unchanged. Extract fresh and run `Launch-Movement-Test.cmd`; F7 compares
against vanilla. Mocked checks include tick-for-tick v11 sprint/jog stop
comparisons. Native compilation and animation blending need local testing.

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

## Walk/jog turning comparison on Ctrl Modes v2

[Download Ctrl Modes v3 turning A/B](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Ctrl_Modes_v3_Turning_AB.zip).

Starts with the original v2 turning. Press F8 to switch to more responsive
walk/jog turning (native direction/heading delay multipliers 1.6 instead of
2.5), then press again to restore v2. F7 retains the separate vanilla comparison.
Extract fresh and run `Launch-Movement-Test.cmd`; Ctrl/Shift controls and all
startup/stopping curves are retained. Sprint filters are unchanged. Actual
translated filter/toggle checks and movement regression checks passed; native
turn arcs and animation behavior need the in-game comparison. Stable v2 stays
available above. The isolated walk-blend experiment is not included.

## Rear-diagonal direction fix with body-only turning comparison

[Download Ctrl Modes v4 direction fix](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Ctrl_Modes_v4_Direction_Fix.zip).

Fixes startup re-entry during continuous turn/backward gait dips, repeated
mode-return braking and stale angle ownership while steering. F8 now changes
only body heading delay; movement-direction filtering stays identical between
A/B modes. Existing Ctrl/Shift controls and v11 timing budgets are retained.
Extract fresh and run `Launch-Movement-Test.cmd`. Test slow camera/directional
turns into S+A and S+D in walking and jogging. Previous v3 fails the added
sustained-input regression; v4 passes. Mocked movement/filter checks passed;
actual paths and animation stability require the local DayZ test.

## Isolated jog-to-walk blend experiment

[Download the standalone jog-to-walk blend test v1](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Jog_Walk_Blend_Test_v1.zip).

Extract fresh and run `Launch-Movement-Test.cmd`. Use ordinary DayZ controls:
hold W to jog, then hold Ctrl while keeping W pressed to walk. This single
experiment eases the gait-speed request into walking over 0.45 seconds;
F7 compares vanilla. It includes none of the v11 startup, braking, heavy
filters or persistent Ctrl modes. It does not independently set physical
velocity or clip playback rate. Mocked command-hook checks passed; native
compilation, visual blending and physics need the local game test.

## Walking reference revision v10

[Download walking revision v10](https://github.com/SegWai/Modding-/raw/refs/heads/main/artifacts/MovementLab_Unarmed_Walk_v10.zip).
Open `TestAnimations/MovementLab_Unarmed_Walk_v10.blend` in Blender 4.3.2 and
press Space. The default view is from the front, matching the new reference.
Rear, side and front GIF previews are also included.

This revision follows the user's reduced-bounce and closer-leg feedback on
v09. Pelvis vertical travel drops from 1.92 cm to 1.16 cm (about 39 percent),
by leveling its supporting-step height and letting the stance leg accommodate
it. The ankle track narrows from 20 to 16 cm. The lateral weight transfer is
retained exactly (9.06 cm pelvis travel), with the same support-side torso
lean/timing, shoulder/hip turns, inward forearm sweep, small head tilt and
wrist/finger pose. The forward/back foot path, raised toes, cadence, nearly
straight landing knees and delayed initial support flex are retained.

Hand-to-hip surface-distance checks pass at half frames on the unclothed
reference mesh; native clothing and pace/blend tests remain pending.
`walk-test-v10/reference_notes.json` records the revision's choices and limits.
Appearance still requires user review. No source video or frames are bundled.

Cloud checks cover matching endpoint poses, stationary root, reachable leg
targets, unchanged bone scales, the baked action against authored poses,
contact drift compensated for nominal travel, and deformed-mesh ground
clearance at integer and half frames. The TXA is parsed back and checked for
finite transforms, normalized rotations and all 152 nodes. Rendered poses
are inspected from behind, the front and side. Native Workbench compilation,
pace, footstep events and gameplay blends remain pending for this revision.
The working arm-lift runtime test is retained; judge the walk's appearance
before doing more game setup. Older walking ZIPs remain for comparison.

To reproduce after the existing cloud setup:

```sh
BLENDER_USER_CONFIG=/tmp/dayz-local-workbench/blender-config \
BLENDER_USER_EXTENSIONS=/tmp/dayz-local-workbench/blender-extensions \
blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python tools/build_walk_clip_v10.py -- \
  --rig /tmp/dayz-local-workbench/dayz_reference_rig.blend \
  --addon-root /tmp/dayz-animation-plugin/BlenderPlugin \
  --output /tmp/movementlab-walk-v10
for movementlab_view in front rear side; do
  BLENDER_USER_CONFIG=/tmp/dayz-local-workbench/blender-config \
  BLENDER_USER_EXTENSIONS=/tmp/dayz-local-workbench/blender-extensions \
  blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
    --python tools/render_walk_preview.py -- --output /tmp/movementlab-walk-v10 \
    --name MovementLab_Unarmed_Walk_v10 --view "$movementlab_view" --save-view front --straight-front
done
python tools/package_walk_test.py --generated /tmp/movementlab-walk-v10 --revision v10
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
