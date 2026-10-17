MovementLab v76 - keep shoulder correction across turn-in-place

The prior graph corrected the idle leaf but left native turn-in-place clips outside that correction. v76 moves the same Spine3/Neck counter-rotation to the shared idle/turn state-machine output. It is applied once, after the turn blend, including both transition directions. The upright turn path now keeps the same continuous head-look additive source already used during idle, avoiding a pose-source change while the body rotates.

No camera or input overrides are added. The v75 pose controller (including shoulder feedback/smoothing and combat safeguards) remains byte-identical. Native turn clips, timing, root rotation, feet and IK are retained. Walking/jogging/sprint graphs and speed/momentum logic are unchanged.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Static graph routing/source and package checks passed. Native DayZ compile and visual shoulder alignment during small and large turns still require in-game testing.
