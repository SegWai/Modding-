# V14 moving reversal experiment

Based on v11 with v13's verified-in-user-game native scripted pose mechanism.
V11 source, stopping/starting settings and stable ZIP are unchanged. V13 is
retained separately for comparison; no v12 walking-restart/braking code is used.

The uploaded graphs select a directional pose with (MovementDirection+180)/360.
Locomotion.Erc.RunSlidingPose maps to p_erc_run_stop_poses.anm. This is a
pose collection, not an ordinary temporal walking clip. Normal SlidingPose
exits have a >0.18 realtime-state threshold and 0.3 outgoing blend span.

V14 issues CMD_SlidingPose only once from HumanCommandScript.OnActivate.
PreAnimUpdate progresses MovementDirection smoothly to the opposite input
over 0.18s rather than holding a single direction throughout a stationary
pause. The normal graph exit/blend is not blocked or replaced. The actual
native locomotion animation clock remains unchanged; no generic clip playback
rate setter has been verified. Graph variable-update semantics, foot placement,
visible pose progression and outgoing blend must be checked locally.

PrePhysUpdate assigns local X/Z translation from old/new intent vectors. Old
momentum declines from 55% to 10% over 0.10s, blends into the opposite momentum
over another 0.08s, then new-direction speed eases from 10% to 100% over 0.32s.
A mathematical zero crossing can occur for opposing velocities, but no timed
stationary dwell is imposed. Pure lateral velocity never rotates through a
forward direction. Root rotation is no longer locked. Vertical translation is
preserved; no world-space teleport or disabled gravity. Engine collision remains
involved, but slopes/collision and physical drift require local verification.

Base speed samples PhysicsGetVelocity on activation. Native root-driven velocity
may be zero, in which case 2.8m/s is used. Values are clamped to 1.5..3.2m/s.
This approximation can cause mismatch/sliding compared with native gait and is
not an exact physical velocity model. Returning to native movement after 0.50s
may still require handoff tuning, especially if Shift is held.

Trigger retains v13's raw opposite-intent detection, but no longer requires two
consecutive sampled high gaits or waits for the walking-start timer to finish
once achieved gait is already >=1.75. Manual walking and non-standing/non-local/
armed/raised/non-move states bypass it. Diagonal reversals use normalized input.
Release of ALL movement keys, F8/F7 disable, UI/pause, death/unconsciousness,
falling, held items, and large time steps cancel. Current keys control native
movement after completion; inputs during recovery cannot reset its timer.

Exact override parameter names were verified against the official DayZ SDK to
avoid v13's dt/pDt native compilation issue. A mechanical translation of actual
command code passed mocked tests at 30/60/144 FPS for single command dispatch,
continuous motion, no dwell, correct horizontal axis, continuous curve boundaries,
progressive pose variables, final full-speed recovery, vertical preservation,
release/guard cancellation and invalid binding. This does not compile Enforce
or model native graph transitions, rotation, collisions or multiplayer behavior.
Harness: tools/check_movement_logic_experiment_v14.py.
