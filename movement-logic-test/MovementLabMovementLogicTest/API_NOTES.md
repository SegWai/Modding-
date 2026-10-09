# Scope and implementation

This is a standalone single-player mission, with no packaged mod dependency.
The user confirmed v1 runs and feels heavier, but sprint release still stops
almost instantly. V2 retains those filters and adds an input-based braking
experiment. V2 has not been compiled or played in a DayZ engine here.

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

## V2 sprint braking

On a straight forward sprint release, a bounded 0.85-second linear ramp
requests movement input from 3 (sprint) through 2 (jog), 1 (walk), to 0 (idle).
These are input gait values, not physical velocity. Native movement blending
and collision remain in control. The ramp uses `OverrideMovementSpeed` and
`OverrideMovementAngle` with `HumanInputControllerOverrideType.ONE_FRAME`,
documented in human.c as clearing on the subsequent CommandHandler call.
Explicit DISABLED calls also release this mission's override on cancellation.
Input angle 0 requests forward relative to the current heading, not retained
world-space momentum. This first test should be performed looking ahead.

The release trigger reads UAMoveForward/Back/Left/Right directly from UAInput
LocalValue, separately from overridden movement. Sprint state is sampled
only while actual forward input is held. This prevents a self-sustaining
input-feedback loop. Non-forward input, new forward input, a non-standing
stance, raised hands, emotes, non-movement commands, menus, pause, death,
a frame over 0.25 seconds, mode switching and mission exit cancel braking.
Jogging release is unchanged. No idle-to-jog acceleration ramp is added.

No forced translation or initialization-only movement settings writes are
used. No asset import, animation replacement, or multiplayer support is
included. Fractional gait requests are accepted by the float API; their
visual blend, actual slowing and update ordering still require the user's
local DayZ test. This is not a custom stopping animation or a physics model.
