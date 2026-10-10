MovementLab v14 - Moving reversal experiment (stable v11 baseline)

Close DayZ, keep Steam running, extract this entire ZIP into a separate folder,
and open Launch-Movement-Test.cmd. No Addon Builder or animation import needed.

Jog A then D, D then A, W then S, and S then W. Test with and without Shift.
F8 toggles ONLY this reversal experiment; OFF retains v11 movement behavior.
F7 switches the original heavier movement vs vanilla filters.
Use flat ground, standing, empty hands. Ctrl/manual walking bypasses the test.
Reversal is based on achieved jogging speed; slow walking is unaffected.

V13's 0.32s stationary hold is removed. The native bracing command is requested
once, directional pose samples progress, and its normal outgoing blend is
allowed to run. Horizontal movement is slow but continues: braking momentum
changes direction and then accelerates back to normal over about 0.50 seconds.
There is no scheduled zero-speed dwell or root-rotation lock. Native clip
playback rates are unchanged; this tests pose/blend progression and movement
weight rather than directly slowing the animation clock.

Watch for a smooth heavy push-off instead of a frozen foot-out pose.
A/D reversal should not travel forward. Current held keys regain normal
control at the end; releasing every movement key ends the experiment early.
Other key presses during the recovery do not reset its timer. After recovery,
repeated reversals can trigger another recovery; there is no invulnerability.

Logs: Profiles/MovementLogic. Search [MovementLab v14]. START shows both
angles, requested base speed and recovery time; END shows displacement.
If a script error appears, send its screenshot. If the motion/feet slide or
blend incorrectly, send a recording. Native compilation and visible blending
need your local test. Stable v11 remains unchanged.
