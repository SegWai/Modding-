CTRL MODES v13 - LATERAL MOMENTUM

Close DayZ, keep Steam running, extract the whole ZIP into a fresh folder and run Launch-Movement-Test.cmd.

In standing jogging mode, pure A/D reversals now slew signed lateral gait from -2 to +2 at 9 gait units per second. A full-speed reversal crosses zero after approximately 0.22 seconds and reaches opposite jogging pace after 0.44 seconds. During that transition the requested direction follows the remaining momentum rather than immediately following the newly pressed key. Spam changes the target without resetting velocity. No pose freeze or script command restart.

Temporary speed AND angle overrides apply during pure lateral resistance. Normal native steering resumes afterwards. Walking, Shift sprint requests, crouching, startup, braking and interaction exclusions remain. Previous stop/toggle/crouch behavior retained. F7 compares vanilla.

Actual translated controller checks passed at 30/60/144 FPS in both callback orders, including crossing delay, continuous signed velocity during spam, reverse recovery and release ownership. Native DayZ compilation, animation blending and physics require in-game testing.
