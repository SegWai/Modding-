# v107 command-context correction

v106 logs: all three captured poses failed readback (position errors 0.81–1.48 m; basis errors 1.88–2.00). Each hit the 1.5 second timeout and resumed native death. No ragdoll activation occurred.

v107 fixes a documented API-context violation: the bridge queues graph values, and only the custom corpse CommandHandler calls AnimSetFloat. It resubmits the controls each command tick and records a revision acknowledgement. Baseline capture and verification each wait an additional native command tick after submission. The maximum handoff wait is reduced to 350 ms. Failed matching still restores native death; this is not claimed to be a proven pose-continuity fix.

The 91-bone graph, pose-error limits and momentum calculation are unchanged. Detailed core-joint target/baseline/actual diagnostics identify remaining axis, propagation or graph-evaluation errors. Other player movement, camera, smoothing, equipment and fixtures are unchanged.

Extract this folder separately and run Launch-Movement-Test.cmd. Test standing with arms raised, running, attacking and crawling deaths. Run Collect-Logs.cmd after testing. Native compilation/gameplay cannot be run in the cloud.


Historical v106 bridge notes (superseded by the correction above):
MovementLab v107 — captured-pose graph bridge (first native experiment)

Extract into a NEW folder, launch normally and kill the infected while standing,
running/attacking and fully crawling. Close DayZ and run Collect-Logs.cmd; send
MovementLab-Corpse-v107-Logs.zip and the visible result. If it fails to compile,
send the error/logs; do not mix its files with earlier versions.

This replaces stance/hand-height guessing with actual bone-transform capture
before native death handling. A replacement-only animation-graph branch receives
calculated parent-before-child joint corrections. The actor remains hidden until
native transform readback matches the captured pose within1cm and a small rotation
basis tolerance. Only then does native ragdoll activate, with working horizontal
momentum retained. Unmatched/binding failures retain the original corpse.

This is the FIRST NATIVE TEST of a new graph route, not a confirmed exact-frame fix.
Offline pose conversion passed mathematical reconstruction tests, but native graph
axis/pivot/propagation behavior and performance are unverified. The branch adds546
controls/nodes, default disabled for every actor; only the dedicated corpse enables
it. Source pose has91 shared candidate nodes; missing/invalid non-core nodes are
skipped, while all11 physical core bones are required. Per-limb angular velocities
are not transferred. Native death processing might still disturb a matched pose.
The measured pose-before-activation and visible result must both be checked.

A pause during capture/graph evaluation can remain. The previous approximate
raised/prone input seeding is removed. Existing player movement and human targets
are unchanged. As before there is one live infected and5s confirmed-death respawn.
