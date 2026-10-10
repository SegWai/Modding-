# Scope and implementation

This is a standalone single-player mission, with no packaged mod dependency.
The user confirmed v1 runs and feels heavier, but sprint release still stops
almost instantly. V3 retains those filters and lengthens the input-based braking
experiment. V3 has not been compiled or played in a DayZ engine here.

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

## V3 sprint braking

The user confirmed v2's startup looked good, but the full-sprint stop remained
too fast. V3 retains the startup and turning settings; only braking changes.

A standing forward sprint release requests a bounded 2.2-second input ramp
from 3 (sprint) to 0 (idle). Its quadratic blend keeps the requested gait above
2 for approximately 1.27 seconds, versus 0.28 seconds in v2's 0.85-second linear
ramp. These gait values are not metres/second, and engine filters can change
the actual movement timing.

Releasing UATurbo (Shift) while retaining UAMoveForward (W) now starts a separate
1.6-second smoothstep ramp from 3 to 2 (jog). It continues moving because W is
still held. Releasing W during that ramp retargets to idle continuously from
the last requested gait, over max(1, 2.2 * currentGait / 3) seconds. It never
jumps back to sprint when retargeting.

Both ramps use OverrideMovementSpeed and OverrideMovementAngle with
HumanInputControllerOverrideType.ONE_FRAME. Explicit DISABLED calls also
clear owned overrides on cancellation. Angle 0 requests forward relative to
the current heading, not retained world-space momentum. Native animation
blending and collision remain in control; no SetPosition or SetVelocity is used.

Raw UA movement inputs and UATurbo are read separately from overridden movement.
The native sprint state is sampled only while raw forward input is held and
no brake is active. Active ramps do not re-arm themselves from generated gait.
New direction input, resumed forward input after a full-stop release, resumed
sprint during the Shift ramp, non-standing stance, raised hands, emotes,
non-movement commands, menus, pause, death, a frame over 0.25 seconds, F7 and
mission exit cancel braking. Normal startup and ordinary jog-release remain
unchanged. V3's actual stopping timing and appearance need a local engine test.
