MovementLab v103 — native starting stance before infected ragdoll

Extract into a NEW folder and launch. Compare a running kill with raised arms,
a stationary kill, and a broken-leg crawling kill. Close DayZ and Collect-Logs.cmd;
send MovementLab-Corpse-v103-Logs.zip and describe any remaining pose jump.

Keeps the v102 momentum handoff you confirmed works. Captures crawling, gait and
whether either hand is above pelvis height BEFORE native death handling. The
hidden infected-model Human actor is primed through native movement/input: prone
for a crawler; raised unarmed stance for an upright raised-arm death; appropriate
movement gait. It waits for matching head/pelvis/hand heights before activating
ragdoll, then releases the inputs. Crawler initialization cannot fall back to a
standing replacement; failure retains the original ground-level infected corpse.

This seeds a native approximate starting pose, not an exact infected frame/limb
velocity clone. Human raised-unarmed and prone poses differ from infected poses.
Native stance forcing, readiness and visible arm/prone results require your run.
One zombie, five-second respawn, momentum, player and other fixtures are retained.
