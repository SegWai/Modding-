# Scope and implementation

This is a standalone single-player mission, with no packaged mod dependency.
The user confirmed v1 runs and feels heavier, but sprint release still stops
almost instantly. V4 retains those filters and fixes the delayed, fixed-speed braking
experiment. V4 has not been compiled or played in a DayZ engine here.

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

## V4 sprint braking

V3 stayed near full sprint too long, and even a short Shift tap could trigger
full-sprint braking. Its trigger used a sprint state and hard-coded start 3;
its t^2 blend also had zero initial deceleration. V4 corrects both.

HumanCommandMove.GetCurrentMovementSpeed is documented as the current
0/1/2..3 idle/walk/run/sprint gait value, and official sprint-attack code
requires it >2.99 for achieved full sprint. It is not physical metres/second.
V4 samples this value only while raw forward input is held, with no active
braking override. It never substitutes 3 for a partial sprint.

Sprint exposure accumulates only while UATurbo is held and sampled gait >2.05,
capped at 0.45 seconds. Below that threshold, ordinary jogging is left alone.
On release, strength = clamp(gait-2,0,1) * clamp(exposure/0.45,0,1).
Full-stop input-ramp duration = 0.18 + 0.97*strength seconds (max 1.15).
Shift-only sprint-to-jog duration = 0.12 + 0.33*strength (max 0.45).
Both use blend = 2*t-t^2, so speed falls immediately then eases into the target.
Full sprint's requested gait crosses 2 after about 0.21s, versus 1.27s in v3;
these figures describe the requested envelope, not actual engine timing.

The run/sprint filter multiplier becomes 0.35 only while a braking ramp is
active, allowing the slowdown request to take effect promptly. Normal startup
and turning multipliers are retained and restored after cancellation/completion.
The native 0.45s base sprint filter would have a nominal 0.1575s span during
braking; engine behavior still needs gameplay validation.

Releasing W during the Shift ramp retargets continuously from the previous
requested gait, with duration max(0.18, originalStopDuration*current/start).
It does not reset to full sprint. The original stop budget reflects partial
sprint exposure rather than assigning every tap the same long tail.

Both ramps use OverrideMovementSpeed and OverrideMovementAngle with
HumanInputControllerOverrideType.ONE_FRAME. Explicit DISABLED calls also
clear owned overrides on cancellation. Angle 0 requests forward relative to
the current heading, not retained world-space momentum. Native animation
blending and collision remain in control; no SetPosition or SetVelocity is used.

Raw movement actions and UATurbo are read separately from overridden movement.
Active ramps do not re-arm themselves from generated gait. New direction
input, resumed forward input after full-stop release, resumed sprint during
Shift braking, non-standing stance, raised hands, emotes, non-movement
commands, menus, pause, death, a frame over 0.25s, F7 and mission exit cancel
braking. Physical stopping duration and native v4 compilation need a local test.
