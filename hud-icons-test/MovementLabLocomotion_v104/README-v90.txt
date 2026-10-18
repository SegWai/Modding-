MovementLab v90 - male target lateral jogging loop

Male starts jogging left/right across a two-metre span: endpoints one metre left and one metre right of his spawn centre, measured in his initial facing frame. Initial travel is left; reverse at each endpoint. Uses native input gait 2 and +/-90-degree lateral movement, retaining the forward-facing target pose; native direction filters handle reversals. No SetPosition/teleport loop. Turning inertia/frame timing can cause small endpoint overshoot.

Common male creation helper initializes the route after orientation is set, including every eight-second respawn. Each replacement uses its own spawn/death-position centre under the existing respawn rules. Only this explicitly initialized offline male receives movement input. Overrides are released on death, unconsciousness, non-move commands, or disabled test state. Female remains unchanged.

Persistent male death ragdoll, grenade refill/blast, Gunter, player locomotion and camera retained. Extract into a fresh folder. Static/package checks only; native compilation, NPC jogging/input acceptance and reversal distance require local DayZ testing.
