# Scope and implementation

This is a standalone single-player mission, with no packaged mod dependency.
It uses the already tested offline spawn/launch pattern. Native filters and
the new mission have not been compiled or played in a DayZ engine here.

Source evidence: Bohemia's DayZ 1.29 script revision
`86974a0f5bd16b1ee3e334ad828133c93dca80a1`.

- [HumanCommandMove runtime setters](https://github.com/BohemiaInteractive/DayZ-Script-Diff/blob/86974a0f5bd16b1ee3e334ad828133c93dca80a1/scripts/3_game/human.c)
- [Vanilla stamina inertia formula](https://github.com/BohemiaInteractive/DayZ-Script-Diff/blob/86974a0f5bd16b1ee3e334ad828133c93dca80a1/scripts/4_world/entities/manbase/playerbase.c)
- [Movement defaults](https://github.com/BohemiaInteractive/DayZ-Script-Diff/blob/86974a0f5bd16b1ee3e334ad828133c93dca80a1/scripts/3_game/cfggameplaydatajson.c)
- [Movement and heading initialization](https://github.com/BohemiaInteractive/DayZ-Script-Diff/blob/86974a0f5bd16b1ee3e334ad828133c93dca80a1/scripts/4_world/entities/manbase/dayzplayer/dayzplayercfgbase.c)

| Filter | Heavier multiplier relative to vanilla |
| --- | --- |
| Run/sprint transition | 4 |
| Jog direction | 2.5 |
| Sprint direction | 2 |
| Jog body heading | 2.5 |
| Sprint body heading | 2.5 |

These multiply filter spans; they are not guarantees of exact transition
duration. The run/sprint filter is documented as the Shift-hold filter,
not an ordinary idle-to-jog or W-release braking API.

PlayerBase normally overwrites three multipliers each command tick. This
mission temporarily disables that automatic update and applies the same
stamina formula itself in both modes. At normalized stamina S, vanilla
sprint turn/direction multipliers are 2-S and the run/sprint multiplier is
(2-S)*0.5. If stamina inertia was originally disabled, each is 1 instead.
The original flag and vanilla modifiers are restored on mission finish.
Modifiers are reapplied to the current movement command every update.

No speed override, forced translation, or direct initialization-only movement
settings writes are used. No asset import, animation replacement, or
multiplayer support is included. Current native engine ordering and actual
motion still require the user's first local launch and A/B comparison.
