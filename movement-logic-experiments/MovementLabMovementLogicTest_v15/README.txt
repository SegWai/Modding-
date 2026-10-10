MovementLab v15 - Clean v11 base + heavy moving reversals

Close DayZ, keep Steam running, extract this ZIP into a fresh folder,
and open Launch-Movement-Test.cmd. No packing or animation import needed.

Jog A then D, D then A, W then S, and S then W, with/without Shift.
F8 toggles ONLY the moving-reversal addition; OFF retains v11 movement.
F7 retains the original heavier/vanilla switch. Test standing with empty hands.
Ctrl/manual walking bypasses the addition. There is no stationary hold.

This build was copied directly from stable v11. Its ordinary walking-start,
sprint/jog/backward/lateral braking methods and timings are preserved.
Only the moving-reversal controller is added, with two stability corrections:
- No sweep across unrelated directional brace samples. A single native brace
  progresses into the graph's normal blend toward the opposite direction.
- A brief direction/gait handoff prevents the new native movement command
  starting with an unintended forward or idle animation.

The moving reversal retains v14's approximately half-second heavy push-off.
The native animation playback clock is unchanged. The brief foot-plant pose
is the native transition; the v13 fixed stationary pause is not present.

Look for smoother A/D transitions without jumps or forward movement.
Also check ordinary v11 starts/stops by pressing F8 to disable the addition.
Logs are in Profiles/MovementLogic; search [MovementLab v15].
Native animation blending still needs a local test. Send a recording of any
remaining jumps, or a screenshot if a script compile error appears.
Stable v11 and your older extracted versions remain unchanged.
