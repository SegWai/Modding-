MovementLab v93 - one living infected; remove forced common death mode

Reduced infected fixture count from five to one, 20m straight ahead of initial player facing. Native AI active; spawns alive and damageable. Existing death-confirmed five-second replacement retained. No periodic missing-reference respawns.

Removed all forced infected death-mode, StartCommand_Death and HandleDeath overrides. EEKilled only notifies the slot timer; native infected death behaviour is preserved. IMPORTANT: this does not implement character-style custom zombie ragdoll. The Human.PhysicsSetRagdoll API is not exposed on DayZInfected and is documented as a collision-layer toggle. No substitute death animation is claimed to be that feature. Matching custom physical ragdoll for infected remains unresolved.

Human NPCs and their existing behaviour, grenade supply/blast, Gunter, player movement and camera unchanged. Start a fresh mission/extract a fresh folder to clear the old group. Static/package checks only; local compilation and gameplay test required.
