# Ctrl modes derived directly from stable v11

Source/ZIP v11 untouched. Existing mission braking and native filter methods
remain the timing authority. PlayerBase adds a persistent base mode (1 walk,
2 jog); UAWalkRunTemp rising edge toggles it. Native Shift UATurbo requests
3 only while held. Ctrl edges during Shift are ignored, so sprint release
returns to the same saved base mode. No double-tap or sprint latch is added.

Original 0.10/0.18/0.35 startup timings are retained. Existing walking also
uses the original walk/jog blend before sprint is handed to native heavy
filters. Persistent mode speed ownership changes Ctrl hold into Ctrl toggle.
On mode decreases, the pre-handler holds achieved speed until the mission
starts the timed brake; no early walking frame precedes the slowdown.
MovementLabSetBrakingActive cancels mode/start ownership, leaving the mission
as the sole speed/angle brake owner. Native base lifecycle remains untouched.

Original sprint/jog stop deadline formulas, phase fractions, lateral walking
finish and quick backward finish are retained. Walking retains its original
native stop behavior. Jog->walk uses original jog settle duration and target
1. Sprint->jog uses the original release duration/target2. Sprint->walk uses
the full v11 stop phase clock and clamps at walking; target1 completes into
walking, not idle. Releasing movement during a mode-return brake continues
from its current request with v11's existing proportional stop rule.

Existing direction and turbo cancellation logic is adapted to desired gait
so walk-return braking survives walking input while new sprint/jog input can
take control. Release of all direction keys is a stop; partial diagonal release
remains movement in the remaining direction.

Test harness executes mechanically translated actual World/mission methods
with mocks, including callback orders and FPS 30/60/144. Differential tests
execute original v11 and derivative stop methods and compare requested speed,
angle and deadline each tick for achieved jog/full sprint across directions.
These are not native compilation/graph/physics tests. Native clips are unchanged
and their visual blending still needs local DayZ validation.
