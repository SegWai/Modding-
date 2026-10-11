MovementLab CTRL MODES v11 - jogging A/D reversal resistance (based on v10)
This is distinct from the historical original Movement Logic Test v11.

Close DayZ, keep Steam running, extract the WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing/import needed.

NEW CHANGE:
Rapid jogging A -> D or D -> A adds strong native movement-direction inertia.
This includes W+A -> W+D and backward diagonals while jogging. It also detects
short key-release or both-held gaps (up to 0.18s). Repeated switching keeps the
resistance active; holding a stable direction lets it smoothly fade in 0.50s.

Only the native direction filter is increased during a reversal: 2.5 normally,
up to 7.0 while resisting the opposite input. Body turning stays responsive.
No frozen frame, forced full stop, artificial speed dip, angle override, queued
reversal or animation restart is added. Native DayZ controls the resulting
motion/path and pose. This is not a tested guarantee of difficulty dodging.

TEST:
Select standing jogging with Ctrl. Hold A long enough to jog, then switch to
D while moving. Try repeated A/D presses and W+A/W+D. Compare with saved v10.
Then hold one direction steady to check normal movement returns. Test releases
and Ctrl jog-to-walk to check the existing stopping/transition rules remain.
This resistance is jogging-only: walking, crouching, aiming/gestures, startup,
standing braking, and Shift sprint requests are excluded. Native stance and
weapon restrictions remain. F7 still compares the whole profile with vanilla.

All v10 controls are retained: permanent responsive body rotation with no F8
toggle; later Ctrl jog-to-walk entry; slow crouch/native fast Shift crouch;
fast crouch -> standing jog with consumed Shift; slow crouch -> previous mode.
Full stopping and sprint returns retain their current curves and timers.
V10 remains available unchanged as the fallback.

Actual translated method tests passed at 30/60/144 FPS in both callback orders:
A/D and diagonal reversals, spam, stable decay, both-held gaps and exclusions,
plus standing/crouch/stop regression checks. Actual filter checks verify only
direction timeout changes and other filter outputs match v10. These checks
model script requests, not native animation frames or physical paths. Native
Enforce compilation and the heaviness/visual feel need your local game test.
Logs: Profiles/MovementLogic.
