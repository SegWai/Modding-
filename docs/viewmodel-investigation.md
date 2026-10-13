# Separate first-person viewmodel investigation

The requested behavior is a camera-fixed gun-and-arms presentation, independent
of the real character's aim/turn animation. Revision49 remains intact. Earlier
camera-angle experiments did not provide this and were rolled back after video
showed major weapon/view separation.

## Verified interfaces

The checked DayZ script SDK exposes `PlayerPreviewWidget.SetPlayer`,
`UpdateItemInHands`, `GetDummyPlayer`, `SetModelOrientation`, and
`SetModelPosition`. The native inventory player preview uses these and modifies
its dummy's animation additives independently of the real player. The native
`MasterInventoryState` uses `InventoryIK`/`InventoryIdleG`. Its existing
`APoseSrc` is a fixed frame of `Locomotion.ErcRas.Idle`.

`Camera.GetCurrentCamera()` explicitly does not return the player camera. A
camera-child entity attachment cannot therefore be assumed. Generic entity
camera masks are exposed but their applicability to DayZ's RV player rendering
and camera indices is not established. There is no demonstrated dedicated
first-person-viewmodel layer in these sources.

GUI syntax was checked against public community layouts, including
PlayerPreviewWidgetClass in DayZ Expansion's player-profile layout. Only native
API names and layout grammar were used; the prototype has its own layout/code
and does not require those mods or redistribute their assets.

## Prototype v1

`viewmodel-prototype/MovementLabViewmodelPrototype_v1` is based on Revision49.
F9 enables a separate PlayerPreviewWidget; F10 cycles close/closer/wide framing.
It starts disabled and remains offline only.

The widget receives the current player/equipment and owns the preview dummy.
Its orientation stays fixed; it never reads the mouse for rotation. A new graph
variable defaults to zero everywhere, preserving native inventory preview.
Only the verified independent dummy gets the value1, selecting the existing
fixed aiming pose in Master.agr. Dummy aim axes are zero; the real player's
animation variables, camera and movement inputs are untouched.

Only after a widget, independent dummy and pose binding are present does the
prototype locally hide the real body, hand proxy and sleeve/glove/vest items.
Exits restore what it hid. Missing renderer/binding retains native view.
No world NPC, weapon, player or inventory item is created by the script.

This is a rendering proof, not a finished production viewmodel. Native pixels,
framing, alpha/lighting, pose/grip, performance, visibility and shooting with
the real proxy hidden require the Windows DayZ test. Native weapon actions,
ADS, free-look, obstruction and third person use the original view; separate
reload/fire animation synchronization is not implemented.

## Validation and limits

### Native test result: full body instead of arms

The user reports that enabling the preview while aiming displays the character's
full body, rather than a first-person arms view. This is a failed viewmodel test:
the widget renders an inventory avatar, not an arms-only first-person layer.
The mock tests above cannot establish framing or model visibility.

The exposed PlayerPreviewWidget interface has no arms-only or first-person LOD
selector. EntityAI.HideSelection requires named hide animations configured in
both config and models.cfg; arbitrary body/legs names are not a verified fix.
The available reference Blender file contains one full-body zMale_body mesh
(8,424 vertices) and an armature, not a ready-to-use arms-only DayZ model.
There is no verified native arms-only P3D/preview integration in this prototype.
Do not treat closer framing or an undocumented fixed LOD index as a solution.

Keep F9 disabled to retain the original view. A subsequent renderer attempt
needs an arms-only model and a verified DayZ model/weapon-proxy integration,
followed by a native rendering test, before hiding the actual player view.

`tools/check_viewmodel_prototype_v1.py` executes unchanged movement regressions
and the actual UI controller translated to C++ with renderer/player mocks.
It verifies independent dummy ownership, fixed pose writes, no real-player
animation writes, cached setup, visibility recovery, missing renderer/binding
fallback, delayed binding recovery, framing and shutdown. Graph checks preserve
the entire native Master resource except the one guarded inventory-pose branch.
The current prototype does not prove native rendering or native compilation.

Launch with Launch-Movement-Test.cmd in a fresh folder. In first person, hold
RMB for hip aim, press F9 and turn. If close framing is empty or badly cropped,
F10's wide preset verifies the dummy renderer. F9 restores native view. Capture
screens/video and MovementLab-Viewmodel-Prototype-v1-Logs.zip for the remaining
native questions.

## Arms-only renderer test v2

`viewmodel-prototype/MovementLabArmsOnlyTest_v2` replaces the full-body avatar
widget with two ItemPreviewWidgets. The first renders a new, static arms-only
MLOD model; the second renders the real held weapon's native inventory preview.
Neither orientation reads mouse/camera rotation. The v1 inventory graph marker
and Master override have been removed from this test. Revision49 World movement,
camera, aiming, recoil and sway scripts are byte-identical.

The reference Blender mesh was cut using arm/forearm/hand weights and posed with
two-segment arm transforms. The baked model contains 4,522 vertices and 7,974
faces; no torso/head/leg geometry remains. Blender export/reimport preserved those
counts. The importer's viewport collection visibility helper was bypassed only
because it requires an interactive UI; binary parsing and geometry import ran.
ArmAToolbox export/import commit: 016c9b8f30f8a9da3fb53b2afb2b28cbff7c057e.
Reference mesh attribution and DayZ-only ADPL-SA terms are in ModelSource.

This is an uncalibrated static rendering diagnostic. Two item-preview cameras
do not share scene depth, and there is no verified first-person camera calibration
or matching hand grip. Action animation mirroring is not implemented; ADS and
weapon actions return to the original view. MLOD acceptance and rendered output
must be checked in DayZDiag. Do not call this a completed FPS viewmodel.

The test creates one local, nonpersistent, non-simulating diagnostic arms item
far below the world, not a character. Shutdown clears widget item references
before deleting only that owned fixture. The C++ controller checks cover cached
setup, creation failure, widget/item failure, visibility restoration, ownership,
F9/F10 and deletion. The native renderer and Enforce compiler were not run.

The user additionally requested SNAFU weapons/gear and five full spare magazines.
They confirmed only SNAFU Weapons is installed. The launcher resolves that external
Workshop mod, and the mission scans its loaded public weapon configs for rifle,
sniper, SMG and pistol names and compatible magazine lists. Each receives one
loaded magazine and five full spares; all loose ammunition spawning is removed.
No pack assets or invented class names are included. Gear remains the existing
black native kit; no separate SNAFU gear pack is identified. The bag's cargo is
expanded for the magazine-only loadout. Native class recognition is unverified
until the installed pack is run locally, and missing roles are logged.
