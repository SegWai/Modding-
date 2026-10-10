MovementLab v17 - Native movement continuity test

Close DayZ, keep Steam running, extract into a fresh folder, and run
Launch-Movement-Test.cmd. No packing or animation import needed.
F8 toggles reversal control only; F7 retains the original heavy/vanilla switch.
Test empty-handed and standing. Ordinary v11 start/stop formulas are retained.

V16 still produced visible pose jumps in your recording. V17 replaces its
scripted movement/brace/handoff with native MOVE input control throughout.
It never starts a script command, manually requests SlidingPose, writes graph
animation variables, freezes frames, or overrides physical translation.
DayZ chooses and blends the animations. The exact brace shape and perceived
weight can differ from v15/v16; this test prioritizes native animation continuity.

Reversal: reduce incoming gait during 0.12 seconds, switch to the committed
opposite direction, and ease back toward jogging over 0.50 seconds.
Minimum requested gait is 1.60, not idle. Recovery totals 0.62 seconds.
Opposite taps during recovery cannot restart or retarget it. After recovery,
current held input selects the next reversal without an intervening raw-input
tick. Taps are not queued. Opposing held keys are neutral and cannot cancel
an ongoing reversal; complete key releases lasting 0.10 seconds do cancel.

Try single A->D / D->A and W->S / S->W reversals, then rapid alternation.
Check whether pose jumps are gone and whether weight is still sufficient.
F8 OFF restores ordinary v11 behavior for comparison.

Actual translated controller checks passed at 30/60/144 FPS with a mocked SDK,
including overlaps and release gaps. Native Enforce compilation and graph
animation behavior still require this DayZ test. Logs: Profiles/MovementLogic.
V11, v15 and v16 remain unchanged and available.
