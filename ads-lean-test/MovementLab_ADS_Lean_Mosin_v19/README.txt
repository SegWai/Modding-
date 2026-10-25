Mosin lean v19 — shooting range + small right-lean head correction

Extract into a NEW folder. Run Launch-Mosin-Lean-Test.cmd directly.
Project root F:\DayZProjects; Steam game location is separate. Vanilla only.

Head: on right lean, Head rotation is moved another 5 degrees toward anatomical left in all four shared pose branches. Player and NPC receive the same correction. Left lean and the v14 restored standing legs stay unchanged.

Your Mosin starts with the PU scope and vanilla improvised bottle suppressor attached. The internal magazine reserve refills every 100ms when the weapon FSM is idle; ammo reloads are unnecessary. The normal Mosin bolt cycle remains. Rifle/suppressor condition is maintained during this offline test. No changes to ballistics, rate of fire or bullet damage.

The red NPC keeps the working +/-2m aimed/leaning patrol. It is now damageable. Each death schedules a NEW target after 1000ms, from EEKilled rather than a polling timer. The old body remains briefly. The new target restarts the same patrol from the original position.

Ragdoll: reuse the earlier human range target immediate PhysicsSetRagdoll takeover (MovementLabLocomotion_v107/MovementLabRangeNPC.c, same human path as v88), not the infected mesh replacement bridge. Transfer recent horizontal travel with one impulse while preserving gravity. If native articulated physics does not activate, retry once after 50ms, then leave native death as fallback. Corpses remain up to 10 seconds, maximum four, to avoid accumulating bodies. This is native human articulated ragdoll; no claim of a new 91-bone captured-pose bridge for humans.

F10 pause/resume NPC. F6 native ADS head-tilt comparison. F7 native/custom lean.
F8 third-person inspection; F9 joint measurements. No launch menus.

Test scoped shooting, head exposure in both directions, sustained fire without ammunition reload, death ragdoll and repeated 1-second respawns. Native compilation, attachment acceptance, ragdoll behavior and firing/respawn timing need your game test. If wrong, close DayZ and run Collect-Logs.cmd; send the v17 ZIP.

V18 compile correction: v17 referenced a method added by a different modded PlayerBase layer. Lean control, range motion capture, death and ragdoll hooks now live in ONE PlayerBase patch. The ammo helper remains a separate class. Head/legs, equipment, ammo refill, ragdoll and 1-second respawn behavior are otherwise unchanged. Native DayZ compilation/playback still needs testing.

V19 compile correction: replace the rejected vector/scalar division in the motion sampler with separate float time conversion and vector * scalar multiplication. Sampling threshold, velocity limits, ragdoll, 1-second respawn, unlimited reserve and pose are unchanged. Native compilation/playback still needs a game test.
