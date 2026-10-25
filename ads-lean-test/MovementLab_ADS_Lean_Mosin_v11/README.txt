MOVEMENTLAB MOSIN ADS LEAN v6 - BALANCE / WALK / CROUCH / DEMO

V6 COMPILE FIX / DIRECT LAUNCH
Your v5 logs show two calls to the nonexistent GetCommand_Weapons function.
Both now use the official Human.GetCommandModifier_Weapons API. The animation
graph and pose data are unchanged. The batch and PowerShell launchers start
the custom test directly, without numbered choices. Mode toggles are in-game:
F7 native/custom, F8 inspection, F9 measurements, F10 pause/resume the NPC.
Numbered menus remain specific to the separate FPS graphics helper.
Native compilation/playback of this fix still needs your local DayZ test.

FEATURES RETAINED FROM v5
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
Launch-Mosin-Lean-Test.cmd. It starts the custom test directly. Do not combine this with
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
If startup fails, run Collect-Logs.cmd and send the ZIP. There is no batch
mode-selection menu; F7 is the native/custom toggle after the game starts.
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

V7 NPC correction: v6 runtime logs showed graph=true/gate=1 but stance=0 (unraised). The offline demo now locks the native move command to raised erect, releases that lock on stop, and logs actual native ADS/raise state separately from its ADS request. Pose targets, weapon roll and animation graph are unchanged. Native playback still needs an in-game check.

V8: Split the status message into short statements to resolve the reported line-204 Formula too complex compile error. No animation or gameplay change from v7. Windows DayZ compile/playback still requires an in-game test.

V9 NPC input revision (video review): the demo no longer forces AimX/AimIKX to +/-90 degrees while side-stepping. It keeps the rifle forward with AimX=0/AimIKX=0 and sets the native ArmIK aim/right-hand/left-hand bits (7), only on the designated offline NPC. It defaults to normal movement input 2 and remembers the selected player's most recent moving raised-Mosin ADS/inspection gait (1 or 2); stand still to watch it retain that gait. Native locomotion still controls actual speed and foot placement. F10 pauses/resumes it. Player input, pose targets, graph and shared weapon roll are unchanged. This addresses the demo input differences seen in the video; native playback and any remaining sliding/ghosting need a new in-game check.

V10 runtime-backed correction: v9 logs alternated stance 0/3 every few milliseconds, always raise_complete=false. The demo now issues its persistent raised stance lock once per move-command start, removes the competing raise override, and waits at speed 0 until the real native weapon raise completes. Its ADS/IK and patrol are enabled only when genuinely ready. Default gait is walk (1), then follows measured player ADS gait. Periodic diagnostics include raise transition count and position, without per-frame state-change spam. The shared pose, graph and player controls are unchanged. Native playback requires a new game test; do not assume local checks prove the stance is stable.

V11: v10 log shows one transient raise (two transitions), then persistent stance=0/raise_complete=false. Restore OverrideRaise(ENABLED,true) ONCE in the same guarded startup block as the single stance request. ENABLED is documented to persist until disabled; no per-frame reinitialization. Cleanup disables it. The genuine weapon-raise readiness gate remains, and successful raise completion is now logged explicitly. Periodic diagnostics include the native raise input and stance-transition status. Pose, graph, player input and locomotion speed policy are unchanged. Requires native DayZ test; no timeout starts an unready patrol.
