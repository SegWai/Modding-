MovementLab v79 - offline NPC and Gunter range fixtures

One unarmed, damageable survivor stands 8 metres along the range direction. He has no AI patrol/input and is not invincible. Native PhysicsSetRagdoll(true) is enabled on his death only; he remains animated and standing while alive. This is a native API test, not a bundled external ragdoll mod. Native engine support/behaviour needs in-game verification.

A Gunter 2 (Hatchback_02) spawns 6 metres east of the player with native OnDebugSpawn setup: wheels, doors, engine essentials, headlights and operating fluids, with its mounted battery charged. Engine starts normally via the driver controls.

Keeps v78 camera limits, 90-degree turn threshold, shoulder smoothing and suppressor loadout. Offline only, one set per mission launch. Extract to a fresh folder. Native compilation, ragdoll behaviour, placement and driving require a local DayZ 1.30 test.
