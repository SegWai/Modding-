# V15 clean-baseline rebuild and reversal handoff stabilization

Created by copying movement-logic-test/MovementLabMovementLogicTest (stable
v11), not by copying a v12/v13/v14 source tree. Only the v14 moving momentum
controller and necessary command lifecycle/handoff hooks were integrated.
V11's ordinary startup and braking method bodies are unchanged, except the
mission's version labels. The harness compares those bodies to v11 exactly.
The stable v11 ZIP/source are preserved.

V14's moving momentum curve is unchanged: old-direction gain 0.55 to 0.10
in 0.10s; continuous old/new vector crossover over 0.08s; new-direction gain
0.10 to 1 over 0.32s. Base velocity sampling/fallback/clamp are unchanged.
One CMD_SlidingPose request, normal graph exit/blend and no fixed dwell or
rotation lock. Native animation playback rates are not changed.

The user reported intermittent animation/pose jumps in v14. Two candidate
causes are addressed here; neither is proven without native instrumentation:
1. Directional pose atlas traversal. V14 interpolated the graph direction
across 180 degrees, potentially sampling unrelated forward/back braces during
sideways movement. V15 keeps the original brace direction until the normal
0.18s exit gate, then provides the target locomotion direction. It never
sweeps intermediate direction samples. A single native request lets the graph
continue its own outgoing blend; it does not re-trigger a held pose each tick.
2. Native-command recreation. After finishing the script command, native MOVE
may begin with a default angle/gait. A 0.10s input-owned handoff seeds direction
from CURRENT raw keys and gait=2, then releases those overrides. This is only
applied after the custom reversal, not to ordinary v11 starts/stops. Input
release/manual walk/UI/F7/F8/death/non-move/crouch states clear its ownership.

The existing graph's SlidingPoseVar may capture the initial movement direction;
its variable semantics and exact internal state clock cannot be observed in
this cloud environment. State/pose blending and foot timing need local testing.
There are no edits to native animation files or a packaged replacement graph.

The actual command and handoff methods were mechanically translated to C++
with an SDK mock. At 30/60/144 FPS checks cover constant bracing vs target
angles (no atlas sweep), continuous horizontal momentum/no dwell, single native
request, recovery, correct horizontal axis, vertical preservation, cancellation,
invalid binding, native handoff direction/gait and override release. Exact
override argument names are checked, including the prior dt/pDt failure.
Ordinary v11 startup and braking method equality checks pass.
These checks do not compile Enforce or simulate the native animation graph,
collision, gravity, gait filtering or network replication. Instrumented local
logs and the user's video are required to assess actual transition stability.
Harness: tools/check_movement_logic_experiment_v15.py.
