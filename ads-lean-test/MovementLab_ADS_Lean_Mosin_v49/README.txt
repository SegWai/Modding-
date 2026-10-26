ORIGINAL DAYZ DISTANCE CALIBRATION v49 — measurement only
No pose changes yet. We must measure the actual vanilla distances before matching
the custom poses. Body graph and first-person camera fix are unchanged from v48.
Native reference loads ONLY the logic recorder PBO, not the custom workspace.
Two direct launchers; no numbered batch menu or toggle.

1. Run Launch-Vanilla-Lean-Reference.cmd.
   Stand still with AK74 raised/aiming. Keep the same aim direction and mode.
   Hold NEUTRAL about 3 seconds, Q about 3 seconds, E about 3 seconds.
   Wait for each captured notice and then "Lean distances captured". Close DayZ.
2. Run Launch-Mosin-Lean-Test.cmd and repeat the same neutral/Q/E holds with
   the same gun and aiming mode. Wait for completion. Close DayZ.
3. Run Collect-Logs.cmd and send the ZIP. It contains both runs.

Capture starts automatically. Do not press F7 during calibration. F9 restarts
that run if needed. Stay standing; do not walk, crouch or change aim direction.
Each state averages 20 real samples after 0.5 seconds settling and records the
head, eyes, chest, pelvis and both feet. Full bone transforms accompany each.
Distances will be measured against each run's neutral position in model space.
Any vanilla left/right asymmetry will be reported rather than silently guessing
an equal target. Keep the existing silhouettes and foot placements when adjusting.
No Blender assets/helpers, previews or authoring sources are in this runtime ZIP.
Native Windows compilation/playback and measurement remain to be checked in game.
