MovementLab v87 - reserve starting grenade supply

Fixes grenade creation being attempted only after the weapons and magazine loadout had filled cargo. Both native and SNAFU loadouts now reserve the two M67 grenades immediately after the backpack is equipped, before weapon/magazine creation. SNAFU path also has a native backpack fallback if the custom backpack fails.

Grenades are created directly in backpack cargo with CreateEntityInCargo. When a used/thrown grenade needs replacing, refill still prefers backpack cargo, but falls back to other player inventory space if the backpack is full/missing. No space anywhere: log an explicit error and retry when space is available. Count includes carried and held M67s, ceiling two, check every 250ms; dropping/transferring out also replenishes. No armed grenades or ground spawns are created by this routine.

Only loadout/refill mission source changed. NPC timing, camera, locomotion and Gunter remain v86. Extract into a fresh folder. Static/package checks only; local DayZ compilation and inventory/throw-refill checks still required.
