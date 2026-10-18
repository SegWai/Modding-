MovementLab v82 - experimental living-ragdoll targets

IMPORTANT: PhysicsSetRagdoll is a full native physics switch. Available script source does not establish support for balanced living active ragdolls, or wake/stand animations while physics remains enabled. This package tests the requested switches; a living target may collapse or fail to stand. Do not treat it as a verified active-ragdoll system.

Male: enable physics ragdoll at spawn while alive; keep enabled on death; one second after EEKilled disable ragdoll and simulation. Respawn at the recorded death position five seconds after death observation; new male has physics enabled again. No death animation replaces the physics body during the one-second interval.

Female: physics ragdoll enabled at spawn and never explicitly disabled during knockout or recovery. Incoming native-calculated global health damage is accumulated manually, while engine damage is vetoed to prevent fatal zone/shock/blood effects. Nonlethal hits reduce actual global health; lethal hit leaves 1 health and requests unconsciousness instead of setting health to zero. No every-frame health refill. Five seconds after unconsciousness starts, restore full global health/blood/shock and request wake/stand with physics still enabled. Repeat hits while unconscious/recovering do not restart the timer. Native wake/stand compatibility with persistent ragdoll is unverified.

Targets have no movement AI. Different female clothes, male respawns, Gunter, camera limits, shoulder smoothing and loadout retained. Extract to a fresh folder. Native compilation and all ragdoll/knockout/recovery behaviour require local DayZ testing.
