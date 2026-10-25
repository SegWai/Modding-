MOVEMENTLAB - MOSIN ADS LEAN - NATIVE TEST v4

This is a local calibration build from your approved Blender v6 pose, adapted
additively to DayZ's native Mosin aiming pose. V2 pose activation was confirmed by your in-game screenshot. V4 posture behavior
has not been verified in the native engine in this cloud environment. Do not install it into your normal mod set.

V4 LEFT-LEAN POSTURE REVISION
Only the left-lean authoring target changes. The opposite lean is retained.
The right elbow is brought down to shoulder height in the authoring model
(upper arm 90 degrees from vertical), while retaining the trigger-hand pose.
The right leg reaches about 9 cm farther sideways, its knee is straighter,
and its foot turns outward about 55 degrees relative to its old orientation.
The hips lower by another 4 cm to make room for the wider planted stance;
the left support leg adjusts to keep its foot on the ground. No limb scaling.
These are authoring measurements, not a claim of exact native joint angles.
While holding the LEFT lean, press F9. The log now records both leg joint
angles/positions and the right elbow/upper-arm angle from the actual game.
Send a front-view screenshot and Collect-Logs.cmd ZIP for the next calibration.
The v3 custom-lean foot-IK bypass, v2 working controls and all Mosin-only gates
are retained. Test flat ground before uneven terrain.

V3 LEG FIX RETAINED
The v2 graph applied the custom pose before IdleRasIK, which then solved the
legs back toward their original foot targets. V3 blends that foot solver out
only while the custom standing Q/E lean is active. At full lean the authored
leg corrections can reach their wide, extended stance. No bone is scaled.
At center, F7 native comparison, crouch/prone and moving branches, native foot
IK stays in place. Upper-body correction amounts and v2 activation logic are
unchanged. Test on flat ground first: custom full-lean feet no longer get this
terrain-adaptation pass and can float/clip on uneven ground. Native validation
of the new blend remains pending; please send a front-view video of both sides.

V2 FIXES RETAINED
DayZ rejected the v1 graph because MLADSLeanGate was undefined. V2 uses native
multiline control properties and a private control-template identifier.
A second canary control and distinct native bindings prevent an invalid graph
from being reported as active. Binding index zero remains allowed when valid.
F9 shows status; detailed eligibility is logged every two seconds.
The stock offline DayZDiag inventory debug plugins are registered with their
normal defaults when missing from non-debug public DIAG builds. This addresses
the null PluginInventoryDebug call seen during the inventory move in your logs.
The pose corrections themselves are unchanged from v1. V3 native playback
still requires a local test; offline checks cannot verify engine compilation.

RUN
1. Close DayZ and start Steam.
2. Extract this ZIP into a NEW folder, separate from older MovementLab tests.
3. Run Launch-Mosin-Lean-Test.cmd and choose 1.
   Default game folder: D:\SteamLibrary\steamapps\common\DayZ.
   If missing, the launcher asks for the game folder.
   Project reference: F:\DayZProjects. The launcher reads two source hashes
   when present, but the supplied PBOs are ready to test without repacking.
4. You spawn with a vanilla Mosin. The PU scope and extra ammo are in your bag.
5. Stand still, aim down sights, then use your normal Q/E lean controls.
6. F7 switches custom/native lean for comparison. Keep Q/E pressed while comparing.
7. F8 enables third-person inspection: raise the Mosin without ADS, use third
   person, and hold Q/E to inspect body/legs. F8 again restores ADS-only activation.
   Inspection is a pose preview on the raised pose, NOT proof of ADS alignment.
8. Test iron sights first, then attach the PU scope and repeat. Check both lean
   directions, return-to-center, sight alignment, feet, firing and bolt cycling.
9. Press F9 while ADS to see graph/gate and eligibility status.
10. Run Collect-Logs.cmd and send its ZIP plus a short video.

IF IT CRASHES
Close DayZ, run the launcher again and choose 2. This starts the same mission
and logic with the game's native workspace; the custom graph is not loaded.
If baseline works but custom does not, send logs from both attempts. Option 2
has no custom pose and F7/F8 cannot enable one without the patched workspace.

SCOPE
Custom gate: offline local player, Mosin9130, standing still, normal movement
command, raised weapon ready, ADS. Other guns, movement, crouch and prone keep
native lean. F8 deliberately relaxes ADS only for third-person inspection.
Native lean input and its blend are retained; entering/leaving the custom
ADS gate blends over about 0.18 seconds. F7 returns to native lean.
The current uploaded 1.30-era workspace is used, not v107's older overrides.
Only player_main.agr and locomotion.agf are patched. Native collision lean
amounts, all other graph branches, weapon animation instances, Mosin finger
poses, recoil, bolt cycling and native weapon IK are retained. Whether IK
changes the final arm pose must be checked in-game.

IMPORTANT LIMITS
This is a procedural adaptation, not a compiled exact ANM import. Blender
neutral-to-lean corrections affect 20 bones per direction. Their offline
rigid-transform math reconstructs the authoring poses, but native rotation
sign/order, pivots, pose propagation, camera motion and weapon alignment
remain unverified. Legs/arms may need calibration against native Mosin poses.
A narrow standing idle test is intentional; moving and crouched variants
will follow only after the first native result is reviewed.

DISK SPACE
The package contains two small PBOs, source patches and test helpers. It does
not build full copies of the original animation library. No changes are
written to F:\DayZProjects or the game installation. Runtime logs go only in
this package's Profiles\LeanMosin folder. Memory dumps can be large after a
crash; keep logs needed for diagnosis, then remove this test folder when done.
Original project data and other test folders are not automatically deleted.

ADVANCED
PowerShell: .\Launch-Test.ps1 -GameDir 'your game folder' -ProjectRoot 'F:\DayZProjects'
Add -NativeBaseline to bypass the graph. Do not add SNAFU or the old v107 PBOs.
Inspect Pose-Spec.json for conversion and math limits, Workspace-Provenance.json
for original source hashes, and validation.json for actual completed checks.
