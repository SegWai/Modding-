CROUCH WHEEL V6 - NATIVE-SPEED FREEZE CORRECTION TEST

Close DayZ, keep Steam running, extract the entire ZIP into a fresh folder, and run Launch-Movement-Test.cmd. Do not extract over v5. Preparation replaces test PBOs only, original DZ resources remain read-only.

V5 was reported frozen at native level5 with F8 both OFF and ON. V6 removes the experimental nested timed BlendT wheel selectors and outer timed wrapper. It restores the wheel BlendN selector structure from user-confirmed working v1; native run clip mappings remain identical. The hidden90 wrapper now uses a continuously weighted BlendN with a short scripted ramp, so it does not use the suspect timed selectors. Exact native failure mechanism remains unverified here.

FIRST TEST: leave F8 OFF (default), crouch and scroll UP to5. Check native fast crouch keeps animating. Also try holding Shift. If either still freezes, do not treat the correction as verified; use original v1 and send script/RPT logs from this folder Profiles/MovementLogic.

THEN TEST: press F8 ON, move at level5, scroll DOWN once to4. Automatic hidden90 clip stage stays downward-only: .10s entry, .10s hold, .10s exit. More downward scroll queues lower levels. Upward scroll, Shift, stopping, stance exit or F8 OFF cancels. Only five selectable levels; hidden90 cannot be selected or retained.

90% is27FPS of original30FPS slow-crouch clips, not a measured90% of native fast gait. Existing downward pacing and standing/strafe rules retained. Comparison OFF now uses restored v1 graph selection plus the existing downward controller pace, not the rejected v4 timed graph. Existing v1/v4/v5 archives unchanged. Controller/graph/package checks passed here; native compilation/animation still requires DayZ confirmation.
