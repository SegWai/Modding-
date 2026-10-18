MovementLab v105 — correct v104 crawling readiness regression

Extract into a NEW folder, launch, let the broken-leg zombie crawl fully and kill
it. Close DayZ, Collect-Logs.cmd; send MovementLab-Corpse-v105-Logs.zip and whether
its corpse stays low and actually moves with ragdoll.

v104 timed out after2s because its hard model-space pelvis/head height limits
rejected the repeatable native prone pose. Rollback resumed the original death
animation, explaining the freeze then standing/default fall you observed.

v105 checks native prone stance, a horizontal head-to-pelvis torso direction and
100ms of stable pose, rather than assuming model-space Y equals ground clearance.
The replacement pelvis is aligned to the source crawler's captured world pelvis
before physics activation. Existing visibility guards, momentum and cleanup stay.
Native compilation, prone readiness and the visible result need the local test.

IMPORTANT: the running-arm/attack pose snap is NOT solved by this change.
The native Human-pose approximation cannot preserve the exact infected animation
frame. A separate captured-pose graph route has only offline math groundwork so
far; there is no verified exact-frame transfer implementation yet.
