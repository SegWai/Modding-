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

## v2 sprint-to-walk correction

For target walk after achieved sprint (>2.05), use the original zero-target
stop envelope, then clamp at gait 1. This fixes the generic partial-sprint
branch (<2.5), whose former target-1 interpolation differed from full stopping.
The >=2.5 staged sprint/jog/walk fractions remain unchanged. Directional
side/back walking finishes now apply equally to sprint returning to walk.
Ordinary Ctrl jog-to-walk and target-2 sprint-to-jog curves are unchanged.

New differential checks compare actual v2 walking return against original
v11 stopping each frame, including speed, angle and deadline: achieved gaits
2.1/2.3/2.49/2.5/2.9/3, exposure .05/.225/.45 seconds, six direction masks,
and 30/60/144 FPS. Original full-stop differential coverage includes those
partial sprint speeds too. Native physical velocity and clip synchronization
are not modeled; the game test is still required.

## v3 turning A/B

Default A is v2. F8 toggles m_MovementLabResponsiveTurn without canceling
start/brake ownership or altering saved mode. B changes only the heavy
non-sprint SetDirectionFilterModifier and SetTurnSpanModifier multipliers
from 2.5 to 1.6. Native SDK human.c defines these as direction timeout and
heading filter span multipliers. Sprint-specific setters, run/sprint filter,
stamina formula, gait curves, angles and timers are unchanged. F7 retains
the existing whole-profile vanilla comparison; responsive turn has no effect
in the vanilla profile. Camera/free-look controls are untouched.

World file and four mission startup/brake helpers are checked byte-for-byte
against v2. Actual filter and key-toggle methods are translated and executed
against mocks to compare all five filter outputs across heavy/braking/stamina
states and verify F8 does not cancel speed state. The inherited movement
checks also run. No native angular speed, turn arc or clip behavior is measured
in these checks; the in-game A/B establishes the feel.
