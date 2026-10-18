MovementLab v106 — captured-pose graph bridge (first native experiment)

Extract into a NEW folder, launch normally and kill the infected while standing,
running/attacking and fully crawling. Close DayZ and run Collect-Logs.cmd; send
MovementLab-Corpse-v106-Logs.zip and the visible result. If it fails to compile,
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
