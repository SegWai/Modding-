MovementLab v101 — infected corpse momentum and pose initialization

Close DayZ, extract the full ZIP into a NEW folder and launch normally.
Kill the zombie while it is standing, walking and running. Compare how far and
in which direction the corpse travels. Close DayZ, run Collect-Logs.cmd and send
MovementLab-Corpse-v101-Logs.zip if momentum or the initial pose is still wrong.

Retains the infected-model Human-ragdoll corpse that you confirmed works in v100.
Captures velocity before native EEKilled, with recent world-motion samples as a
fallback when the infected controller reports zero. Creates the replacement at
the captured death position. It waits for a valid animated head/pelvis pose before
killing it and enabling ragdoll. The hidden initializing replacement has collision
disabled. The original collider is disabled before activating the new ragdoll.

Transfers momentum once using mass*(capturedVelocity-currentVelocity), with no
extra upward boost or continuous pushing. The corpse then moves under physics.
The one live zombie, five-second replacement, human targets, loadout and player
movement are unchanged. Exact limb-pose cloning is not implemented: generic bone
writers failed. Movement capture, native impulse propagation and pose warmup need
your game test; package/lifecycle checks cannot verify the visible result.
