Mosin lean v14 — head and stationary-leg test

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd directly.
Project root F:\DayZProjects; Steam game directory remains separate.
Vanilla Mosin only. The working v13 NPC controller and control template are retained.

Changes:
- Shared final head correction after ADS/weapon IK: an extra 12-degree counter-roll in either lean direction and a small 5-degree forward nod. Applies to player and NPC in standing, moving and crouched custom ADS lean. Neutral/native comparison are unaffected. These angles are a test adjustment based on the screenshots; native visual alignment still needs checking.
- Stationary standing only: restore v3 leg/foot and hip-height corrections, removing the later 55-degree outward foot yaw and deeper hip drop. Current upper-body/hand corrections stay. Walking leg cycles and crouched legs stay unchanged.

Test:
1. Watch the red NPC walking left and right; compare its head to the rifle sights.
2. F10 pauses it in its current lean so you can inspect the restored planted stance. F10 resumes.
3. With your Mosin, stand still, aim and hold Q or E to check both head and legs. Walk and crouch while aiming/leaning to compare the head across states.
4. F8 enables third-person raised-Mosin pose inspection; F7 compares native/custom lean; F9 records joint measurements.
5. If a correction is needed, close DayZ and run Collect-Logs.cmd, then send the log ZIP and a screenshot.

The existing registered controls and HasVariableChanged arguments are unchanged. No new graph variables, NPC speed changes, launch menus or gameplay mechanics. Source pose math and PBO checks do not verify native DayZ animation playback. This package needs your in-game visual test.
