MovementLab v91 - five independently respawning infected

Five native infected start on a small forward arc, each 20 metres horizontally from the player's initial spawn, spaced about two metres apart. Native AI is initialized: they can roam/chase/attack and are not pinned 20m from a moving player. Class: ZmbM_HermitSkinny_Beige.

Each fixture opts into the native ANIM_DEATH_IMPULSE death mode while preserving ZombieBase.HandleDeath/StartCommand_Death. No collision-layer switch is misrepresented as a separate ragdoll solver. Native physics/death appearance needs in-game verification. M67 custom blast impulse now includes infected as well as survivors.

Each of five slots has its OWN deadline: five seconds after that zombie's death is observed, delete only its corpse and create its replacement at that slot's original spawn point. Other living infected are untouched. Multiple deaths use independent clocks. Spawn failures retry after five seconds. Mission shutdown removes tracked infected/corpses. No global group wipe or continuously growing corpse collection.

Male jog loop, other NPC rules, grenade supply, Gunter, camera and player locomotion retained. Offline only. Extract into a fresh folder. Native compilation, AI navigation/death physics and timing still require local DayZ testing.
