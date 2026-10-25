Mosin lean v21 — shared walking posture and small head lift

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. No batch menu.

Standing aimed/leaning walk: reduce the custom pelvis drop from 12cm to 6cm on BOTH sides, letting the native walking foot IK extend the legs instead of keeping the pelvis so low. Native gait and foot IK remain. Stationary standing legs and explicitly crouched legs are unchanged. This naturally raises the upper body/head by about6cm compared with v20 while standing and moving.

Rightward aimed/leaning movement: add a small extra6mm neck/head lift on top of the posture change. Interprets the requested roughly3% as3% of a20cm head. The extra lift is weighted by right lean, movement and custom gate; it is zero at idle, left lean or native comparison. Prior right-lean side exposure and head rotation stay unchanged.

Both player and NPC use the EXACT SAME graph corrections and weights. No NPC-only pose adjustment. Naturally, matching visible frames also depends on matching stance, lean strength, gait and walk-cycle phase.

Hands, gun cant, scoped/suppressed unlimited-reserve Mosin, normal bolt cycle, ragdoll and one-second NPC respawn stay as in v20.
F10 pause/resume NPC. F8 third-person inspection. F6 head-tilt comparison; F7 full lean comparison; F9 measurements.

Test walking in both directions while aiming/leaning, on NPC and player. Check head height, straighter knees and foot contact. Native animation playback is not available here; use Collect-Logs.cmd and screenshots if changes need tuning.
