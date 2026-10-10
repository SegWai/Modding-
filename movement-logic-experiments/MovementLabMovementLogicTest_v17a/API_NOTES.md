# V17a native movement continuity

V16's repeated scripted-command/native-MOVE handoff is a candidate cause of
visible pose jumps, not a confirmed diagnosis from logs. The supplied recording
shows abrupt changes; it does not provide input/graph/command telemetry.

V17a removes all scripted command lifecycle, manually requested SlidingPose,
PreAnim variables and PrePhys translation. PlayerBase overrides only native
movement angle and gait before the normal CommandHandler. The engine retains
its animation clock, command, direction-change state and collision handling.
No exact brace pose or slowed clip playback is promised.

Incoming gait eases to 1.60 in 0.12s, then direction switches once and gait
easily recovers to 2.0 over 0.50s. During that 0.62s interval direction is
committed. Current net intent at completion can trigger a new reversal in the
same tick, preserving override ownership. Equal opposing keys never select
an arbitrary direction. Held overlap is neutral; no-key gaps below 0.10s are
tolerated. Other exclusions release overrides immediately.

V11 startup methods and ordinary braking formulas remain unchanged. An added
mission guard skips key-release braking while reversal owns native inputs,
recording effective direction and gait for a subsequent ordinary stop.
This avoids two controllers competing during a short input gap.

Tests mechanically translate the actual state controller and PlayerBase
integration methods into C++ with a mock SDK. Checks cover 30/60/144 FPS,
committed angle, bounded speed changes, overlap, gaps, consecutive reversals,
exclusions and v11 method/formula equality. They do not compile Enforce or
simulate native animation selection. Local DayZ validation is required.

V17a: split the oversized eligibility expression into short early-return
checks, with the same exclusions. Read key values individually before
computing intent. Native Enforce compilation still requires local validation.
