# V16: committed moving reversals

Based on v15, retaining unchanged v11 ordinary startup and braking methods.
The new reversal recovery is 0.62 seconds: old weight 0.48 -> 0.10 during
0.10 seconds, crossover during 0.10-0.18 seconds, new weight 0.10 -> 1.0
during 0.18-0.62 seconds. The native graph clock is unchanged.

One CMD_SlidingPose request per scripted reversal. Incoming direction is held
until the native 0.18-second gate; target direction is fixed thereafter.
No pose-atlas sweep, repeated command, frame freeze or stationary dwell.

Completed target is passed to PlayerBase when the custom command ends.
Native movement handoff locks that completed angle and jogging gait for
0.14 seconds. CommandHandler processes the handoff before reversal detection;
at its completion, an opposite current input starts the next reversal in the
same handler tick, avoiding a tick of native instant direction switching.
Current input, rather than a queue of every press, selects the next reversal.
Neither the custom command nor native handoff retargets while in progress.

Short no-key gaps accumulate to 0.10 seconds before cancellation, reset by
any held movement key (including overlapping opposite keys). Sustained key
release cancels. Native lifecycle and other existing exclusion checks remain.
Physics controls only horizontal translation; vertical translation is retained.

Override parameter names match the native prototypes, including pDt.
Test harness mechanically translates actual command/handoff methods and checks
30/60/144 FPS, spam/overlap/gap patterns, cancellation and v11 method equality.
It does not compile Enforce or emulate graph playback. Native animation
stability, script compilation and collision still need a local DayZ test.
