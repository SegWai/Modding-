Immediate Scroll Targets v2 — based on user-confirmed all-pose smoothing v1.
Standing upward ladder: walk~85,walk100,walk120,jog80,jog100,sprint100.
Prior downward boundary retained: jog80 -> defaultwalk~85 (notwalk120).
A wheel burst can select any target across mode boundaries in one update.
Crouch ladder remains30/~47/60/~73/~87/nativefast.
Raw signed wheel delta counted; common120-unit deltas normalized, action press fallback.
Animations/acceleration blend toward the stored target after scrolling stops.
No need to wait for animation completion before selecting another speed.
Pending input during temporary native command restrictions is applied when eligible;
menus/pause/stance changes clear pending input. Clamp at ladder endpoints.
Physical held Shift still overrides current gait; target selection is retained.
No graph/clip/brake/pose timer changes from confirmed all-smoothing package.
Close DayZ, extract ZIP, run Launch-Movement-Test.cmd.
Native wheel sign/units/focus and visual pacing require local test; logs record raw steps.
Default confirmed PoseExit v2 and previous all-smoothing package stay preserved.

Revision20: jog100 -> fast aim native100; fast aim100/120 -> jog100 on lowering. Fast aim80 -> jog80. Fast aim level2 now uses original native animation sources. Entry Shift latch initialized from held input.

Sprint -> aim enters exclusive fast aim140% (42FPS), smoothly falls to native100% over1.5s. Wheel events during transition are discarded. Normal wheel levels remain80/100/120. Crouch/slow aim unchanged.

Revision20 captures recently achieved sprint before weapon raise clears it. Exclusive140% entry applies to IsWeapon projectile weapons only. F8 must be custom/OFF to see custom speeds.

Revision20: sprint-entry fast aim140 ->100 slowdown duration1.5s; handoff allowance remains0.25s. Wheel locked until complete.

Revision20: exclusive140% aim requires1 continuous second achieved upright sprint gait>=2.99. Lowered slowdown/stopping/crouch/menu resets qualification. Acceleration/Shift/sprint selection alone never qualifies. Existing1.5s decay and0.25s maximum handoff retained.

Revision20: sprint qualification gait>=2.9 plus active sprint request for1 continuous second. Offline unlimited stamina/load cap; black tactical gear and smaller42-slot black assault backpack, two weapon attachments retained. Every launch spawns atNWAF (4610,10180).1.5s aim decay unchanged.

Revision20: qualified sprint-to-raise grace1s (still resets immediately on lowered slowdown); additional gate logs. Intended NWAF runway spawn4500/10300.5 stationary damageable targets,10m spacing, respawn3s after death forever.140% visible speed remains under investigation; send logs.

Revision20:140->100 decay restored0.5s. Exactly5 targets total (one per slot),10m spacing along airfield pavement; spawn search checks60m paved line. Initialization guarded against repeatedOnInit.3-second recurring respawn retained.

Revision20: pavement vector multiplier nowfloat (native compile fix). Full-sprint qualification uses achieved gait, accepts upright0/3 before raise, does not require heldShift/native cleared input.1s eligibility and0.5s decay retained.

Revision20: workingRevision17 sprintgate preserved; onlyaimdecay changedto1.5s. Offline range removesuntracked extra survivorswithin100m onstartup/every1s, preservingcontrolledplayerandfive assignedtargets; live-slotspawn guarded. This cleanup islimitedtothetestmission.

Revision20: aim140->100 decay1second. ALLrangeNPCspawning/respawn/cleanupremoved. Onlycontrolledplayercreated. Blackgear/unlimitedstamina/pavedairfieldspawnretained.

Revision20:140->100 slowdown0.7seconds. Workingqualification/handoffunchanged. NoNPCs.
