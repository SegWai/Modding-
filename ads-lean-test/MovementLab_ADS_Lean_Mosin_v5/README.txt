MOVEMENTLAB MOSIN ADS LEAN v5 - BALANCE / WALK / CROUCH / DEMO

NEW IN v5
1. Full left/right central-body targets are symmetric about neutral. Authoring
   head displacement is +/-0.317630 m and chest displacement +/-0.159135 m.
   Pelvis displacement is +/-0.08 m; vertical/depth offsets match on both sides.
   The rifle remains right-handed. Exact rendered exposure, collision limits,
   aim sway and first-person camera balance still need game comparison.
2. Custom ADS lean is connected to all four branches: standing idle, standing
   walking, crouched idle and crouched walking. The old default tilt is gated
   out in each branch while custom mode is active. Walking retains native
   footsteps/foot IK, combined with our pelvis/torso/arm lean corrections.
3. One red-hoodie Mosin demo actor walks about 2 m to each side of its starting
   point (about 4 m end-to-end). It leans and turns its aim toward travel.
   Its movement uses native walk input and measured endpoints; it never
   teleports between endpoints. Native filters can cause slight overshoot.
   The demo uses the same MLADSLeanAmount, gate and graph branches as you.
4. Crouching uses the same torso/arm correction with the lateral hip offset
   transferred to the lower spine. Its pelvis/legs are left in the native
   crouch pose. One final weapon IK roll expression supplies a common signed
   8-degree cant target for all supported states, mirrored by lean direction.
   Actual native roll interpretation and sight alignment require testing.

RUN
Close DayZ, start Steam, extract the entire ZIP into a NEW folder, and run
Launch-Mosin-Lean-Test.cmd. Choose 1 for custom mode. Do not combine this with
older test PBOs or SNAFU. The project reference remains F:\DayZProjects.
Default game directory is D:\SteamLibrary\steamapps\common\DayZ; the launcher
asks for the correct directory if DayZDiag_x64.exe is not found there.
No extraction or preparation of the original animation library is required.

TEST CONTROLS
Q/E + ADS: your normal left/right lean, now active standing, walking or crouching.
F7: custom/native comparison (also applies to the demo).
F8: third-person inspection with the Mosin raised, without entering ADS.
F9: logs your status/joints/exposure offsets and the demo's joints.
F10: pause/resume demo walking; its aim/lean remain visible while paused.
The demo is about 8 m in front of the original spawn and wears a red hoodie.
It is an invulnerable visual test actor, not a combat AI, and does not fire.
Your Mosin is loaded; the PU optic is in your bag.

BALANCE CHECK
On flat ground, stand still in ADS without leaning and press F9 once to record
neutral head/chest X. Hold left lean until settled, press F9; repeat on right.
The log prints signed offsets from that neutral sample. Send the collected
logs and a front view of both sides so we can verify the actual native result.
Those neutral offsets apply to standing-idle comparison; capture neutral again
when changing the setup. Walking/crouch samples also contain native gait/sway.

CHECK THE OTHER REQUESTS
Walk forward/back/sideways while ADS + leaning. Confirm the upper-body pose
stays custom while the feet take real steps. Crouch and repeat stationary,
then crouch-walk. Compare the rifle roll and sight alignment in each state.
Watch the red NPC traverse both directions; F10 lets you inspect a stopped
endpoint. F9 captures NPC status/joint data too. It blends through reversal.

IF SOMETHING FAILS
Press F9 and run Collect-Logs.cmd. Send the resulting ZIP and a short video.
If custom mode fails at startup, launcher option 2 uses the native workspace
with the same test mission. It cannot show the custom pose without its graph.
The v2 multiline controls, distinct binding validation and offline debug-plugin
registration are retained. Writes to animation variables remain inside each
actor's CommandHandler. Native player input/aim are not overridden by NPC input.

SCOPE AND LIMITS
This is an offline Mosin test for the local player and designated demo actor.
Prone and unsupported actions remain native. Moving ADS supports the native
walking/raised-movement states, with the native foot solver kept for gait.
The authored balance is symmetric at full lean to float precision; offline
interpolation checks allow less than 1 mm of central-body asymmetry. Native
Mosin IK, cover collision and camera may change the rendered result.
The static standing wide-leg pose releases foot pinning as in v3; test flat
ground first because feet may float/clip on uneven terrain at full lean.
The crouch adaptation and shared weapon roll need native verification.
The demo's native steering, ADS presentation and endpoint overshoot need a
local playtest. No game engine or Enforce compiler ran in this cloud task.

DISK SPACE / FILES
Only two small PBOs and current source/test metadata are included. No original
animation library is copied. Nothing is written to the game or project root.
Logs and any native crash dumps live in this test folder's Profiles\LeanMosin.
Collect-Logs excludes large memory dumps. Back up useful logs, then remove this
test folder when done. Other projects and previous tests are not deleted.
See validation.json, Mode-Coverage.json and Symmetry-Measurements.json for the
checks actually run and the distinction between authoring and native results.
