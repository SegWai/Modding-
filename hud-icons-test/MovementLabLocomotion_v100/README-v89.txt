MovementLab v89 - M67 outward blast impulse

Keeps native M67 explosion damage/fuse/particles. A single static callback 150ms after detonation applies outward native physics impulse to nearby player/survivor bodies, allowing the explosion's death/knockout processing to run first. Full strength within 2m of body centre, linear falloff to zero at 8m. Solid-cover raycast blocks custom impulse.

Strength uses the native transport-hit corpse impulse formula, 40 * velocity: 20km/h reference = 5.56m/s, giving about 222 Ns outward plus 60 Ns upward at full strength. This is an approximation based on native car code, not an exact match to a live-character collision. Impulse is attempted on living characters too; their native character controller may absorb/ignore it. PhysicsSetRagdoll is documented as a collision-layer toggle, not a general active-ragdoll/knockback switch, and is not used by this blast helper. No forced live-body ragdoll, health/shock change, teleport or repeated velocity override is added.

One impulse per M67 explosion, offline movement-test mission only. Smoke/flash/other grenades unchanged. Replenishing M67 supply, targets, Gunter and locomotion/camera files retained. Logs identify target alive/dead, distance and impulse. Native compilation, actual body displacement and living-character response still require local DayZ testing. Extract into a fresh folder.
