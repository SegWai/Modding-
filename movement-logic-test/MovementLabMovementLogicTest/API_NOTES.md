# Scope and implementation

This is a standalone single-player mission, with no packaged mod dependency.
The user confirmed v1 runs and feels heavier, but sprint release still stops
almost instantly. The user approved v5 forward and diagonal sprint braking. V6 adds a short
jogging stop. V6 has not been compiled or played in a DayZ engine here.

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
clear owned overrides on cancellation. V5 replaces the forward-only angle 0
with the captured current movement angle relative to the current heading. Native animation
blending and collision remain in control; no SetPosition or SetVelocity is used.

Raw movement actions and UATurbo are read separately from overridden movement.
Active ramps do not re-arm themselves from generated gait. New direction
input, resumed forward input after full-stop release, resumed sprint during
Shift braking, non-standing stance, raised hands, emotes, non-movement
commands, menus, pause, death, a frame over 0.25s, F7 and mission exit cancel
braking. Physical stopping duration and native v4 compilation need a local test.

## V5 diagonal input and direction

V4 unconditionally canceled on UAMoveLeft/Right and only remembered forward
input. V5 remembers a raw four-action key mask instead. Diagonal input is
eligible for exactly the same actual-gait/exposure braking formula. Only a
sampled gait above 2.05 arms braking; no lateral sprint speeds are invented.

HumanCommandMove.GetCurrentMovementAngle returns the native current local
movement angle (documented -180..180 degrees). It is sampled only with raw
movement input and no active override, alongside the current movement speed.
Starting a brake captures this angle and applies it through the existing
OverrideMovementAngle API. Retargeting Shift braking to a full stop preserves
that captured angle; it does not default to 0 or snap straight forward.
Angles remain relative to the current heading, not fixed world momentum.
Native angle-override behavior needs the user's first v5 gameplay check.

For Shift-only braking, retaining the original movement keys (including A/D)
does not cancel. A changed movement-key mask or resumed Shift gives control
back immediately. Releasing all movement keys retargets to a full stop.
During full-stop braking, any new movement input cancels. Sequential releases
that leave another movement key held continue to honor that input, rather
than forcing a stop while the player is still steering.

The v4 easing curve, duration/exposure constants, startup and turning filters,
and cancellation safeguards are retained. Source/package checks can confirm
this scope but cannot prove native compilation or diagonal playback.

## V6 jogging release

An additional branch, after the existing sprint branch, starts a short full
stop when raw movement input is released and the previously sampled achieved
gait is between 1.75 and 2.05 inclusive. It requires no UATurbo/Shift or sprint
exposure. Values below this band (ordinary walking) receive no new override.
The bands are disjoint: sprint requires >2.05, so a jogging branch cannot
replace or retrigger an active sprint ramp.

Jog duration = 0.42*min(sampledGait/2,1), or 0.3675-0.42 seconds within the
eligible band. This is shorter than a sustained full/near-full sprint tail.
The same immediate ease-out and captured-angle handling are reused, without
boosting the requested start gait. No step-count or foot-phase scheduling is
implemented: the intended small settling step must be assessed in-game.

V5's sprint duration/exposure formula, diagonal direction capture, startup,
turning and braking-only filter are retained. Jogging and diagonal jog stops
still need the user's native compilation/playback check.
