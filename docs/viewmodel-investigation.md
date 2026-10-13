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
